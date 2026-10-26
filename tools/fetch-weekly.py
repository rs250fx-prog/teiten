# -*- coding: utf-8 -*-
"""週次まとめの数値を一括で取り、`src/data/weekly/<YYYY-wNN>.json` に書く。

    python tools/fetch-weekly.py                 # 直近に終わった週（土曜の定期実行はこれ）
    python tools/fetch-weekly.py 2026-w43        # 週を指定
    python tools/fetch-weekly.py 2026-w43 --write  # JSON を書き出す（無しなら表示だけ）

## なぜ作ったか

週次の performance は9銘柄で、本文に「銀・プラチナもそろって下げた」「12月の利上げは約8割」と
書きながら数値を定点化していなかった（docs/SPEC.md 更新履歴 2026-10-27）。銘柄を倍に増やすと、
報道を寄せ集めて書く手作業では割れと捏造の危険も倍になる。**日次と同じく、取れる系列は機械で取る。**

## 何を出すか

1. 各資産の週末値と前週末比（26行）。performance にそのまま貼れる YAML の行も出す
2. レシオ3本（金/銀・金/原油・金/銅）と直近20週の推移
3. 週足のレンジ（金・銀・ドル円の高値・安値）
4. ポジションとフロー：CFTC の建玉（金・銀・原油・円、4週）、BTC現物ETFの週間フロー、
   FF金利先物から算出した次回・次々回のFOMCの織り込み
5. 週次相関：金の週次変化率と、実質金利・ドル指数・Nasdaq・BTC の週次変化の相関（直近8週）

サイトはこの JSON から 2〜5 を描く。**記事の frontmatter には手で写さない。**同じ数字を
2か所に書くと、片方だけ直した号が出る（thumb と同じ理由）。1 の performance は寸評が要るので
frontmatter に置き、`check-report.py` がこの JSON と値を突き合わせる。

## 定義の注意

- 金は USAGOLD の現物（日次と同じ系列）。**レシオと相関と週足のレンジは COMEX の期近先物で出す。**
  銀・銅の現物の確定値がクラウドから取れないため、比をとる両側を同じ種類の値にそろえる
- 円建て金は「金（USAGOLD）× ドル円（ニューヨーク17時）」の算出値。1トロイオンスあたりの円
- FRED の系列は1〜2営業日遅れる。土曜の朝には金曜分がまだ無いことが多く、そのときは
  `asof` に実際の日付が入る。**本文にはその日付を添える**
- 先物とドル指数の金曜の足は、土曜13時（JST）まで確定しない。それまでは「読み取り」になる
- FF金利先物の織り込みは CME FedWatch と同じ考え方の**算出値**で、FedWatch の値そのものではない。
  FedWatch のページはクラウドからも手元からも 403 で開けない（2026-10-27）

取れなかった項目は `status: "未確認"` で値を空にして書く。近い数字で埋めない。
"""
import csv
import importlib.util
import io
import json
import math
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "data" / "weekly"
JST = ZoneInfo("Asia/Tokyo")
MT = ZoneInfo("America/Denver")


def sibling(name: str):
    spec = importlib.util.spec_from_file_location(
        name.removesuffix(".py").replace("-", "_"), Path(__file__).with_name(name))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


market = sibling("fetch-market.py")
gold = sibling("fetch-gold.py")
extra = sibling("fetch-extra.py")

# FOMC の政策金利の発表日（2日目）。https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
# 2026-10-27 に 2027年分まで確認。**年が明けたら翌年分を足す**（足りなくなると織り込みが出ない）
FOMC = [
    "2026-10-28", "2026-12-09",
    "2027-01-27", "2027-03-17", "2027-04-28", "2027-06-09",
    "2027-07-28", "2027-09-15", "2027-10-27", "2027-12-08",
]
MONTH_CODE = "FGHJKMNQUVXZ"

# (key, 表示名, グループ, 取得元, 小数, 変化の単位)
# 表示名は既存の週次（W39〜W43）と同じにする。thumb と infographic が label の部分一致で引くため
ASSETS = [
    ("xau", "金（XAU/USD）", "metals", ("gold",), 2, "%"),
    ("xag", "銀（XAG/USD）", "metals", ("yahoo", "SI=F"), 3, "%"),
    ("xpt", "プラチナ（XPT/USD）", "metals", ("yahoo", "PL=F"), 2, "%"),
    ("xaujpy", "円建て金（XAU/JPY）", "metals", ("calc", "xaujpy"), 0, "%"),
    ("us2y", "米2年債利回り", "rates", ("ust", "nominal", "2 Yr"), 2, "bp"),
    ("us10y", "米10年債利回り", "rates", ("ust", "nominal", "10 Yr"), 2, "bp"),
    ("us2s10s", "米2-10年スプレッド", "rates", ("calc", "us2s10s"), 2, "bp"),
    ("real10", "実質金利（TIPS10年）", "rates", ("ust", "real", "10 YR"), 2, "bp"),
    ("bei10", "期待インフレ（10年BEI）", "rates", ("fred", "T10YIE"), 2, "bp"),
    ("jgb10", "日本10年債利回り", "rates", ("jgb",), 3, "bp"),
    ("dxy", "ドル指数 DXY", "fx", ("yahoo", "DX-Y.NYB"), 2, "%"),
    ("usdjpy", "USD/JPY", "fx", ("fx", "JPY=X"), 2, "%"),
    ("eurusd", "EUR/USD", "fx", ("fx", "EURUSD=X"), 4, "%"),
    ("wti", "WTI原油", "commodities", ("yahoo", "CL=F"), 2, "%"),
    ("brent", "Brent原油", "commodities", ("yahoo", "BZ=F"), 2, "%"),
    ("copper", "銅（COMEX）", "commodities", ("yahoo", "HG=F"), 4, "%"),
    ("spx", "S&P 500", "equities", ("yahoo", "^GSPC"), 2, "%"),
    ("ndx", "Nasdaq総合", "equities", ("yahoo", "^IXIC"), 2, "%"),
    ("dji", "ダウ平均", "equities", ("yahoo", "^DJI"), 2, "%"),
    ("n225", "日経225", "equities", ("yahoo", "^N225"), 2, "%"),
    ("btc", "BTC/USD", "crypto", ("btc",), 0, "%"),
    ("vix", "VIX", "vol", ("yahoo", "^VIX"), 2, "%"),
    ("nkvi", "日経VI", "vol", ("yahoo", "^NKVI.OS"), 2, "%"),
    ("move", "MOVE指数", "vol", ("yahoo", "^MOVE"), 2, "%"),
    ("hy", "米HYスプレッド", "credit", ("fred", "BAMLH0A0HYM2"), 2, "bp"),
]

SOURCE_NAME = {
    "gold": "USAGOLD 価格履歴（現物、山岳部時間15:00）",
    "fred": "FRED {}",
    "ust": "米財務省 Daily Treasury {} Yield Curve（{}）",
    "jgb": "財務省 国債金利情報",
    "yahoo": "Yahoo Finance {}（日足終値・清算値）",
    "fx": "Yahoo Finance {}（ニューヨーク17時）",
    "btc": "CoinGecko 日次（UTC 0:00）",
}

# CFTC の建玉。(表示名, データセット, 絞り込み, 買いの列, 売りの列, 区分)
COT = [
    ("金（COMEX）", "72hh-3qpy", "cftc_contract_market_code='088691'",
     "m_money_positions_long_all", "m_money_positions_short_all", "マネージド・マネー"),
    ("銀（COMEX）", "72hh-3qpy", "cftc_contract_market_code='084691'",
     "m_money_positions_long_all", "m_money_positions_short_all", "マネージド・マネー"),
    ("WTI原油（NYMEX）", "72hh-3qpy", "cftc_contract_market_code='067651'",
     "m_money_positions_long_all", "m_money_positions_short_all", "マネージド・マネー"),
    ("円（CME）", "gpe5-46if", "market_and_exchange_names like 'JAPANESE YEN - CHICAGO%'",
     "lev_money_positions_long", "lev_money_positions_short", "レバレッジド・ファンド"),
]


# ── 週の決め方 ───────────────────────────────────

def week_of(arg: str | None) -> tuple[date, date]:
    """(月曜, 金曜)。引数なしは new-weekly.py と同じ「直近に終わった週」"""
    if arg and "-w" in arg:
        y, w = arg.split("-w")
        monday = date.fromisocalendar(int(y), int(w), 1)
    else:
        if arg:
            base = date.fromisoformat(arg)
        else:
            today = datetime.now(JST).date()
            wd = today.weekday()
            base = today - timedelta(days=wd - 4 if wd >= 5 else wd + 3)
        monday = base - timedelta(days=base.weekday())
    return monday, monday + timedelta(days=4)


def on_or_before(rows, d: date, within: int = 6):
    """[(日付, 値)] から d 以前で最も新しい行。within 日より古ければ None"""
    best = None
    for rd, v in rows:
        if rd <= d and v is not None:
            if best is None or rd > best[0]:
                best = (rd, v)
    if best and (d - best[0]).days <= within:
        return best
    return None


# ── 取得 ───────────────────────────────────

def fred(series_id: str):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&_={int(datetime.now().timestamp())}"
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})   # UA は付けない（fetch-indicators.py）
    with urllib.request.urlopen(req, timeout=30) as r:
        rows = list(csv.reader(io.StringIO(r.read().decode("utf-8"))))
    out = []
    for row in rows[1:]:
        if len(row) >= 2 and row[1] not in (".", ""):
            out.append((date.fromisoformat(row[0]), float(row[1])))
    return out


def treasury(curve: str, column: str, years):
    """米財務省の日次の利回り曲線（nominal / real）。FRED より1営業日早く、記事の金利の原本"""
    kind = "daily_treasury_yield_curve" if curve == "nominal" else "daily_treasury_real_yield_curve"
    out = []
    for y in sorted(set(years)):
        url = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
               f"daily-treasury-rates.csv/{y}/all?type={kind}&field_tdr_date_value={y}&page&_format=csv")
        req = urllib.request.Request(url, headers={"User-Agent": market.UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            rows = list(csv.DictReader(io.StringIO(r.read().decode("utf-8-sig"))))
        for row in rows:
            v = row.get(column)
            if v:
                out.append((datetime.strptime(row["Date"], "%m/%d/%Y").date(), float(v)))
    return out


_cache: dict = {}

# 期近先物の連続足（CL=F など）は、限月が替わった週の前週比が限月をまたぐ。
# 第43週は WTI の11月限が10/20に満期を迎え、連続足の前週比は +1.83%、12月限どうしでは +4.3% だった。
# 金曜の値が連続足と一致する限月を探し、その限月の前週末値と比べる
FUT_ROOT = {"CL=F": ("CL", "NYM"), "BZ=F": ("BZ", "NYM"), "GC=F": ("GC", "CMX"),
            "SI=F": ("SI", "CMX"), "HG=F": ("HG", "CMX"), "PL=F": ("PL", "NYM")}


def same_contract(symbol: str, friday: date, value: float):
    """金曜の値が value と一致する限月の (記号, 確定した足)。見つからなければ None"""
    root, ex = FUT_ROOT[symbol]
    y, m = friday.year, friday.month
    for i in range(0, 5):
        mm, yy = (m - 1 + i) % 12 + 1, y + (m - 1 + i) // 12
        sym = f"{root}{MONTH_CODE[mm - 1]}{yy % 100:02d}.{ex}"
        try:
            rows, live, _ = yahoo(sym)
        except Exception:
            continue
        p = on_or_before(rows + ([live] if live else []), friday)
        if p and p[0] == friday and abs(p[1] - value) <= abs(value) * 1e-5:
            return sym, rows
    return None


def yahoo(symbol: str):
    """(確定した日足 [(日付, 値)], 読み取り (日付, 値) か None, 生の結果)"""
    if symbol not in _cache:
        res = market.chart(symbol, "/v8/finance/chart/{}?range=6mo&interval=1d")
        rows, live = market.closes(res, datetime.now(timezone.utc).timestamp())
        live_d = (live[0].date(), live[1]) if live else None
        _cache[symbol] = (rows, live_d, res)
    return _cache[symbol]


def fx(symbol: str):
    key = symbol + "@1h"
    if key not in _cache:
        res = market.chart(symbol, "/v8/finance/chart/{}?range=1mo&interval=1h")
        rows, live = market.fx_closes(res, datetime.now(timezone.utc).timestamp())
        live_d = (live[0].date(), live[1]) if live else None
        _cache[key] = (rows, live_d, res)
    return _cache[key]


def usagold(monday: date, friday: date):
    prev = monday - timedelta(days=7)
    months = {(prev.year, prev.month), (friday.year, friday.month)}
    rows = {}
    for y, m in sorted(months):
        rows.update(gold.calendar(y, m))
    return sorted((d, v) for d, (v, _c) in rows.items())


def point(kind, arg, monday, friday):
    """(今週末 (日付, 値), 前週末 (日付, 値), status)。取れなければ例外"""
    prev_fri = friday - timedelta(days=7)
    status = "確定"
    note = ""
    if kind == "ust":
        rows = treasury(arg[0], arg[1], [prev_fri.year, friday.year])
        cur, prv = on_or_before(rows, friday), on_or_before(rows, prev_fri)
    elif kind == "gold":
        rows = usagold(monday, friday)
        cur, prv = on_or_before(rows, friday), on_or_before(rows, prev_fri)
        # 山岳部時間でまだ金曜のうちは、金曜のセルが動いている（fetch-gold.py）
        if cur and cur[0] >= datetime.now(MT).date():
            status = "読み取り"
    elif kind == "fred":
        rows = fred(arg)
        cur, prv = on_or_before(rows, friday), on_or_before(rows, prev_fri)
    elif kind == "jgb":
        rows = extra.jgb10() + extra.jgb10(all_years=True)
        cur, prv = on_or_before(rows, friday), on_or_before(rows, prev_fri)
    elif kind == "btc":
        rows = extra.btc_daily(120)
        # 金曜 UTC 0:00（JST 9:00）を週の基準にする（docs/SOURCES.md の BTC と同じ時点）
        cur, prv = on_or_before(rows, friday, 0), on_or_before(rows, prev_fri, 0)
    elif kind in ("yahoo", "fx"):
        rows, live, _ = (yahoo if kind == "yahoo" else fx)(arg)
        cur, prv = on_or_before(rows, friday), on_or_before(rows, prev_fri)
        # 金曜の足がまだ確定していなければ、読み取りで出す（終値とは書かない）
        if (cur is None or cur[0] < friday) and live and monday <= live[0] <= friday:
            cur, status = live, "読み取り"
        if kind == "yahoo" and arg in FUT_ROOT and cur and prv:
            hit = same_contract(arg, cur[0], cur[1])
            if hit:
                sym, crow = hit
                p2 = on_or_before(crow, prev_fri)
                if p2 and abs(p2[1] - prv[1]) > abs(prv[1]) * 1e-5:
                    prv, note = p2, f"限月交代の週。前週比は同じ限月（{sym}）どうしで出した"
            else:
                note = "限月を特定できない。前週比が限月をまたいでいる可能性がある"
    else:
        raise ValueError(kind)
    if cur is None or prv is None:
        raise RuntimeError("週末の値か前週末の値がありません")
    return cur, prv, status, note


def build_assets(monday, friday):
    out = {}
    for key, label, group, src, digits, unit in ASSETS:
        kind = src[0]
        row = {"key": key, "label": label, "group": group, "digits": digits, "unit": unit}
        try:
            if kind == "calc":
                continue
            arg = src[1:] if kind == "ust" else (src[1] if len(src) > 1 else None)
            cur, prv, status, note = point(kind, arg, monday, friday)
            row.update(close=cur[1], asof=cur[0].isoformat(), prev=prv[1], prev_asof=prv[0].isoformat(),
                       status=status, source=SOURCE_NAME[kind].format(*src[1:]))
            if note:
                row["note"] = note
        except Exception as e:
            row.update(close=None, prev=None, status="未確認", source="", error=str(e))
        out[key] = row

    def calc(key, f, src_keys, source):
        label, group, digits, unit = next((a[1], a[2], a[4], a[5]) for a in ASSETS if a[0] == key)
        parts = [out[k] for k in src_keys]
        row = {"key": key, "label": label, "group": group, "digits": digits, "unit": unit, "source": source}
        if any(p["close"] is None for p in parts):
            row.update(close=None, prev=None, status="未確認")
        else:
            st = "読み取り" if any(p["status"] == "読み取り" for p in parts) else "確定"
            row.update(close=f(*[p["close"] for p in parts]), prev=f(*[p["prev"] for p in parts]),
                       asof=min(p["asof"] for p in parts), status=st)
        out[key] = row

    calc("xaujpy", lambda g, j: g * j, ["xau", "usdjpy"], "算出：金（USAGOLD）× ドル円（ニューヨーク17時）")
    calc("us2s10s", lambda a, b: (b - a), ["us2y", "us10y"], "算出：米10年債 − 米2年債（米財務省）")
    # 表の並びは ASSETS の順
    return [out[a[0]] for a in ASSETS]


def change_text(row) -> tuple[str, str, str]:
    """(value, change, dir) を記事の書式で返す"""
    if row["close"] is None:
        return "", "", "flat"
    c, p, d = row["close"], row["prev"], row["digits"]
    if row["key"] == "us2s10s":
        value = f"{c * 100:+.0f}bp".replace("-", "−")
    elif row["unit"] == "bp":
        value = f"{c:.{d}f}%"
    else:
        value = f"{c:,.{d}f}"
    if row["unit"] == "bp":
        x = round((c - p) * 100, 1)
        ch = f"{abs(x):.0f}bp" if abs(x) >= 0.5 else "0bp"
    else:
        x = (c / p - 1) * 100
        ch = f"{abs(x):.2f}%"
    sign = "+" if x > 0 else "−" if x < 0 else "±"
    if ch in ("0bp", "0.00%"):
        sign, x = "±", 0
    return value, sign + ch, "up" if x > 0 else "down" if x < 0 else "flat"


# ── レシオと週足 ─────────────────────────────────

def weekly_last(rows, fridays):
    """各金曜（その週の最後の取引日）の値。{金曜: 値}"""
    out = {}
    for f in fridays:
        p = on_or_before(rows, f, 4)
        if p and p[0] > f - timedelta(days=5):
            out[f] = p[1]
    return out


def ratios(friday):
    fridays = [friday - timedelta(days=7 * i) for i in range(19, -1, -1)]
    series = {s: weekly_last(yahoo(s)[0] + ([yahoo(s)[1]] if yahoo(s)[1] else []), fridays)
              for s in ("GC=F", "SI=F", "CL=F", "HG=F")}
    defs = [
        ("gold_silver", "金/銀", "SI=F", 2, "金が銀の何倍か。上がる週は不安の買い、下がる週は商品全体の買い"),
        ("gold_oil", "金/原油", "CL=F", 2, "金1オンスで買える原油の量（バレル）。上がる週は景気の不安、下がる週はインフレ・供給の材料"),
        ("gold_copper", "金/銅", "HG=F", 0, "金と景気の代理（銅）の比。上がる週は景気への不安、下がる週は景気への期待"),
    ]
    out = []
    for key, label, sym, digits, gloss in defs:
        hist = []
        for f in fridays:
            g, o = series["GC=F"].get(f), series[sym].get(f)
            if g and o:
                hist.append({"week_end": f.isoformat(), "value": round(g / o, 4)})
        cur = hist[-1] if hist and hist[-1]["week_end"] == friday.isoformat() else None
        prev = next((h for h in reversed(hist) if h["week_end"] == (friday - timedelta(days=7)).isoformat()), None)
        out.append({"key": key, "label": label, "digits": digits, "gloss": gloss,
                    "value": cur and cur["value"], "prev": prev and prev["value"],
                    "history": hist,
                    "source": f"算出：COMEX 金先物（GC=F）÷ {sym}（Yahoo Finance、各週の最後の取引日）"})
    return out


def week_range(monday, friday):
    """金（先物）・銀（先物）・ドル円の週の高値・安値"""
    out = []
    for sym, label, digits, is_fx in (("GC=F", "金（COMEX 先物）", 1, False),
                                     ("SI=F", "銀（COMEX 先物）", 3, False),
                                     ("JPY=X", "USD/JPY", 2, True)):
        try:
            res = (fx(sym) if is_fx else yahoo(sym))[2]
            q = res["indicators"]["quote"][0]
            tz = ZoneInfo("America/New_York")
            hi = lo = op = cl = None
            for t, h, l, o, c in zip(res["timestamp"], q["high"], q["low"], q["open"], q["close"]):
                if None in (h, l):
                    continue
                dt = datetime.fromtimestamp(t, tz)
                # 為替はニューヨーク17時で日を区切る。週は日曜17時〜金曜17時
                d = (dt + timedelta(hours=7)).date() if is_fx else dt.date()
                if not (monday <= d <= friday):
                    continue
                hi = h if hi is None else max(hi, h)
                lo = l if lo is None else min(lo, l)
                if op is None:
                    op = o
                cl = c
            if hi is None:
                raise RuntimeError("足がありません")
            out.append({"label": label, "high": round(hi, digits), "low": round(lo, digits),
                        "open": round(op, digits), "close": round(cl, digits), "digits": digits,
                        "source": f"Yahoo Finance {sym}（{'1時間足' if is_fx else '日足'}）"})
        except Exception as e:
            out.append({"label": label, "status": "未確認", "error": str(e)})
    return out


# ── ポジションとフロー ───────────────────────────────

def cot(friday):
    out = []
    for label, ds, where, lcol, scol, who in COT:
        try:
            q = urllib.parse.urlencode({
                "$select": f"report_date_as_yyyy_mm_dd,{lcol},{scol}",
                "$where": f"{where} AND report_date_as_yyyy_mm_dd <= '{friday.isoformat()}T00:00:00'",
                "$order": "report_date_as_yyyy_mm_dd DESC", "$limit": "5",
            })
            with urllib.request.urlopen(f"https://publicreporting.cftc.gov/resource/{ds}.json?{q}", timeout=30) as r:
                rows = json.loads(r.read().decode("utf-8"))
            if not rows:
                raise RuntimeError("行がありません")
            hist = [{"date": x["report_date_as_yyyy_mm_dd"][:10],
                     "net": int(float(x[lcol])) - int(float(x[scol]))} for x in rows][:4]
            hist.reverse()
            out.append({"label": label, "who": who, "history": hist, "status": "確定",
                        "source": "CFTC Commitments of Traders（火曜時点、金曜公表）"})
        except Exception as e:
            out.append({"label": label, "who": who, "history": [], "status": "未確認", "error": str(e)})
    return out


def btc_etf(monday, friday):
    try:
        rows = [(d, v) for d, v in extra.btc_etf_flows() if monday <= d <= friday]
        got = [v for _d, v in rows if v is not None]
        days = [{"date": d.isoformat(), "flow": v} for d, v in rows]
        if not got:
            return {"status": "未確認", "days": days}
        status = "確定" if len(got) == len(rows) and len(rows) >= 5 else "読み取り"
        return {"status": status, "total": round(sum(got), 1), "days": days,
                "note": "" if status == "確定" else f"{len(rows)}日中{len(got)}日分の合計",
                "source": "Farside Investors（米国の現物ETF合計、百万ドル）"}
    except Exception as e:
        return {"status": "未確認", "error": str(e), "days": []}


def ff_contract(y: int, m: int) -> str:
    return f"ZQ{MONTH_CODE[m - 1]}{y % 100:02d}.CBT"


def ff_implied(y, m, friday):
    rows, live, _ = yahoo(ff_contract(y, m))
    p = on_or_before(rows + ([live] if live else []), friday)
    if not p:
        raise RuntimeError(f"{ff_contract(y, m)} の値がありません")
    return 100 - p[1]


def fedwatch(friday):
    """次回・次々回の FOMC の織り込み。CME FedWatch と同じ考え方の算出値"""
    try:
        effr = on_or_before(fred("EFFR"), friday)
        if not effr:
            raise RuntimeError("EFFR がありません")
        pre = effr[1]
        out = []
        for ds in [d for d in FOMC if date.fromisoformat(d) > friday][:2]:
            d = date.fromisoformat(ds)
            n = (date(d.year + (d.month == 12), d.month % 12 + 1, 1) - timedelta(days=1)).day
            before = d.day          # 発表日までは旧い金利（翌日から新しい金利）
            if n - before < 8:
                # 月末近くの会合は、その月の先物では会合後の日数が少なく、ぶれが大きい。翌月の先物を会合後の金利とみる
                ny, nm = (d.year + 1, 1) if d.month == 12 else (d.year, d.month + 1)
                post = ff_implied(ny, nm, friday)
                contract = ff_contract(ny, nm)
            else:
                avg = ff_implied(d.year, d.month, friday)
                post = (avg - pre * before / n) / ((n - before) / n)
                contract = ff_contract(d.year, d.month)
            move = (post - pre) * 100
            out.append({"meeting": ds, "contract": contract, "pre": round(pre, 3), "post": round(post, 3),
                        "move_bp": round(move, 1), "hikes": round(move / 25, 2)})
            pre = post
        return {"status": "確定", "effr": effr[1], "effr_asof": effr[0].isoformat(), "meetings": out,
                "source": "算出：CBOT FF金利先物（Yahoo Finance）と FRED EFFR。CME FedWatch の値そのものではない"}
    except Exception as e:
        return {"status": "未確認", "error": str(e), "meetings": []}


# ── 相関 ───────────────────────────────────

def pearson(xs, ys):
    n = len(xs)
    if n < 4:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def correlation(friday, window=8):
    fridays = [friday - timedelta(days=7 * i) for i in range(window, -1, -1)]

    def changes(rows, mode, within=4):
        vals = []
        for f in fridays:
            p = on_or_before(rows, f, within)
            vals.append(p[1] if p else None)
        out = []
        for a, b in zip(vals, vals[1:]):
            if a is None or b is None:
                out.append(None)
            else:
                out.append((b / a - 1) * 100 if mode == "%" else (b - a) * 100)
        return out

    def yrows(sym):
        rows, live, _ = yahoo(sym)
        return rows + ([live] if live else [])

    try:
        g = changes(yrows("GC=F"), "%")
        others = [
            ("実質金利（TIPS10年）", changes(fred("DFII10"), "bp"), "週間の変化（bp）"),
            ("ドル指数 DXY", changes(yrows("DX-Y.NYB"), "%"), "週間の変化率"),
            ("Nasdaq総合", changes(yrows("^IXIC"), "%"), "週間の変化率"),
            ("BTC/USD", changes(extra.btc_daily(120), "%", 0), "週間の変化率（金曜 UTC 0:00）"),
        ]
        out = []
        for label, xs, unit in others:
            pairs = [(a, b) for a, b in zip(g, xs) if a is not None and b is not None]
            r = pearson([a for a, _ in pairs], [b for _, b in pairs])
            out.append({"label": label, "r": None if r is None else round(r, 2), "n": len(pairs), "unit": unit})
        return {"status": "確定", "window": window, "pairs": out,
                "base": "金（COMEX 先物 GC=F）の週間変化率",
                "source": "算出：Yahoo Finance・FRED DFII10・CoinGecko。各週の最後の取引日どうしの変化"}
    except Exception as e:
        return {"status": "未確認", "error": str(e), "pairs": []}


# ── 出力 ───────────────────────────────────

def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv
    monday, friday = week_of(args[0] if args else None)
    year, week, _ = monday.isocalendar()
    slug = f"{year}-w{week:02d}"
    print(f"{year}年 第{week}週（{monday} 〜 {friday}）を取得します\n")

    assets = build_assets(monday, friday)
    data = {
        "slug": slug, "start": monday.isoformat(), "end": friday.isoformat(),
        "fetched": datetime.now(JST).strftime("%Y-%m-%d %H:%M JST"),
        "assets": assets,
        "ratios": ratios(friday),
        "ranges": week_range(monday, friday),
        "cot": cot(friday),
        "btc_etf": btc_etf(monday, friday),
        "fedwatch": fedwatch(friday),
        "correlation": correlation(friday),
    }

    print("## performance に貼る行（note を書き足す。value・change・dir は書き換えない）\n")
    print("performance:")
    group = None
    for a in assets:
        if a["group"] != group:
            group = a["group"]
            print(f"  # {group}")
        value, change, dirv = change_text(a)
        st = a["status"]
        extra_f = f', status: {st}' if st != "確定" else ""
        print(f'  - {{ key: {a["key"]}, group: {a["group"]}, label: "{a["label"]}", value: "{value}", '
              f'change: "{change}", dir: {dirv}{extra_f}, note: "" }}')
    print()
    for a in assets:
        if a["status"] == "未確認":
            print(f"NG  {a['label']}：取れませんでした（{a.get('error', '')}）。value を空にして status: 未確認 のまま残す")
        elif a.get("asof") and a["asof"] != friday.isoformat() and a["key"] != "btc":
            print(f"△  {a['label']}：{a['asof']} 時点の値です（{a['source']}）。本文には日付を添える")
        elif a["status"] == "読み取り":
            print(f"△  {a['label']}：読み取り（金曜の値がまだ確定していない）。終値とは書かない")
        if a.get("note"):
            print(f"△  {a['label']}：{a['note']}")

    print("\n## レシオ")
    for r in data["ratios"]:
        if r["value"]:
            ch = f"（前週 {r['prev']:.{r['digits']}f}）" if r["prev"] else ""
            print(f"  {r['label']}：{r['value']:.{r['digits']}f}{ch}  … {r['gloss']}")
        else:
            print(f"NG  {r['label']}：算出できません")
    print("\n## 週足のレンジ")
    for r in data["ranges"]:
        if "high" in r:
            print(f"  {r['label']}：高値 {r['high']:,.{r['digits']}f} / 安値 {r['low']:,.{r['digits']}f}（始値 {r['open']:,.{r['digits']}f} → {r['close']:,.{r['digits']}f}）")
        else:
            print(f"NG  {r['label']}：{r.get('error')}")
    print("\n## CFTC 建玉（ネット）")
    for c in data["cot"]:
        if c["history"]:
            print(f"  {c['label']}（{c['who']}）：" + " → ".join(f"{h['date'][5:]} {h['net']:+,}" for h in c["history"]))
        else:
            print(f"NG  {c['label']}：{c.get('error')}")
    b = data["btc_etf"]
    print("\n## BTC現物ETF（週間）")
    print(f"  {b['total']:+,.1f}百万ドル（{b['status']}{'、' + b['note'] if b.get('note') else ''}）" if "total" in b
          else f"NG  未確認（{b.get('error', '集計された日がありません')}）")
    f = data["fedwatch"]
    print("\n## FOMC の織り込み（FF金利先物からの算出）")
    if f["meetings"]:
        print(f"  EFFR {f['effr']:.2f}%（{f['effr_asof']}）")
        for m in f["meetings"]:
            print(f"  {m['meeting']}：会合後 {m['post']:.3f}%（{m['move_bp']:+.1f}bp ＝ 0.25%の利上げ {m['hikes']:+.2f}回分、{m['contract']}）")
    else:
        print(f"NG  未確認（{f.get('error')}）")
    c = data["correlation"]
    print(f"\n## 週次相関（直近{c.get('window', 8)}週、{c.get('base', '')}）")
    for p in c["pairs"]:
        r = "—" if p["r"] is None else f"{p['r']:+.2f}"
        print(f"  {p['label']}：{r}（{p['n']}週）")

    if write:
        OUT.mkdir(parents=True, exist_ok=True)
        path = OUT / f"{slug}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"\n書き出し: {path.relative_to(ROOT)}")
    else:
        print("\n（表示のみ。--write で src/data/weekly/ に書き出す）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
