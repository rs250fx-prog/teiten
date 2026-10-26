# -*- coding: utf-8 -*-
"""日本10年債（財務省）・BTC（CoinGecko）・BTC現物ETFの資金フロー（Farside）を取り、
記事に書ける形で出す。

    python tools/fetch-extra.py

`fetch-indicators.py` と `fetch-weekly.py` からも呼ばれる。

## なぜ作ったか

この3つは取得元を docs/SOURCES.md で決めたあとも、毎朝手で curl して読んでいた
（HANDOVER §4-5）。BTC 現物ETFのフローは Farside を Web取得ツールで読ませていたが、
要約を通ると数値が作られるため（HANDOVER §3）、ほぼ毎号「未確認」だった。
3つとも鍵が要らず、生の表をスクリプトで読める（2026-10-27 に確認）。

## 定義

- 日本10年債：財務省「国債金利情報」の当月分CSV（jgbcm.csv）。基準日は和暦（R8.10.23）
- BTC：CoinGecko の日次。**UTC 0:00（JST 9:00）の行をその日の基準値にする。**
  末尾の1行は取得時点の値で、基準値ではないので捨てる
- BTC現物ETF：Farside の日次ネットフロー（百万ドル）。括弧は流出。「-」はまだ集計前

## 取れなかったら

「未確認」と書く。**要約された文章から数字を読まない。**
"""
import csv
import io
import json
import re
import sys
import urllib.request
from datetime import date, datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
JGB = "https://www.mof.go.jp/jgbs/reference/interest_rate/jgbcm.csv"
JGB_ALL = "https://www.mof.go.jp/jgbs/reference/interest_rate/data/jgbcm_all.csv"
BTC = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={}&interval=daily"
FARSIDE = "https://farside.co.uk/btc/"


def get(url: str, ua: bool = True) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA} if ua else {})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def signed(x: float, digits: int) -> str:
    """記事の書式（全角のマイナス「−」）で符号つきにする"""
    s = f"{abs(x):,.{digits}f}"
    return ("+" if x > 0 else "−" if x < 0 else "±") + s


def wareki(s: str):
    """'R8.10.23' → date(2026, 10, 23)。令和以外は None"""
    m = re.match(r"R(\d+)\.(\d+)\.(\d+)$", s.strip())
    if not m:
        return None
    return date(2018 + int(m.group(1)), int(m.group(2)), int(m.group(3)))


def jgb10(all_years: bool = False):
    """[(日付, 10年利回り%)] 古い順。all_years=True なら過去分を含む全期間のCSV"""
    text = get(JGB_ALL if all_years else JGB).decode("shift_jis", "ignore")
    rows = list(csv.reader(io.StringIO(text)))
    col = None
    out = []
    for row in rows:
        if col is None:
            if "10年" in row:
                col = row.index("10年")
            continue
        if not row:
            continue
        d = wareki(row[0])
        if d is None or len(row) <= col or row[col] in ("", "-"):
            continue
        out.append((d, float(row[col])))
    return out


def btc_daily(days: int = 10):
    """[(UTCの日付, 値)] 古い順。UTC 0:00 ちょうどの行だけを採る"""
    payload = json.loads(get(BTC.format(days), ua=False).decode("utf-8"))
    out = []
    for ms, v in payload.get("prices", []):
        t = datetime.fromtimestamp(ms / 1000, timezone.utc)
        if (t.hour, t.minute, t.second) == (0, 0, 0):
            out.append((t.date(), float(v)))
    return out


def btc_etf_flows():
    """[(日付, 合計の百万ドル か None)] 古い順。None はまだ集計されていない日"""
    html = get(FARSIDE).decode("utf-8", "ignore")
    out = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        cells = [re.sub(r"<[^>]+>|&nbsp;", "", c).strip()
                 for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
        if len(cells) < 3:
            continue
        try:
            d = datetime.strptime(cells[0], "%d %b %Y").date()
        except ValueError:
            continue
        total = cells[-1].replace(",", "")
        # 集計前の日は、合計が 0.0 と出ていても個別の列がすべて「-」になっている
        if total in ("-", "") or all(c == "-" for c in cells[1:-1]):
            out.append((d, None))
            continue
        neg = total.startswith("(")
        try:
            v = float(total.strip("()"))
        except ValueError:
            continue
        out.append((d, -v if neg else v))
    return out


def report() -> int:
    failed = []
    try:
        rows = jgb10()
        d, v = rows[-1]
        chg = ""
        if len(rows) >= 2:
            pd_, pv = rows[-2]
            chg = f"、{pd_.month}/{pd_.day}比 {signed((v - pv) * 100, 1)}bp"
        print(f"  日本10年債利回り：{v:.3f}%（{d.month}/{d.day}時点{chg}、財務省 国債金利情報）")
    except Exception as e:
        print(f"NG  日本10年債（財務省）取得できません: {e}")
        print(f"    {JGB} を開き、基準日の入った最後の行の「10年」列を読む（Shift_JIS）")
        failed.append("日本10年債")

    try:
        rows = btc_daily(5)
        d, v = rows[-1]
        chg = ""
        if len(rows) >= 2:
            pv = rows[-2][1]
            chg = f"、24時間前比 {signed((v / pv - 1) * 100, 2)}%"
        print(f"  BTC/USD：{v:,.0f}ドル（{d.month}/{d.day} 09:00 JST時点{chg}、CoinGecko 日次 UTC 0:00）")
    except Exception as e:
        print(f"NG  BTC（CoinGecko）取得できません: {e}")
        failed.append("BTC")

    try:
        flows = btc_etf_flows()
        shown = 0
        for d, v in reversed(flows):
            if v is None:
                continue
            print(f"  BTC現物ETFの資金フロー：{signed(v, 1)}百万ドル（{d.month}/{d.day}、米国の現物ETF合計、Farside）")
            shown += 1
            if shown >= 2:
                break
        if not shown:
            print("△ BTC現物ETFの資金フロー：集計済みの日がありません")
    except Exception as e:
        print(f"NG  BTC現物ETFの資金フロー（Farside）取得できません: {e}")
        print(f"    {FARSIDE} の表を生のまま読む。要約からは読まない。取れなければ「未確認」")
        failed.append("BTC現物ETFフロー")

    if failed:
        print("\n取れなかったものは「未確認」と書く。**要約された文章から数字を読まない。**")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(report())
