# -*- coding: utf-8 -*-
"""
週次まとめの雛形を作る。

    python tools/new-weekly.py            # 直近に終わった週
    python tools/new-weekly.py 2026-09-14 # その日を含む週

週番号・対象期間（月〜金）・来週のスケジュール枠は日付から自動で出す。
手で書くと週番号と期間がずれる。

既存ファイルがある場合は上書きせずに終了する。
"""
import sys
import datetime
import zoneinfo
from pathlib import Path

WEEKLY = Path("src/content/weekly")
REPORTS = Path("src/content/reports")
DATA = Path("src/data/weekly")
JST = zoneinfo.ZoneInfo("Asia/Tokyo")
WD = "月火水木金土日"

# Windows の既定コンソールは cp932 で、一部の記号を出力できず落ちる。
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


TEMPLATE = '''---
year: {year}
week: {week}
title: ""
deck: ""
start: "{start}"
end: "{end}"
date: "{pub}"
updated: "{updated}"

# 今週の要点。3〜5件
points:
  - ""
  - ""
  - ""

# 各資産の週次パフォーマンス。値だけでなく寸評（note）を付ける
# value / change / dir / status は tools/fetch-weekly.py の取得値。**書き換えない**（check-report.py が突き合わせる）。
# 書くのは note だけ。status: 未確認 の行は値を空のまま残し、取れた出所があれば本文に書く
performance:
{performance}
# 週のレシオ（金/銀・金/原油・金/銅）への一言。数値は JSON から出るので書かない。
# 例：「金/銀が2週続けて上昇。銀のほうが売られ、不安の買いではなく換金売りの色が濃い」
ratioNotes:
  gold_silver: ""
  gold_oil: ""
  gold_copper: ""

# ポジションとフローのうち、スクリプトで取れないもの。公式ページか複数の報道で確かめた値だけ。
# 確かめられなければ status: 未確認 のまま（値は空）。建玉・BTC現物ETF・FOMC の織り込みは JSON から出る
flows:
  - {{ label: "金ETF（GLD）の保有量", value: "", change: "", dir: flat, status: 未確認, source: "", note: "" }}
  - {{ label: "銀ETF（SLV）の保有量", value: "", change: "", dir: flat, status: 未確認, source: "", note: "" }}

# 来週の主要スケジュール。key: true は★付きで強調される
schedule:
{schedule}
# テクニカル・レベル（週末時点）。上から下へ価格順
# kind は resistance / current / support
levels:
  - {{ kind: resistance, value: "", note: "" }}
  - {{ kind: resistance, value: "", note: "" }}
  - {{ kind: current,    value: "", note: "" }}
  - {{ kind: support,    value: "", note: "" }}
  - {{ kind: support,    value: "", note: "" }}

# 銀・ドル円のテクニカル・レベル（levels は金）。週足のレンジは JSON から出るので、それを根拠に引いてよい
moreLevels:
  - asset: "銀（XAG/USD）"
    levels:
      - {{ kind: resistance, value: "", note: "" }}
      - {{ kind: current,    value: "", note: "" }}
      - {{ kind: support,    value: "", note: "" }}
  - asset: "ドル円（USD/JPY）"
    levels:
      - {{ kind: resistance, value: "", note: "" }}
      - {{ kind: current,    value: "", note: "" }}
      - {{ kind: support,    value: "", note: "" }}

# 来週のシナリオ。発動条件・因果連鎖・価格目処を同じ粒度で書く
scenarios:
  - {{ kind: bull, trigger: "", chain: "", target: "" }}
  - {{ kind: base, trigger: "", chain: "", target: "" }}
  - {{ kind: bear, trigger: "", chain: "", target: "" }}

# 来週のスタンス。記事の結論として独立したブロックに出る
bias: ""

# note 用サムネイルの文言。数値は書かない（performance から取る）。
# title は全角15字相当、sub は24字相当、bias は28字まで（半角の英数字は約半分）。
# notes は各枠の変化率の後ろに添える寸評。8字まで
thumb:
  title: ""
  sub: ""
  bias: ""
  notes: {{ xau: "", nikkei: "", wti: "", dxy: "", us10y: "" }}

tags: []
# 80〜100字。未記入だと deck が流用され、一覧で重複する
description: ""
draft: true
---

## 週の核心テーマ

---

## 今週の主要イベント振り返り

### ①

### ②

### ③

---

## 今週の資金フロー構造

**  →   →  **

第一の流れは。

第二の流れは。

第三に。

情報元：

- []()

---

## 来週の備え（{nw_start_disp}〜{nw_end_disp}）

### 最重要イベント

### 国内政治・政策の波乱要因

### 地政学シナリオ

### 日経・円の焦点

予想レンジ：上限　　円 〜 下限　　円

### 金・銀・ドル円の焦点

金の予想レンジ：上限　　ドル 〜 下限　　ドル
銀の予想レンジ：上限　　ドル 〜 下限　　ドル
ドル円の予想レンジ：上限　　円 〜 下限　　円
'''

# 雛形に並べる performance の行（fetch-weekly.py の JSON が無いとき）。値は空
FALLBACK_KEYS = [
    ("xau", "metals", "金（XAU/USD）"), ("xag", "metals", "銀（XAG/USD）"),
    ("xpt", "metals", "プラチナ（XPT/USD）"), ("xaujpy", "metals", "円建て金（XAU/JPY）"),
    ("us2y", "rates", "米2年債利回り"), ("us10y", "rates", "米10年債利回り"),
    ("us2s10s", "rates", "米2-10年スプレッド"), ("real10", "rates", "実質金利（TIPS10年）"),
    ("bei10", "rates", "期待インフレ（10年BEI）"), ("jgb10", "rates", "日本10年債利回り"),
    ("dxy", "fx", "ドル指数 DXY"), ("usdjpy", "fx", "USD/JPY"), ("eurusd", "fx", "EUR/USD"),
    ("wti", "commodities", "WTI原油"), ("brent", "commodities", "Brent原油"), ("copper", "commodities", "銅（COMEX）"),
    ("spx", "equities", "S&P 500"), ("ndx", "equities", "Nasdaq総合"), ("dji", "equities", "ダウ平均"),
    ("n225", "equities", "日経225"), ("btc", "crypto", "BTC/USD"),
    ("vix", "vol", "VIX"), ("nkvi", "vol", "日経VI"), ("move", "vol", "MOVE指数"), ("hy", "credit", "米HYスプレッド"),
]


def performance_lines(slug):
    """src/data/weekly/<slug>.json があれば取得値を入れた行、無ければ値の空いた行"""
    import json
    import importlib.util
    path = DATA / f"{slug}.json"
    lines = []
    if path.exists():
        spec = importlib.util.spec_from_file_location("fetch_weekly", Path(__file__).with_name("fetch-weekly.py"))
        fw = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fw)
        group = None
        for a in json.loads(path.read_text(encoding="utf-8"))["assets"]:
            if a["group"] != group:
                group = a["group"]
                lines.append(f"  # {group}")
            value, change, dirv = fw.change_text(a)
            st = "" if a["status"] == "確定" else f", status: {a['status']}"
            lines.append(f'  - {{ key: {a["key"]}, group: {a["group"]}, label: "{a["label"]}", value: "{value}", '
                         f'change: "{change}", dir: {dirv}{st}, note: "" }}')
        return "\n".join(lines) + "\n", True
    for key, group, label in FALLBACK_KEYS:
        lines.append(f'  - {{ key: {key}, group: {group}, label: "{label}", value: "", change: "", dir: flat, '
                     f'status: 未確認, note: "" }}')
    return "\n".join(lines) + "\n", False


def main():
    if not WEEKLY.is_dir():
        sys.exit("src/content/weekly が見つかりません。リポジトリ直下で実行してください。")

    now = datetime.datetime.now(JST)
    if len(sys.argv) > 1:
        try:
            base = datetime.date.fromisoformat(sys.argv[1])
        except ValueError:
            sys.exit("日付は YYYY-MM-DD で指定してください。")
    else:
        # 引数なしなら「直近に終わった週」（直近の金曜を含む週）。土日に書く想定
        # 土曜なら前日、日曜なら2日前、平日なら前週の金曜
        wd = now.date().weekday()
        base = now.date() - datetime.timedelta(days=wd - 4 if wd >= 5 else wd + 3)

    monday = base - datetime.timedelta(days=base.weekday())
    friday = monday + datetime.timedelta(days=4)
    year, week, _ = monday.isocalendar()

    path = WEEKLY / f"{year}-w{week:02d}.md"
    if path.exists():
        sys.exit(f"{path} はすでにあります。上書きしません。")

    # 来週（月〜金）のスケジュール枠を空で並べておく
    nw_mon = monday + datetime.timedelta(days=7)
    lines = []
    for i in range(5):
        d = nw_mon + datetime.timedelta(days=i)
        lines.append(f'  - date: "{d.isoformat()}"   # {WD[d.weekday()]}')
        lines.append('    items:')
        lines.append('      - { label: "", key: false }')
        if i == 4:
            # 週次の「ポジションとフロー」の材料。毎週金曜（米国の祝日は翌営業日）に出る
            lines.append('      - { label: "CFTC建玉（COT）の公表（火曜時点）", key: false }')
    schedule = "\n".join(lines) + "\n\n"

    performance, prefilled = performance_lines(f"{year}-w{week:02d}")
    body = TEMPLATE.format(
        performance=performance,
        year=year,
        week=week,
        start=monday.isoformat(),
        end=friday.isoformat(),
        pub=now.date().isoformat(),
        updated=now.strftime("%Y-%m-%d %H:%M JST"),
        schedule=schedule,
        nw_start_disp=f"{nw_mon.month}/{nw_mon.day}",
        nw_end_disp=f"{(nw_mon + datetime.timedelta(days=4)).month}/"
                    f"{(nw_mon + datetime.timedelta(days=4)).day}",
    )
    path.write_text(body, encoding="utf-8", newline="\n")

    print(f"作成: {path}")
    print(f"  {year}年 第{week}週")
    print(f"  対象期間: {monday}（{WD[monday.weekday()]}）〜 {friday}（{WD[friday.weekday()]}）")
    print(f"  来週の枠: {nw_mon} 〜 {nw_mon + datetime.timedelta(days=4)}")
    if prefilled:
        print(f"  performance: {DATA / f'{year}-w{week:02d}.json'} の取得値を入れました。note だけを書く")
    else:
        print("  注意: 取得値がありません。先に python tools/fetch-weekly.py --write を実行し、雛形を作り直してください")

    # その週の日次レポートが何本あるか。少なければ週次を書く材料が足りない
    if REPORTS.is_dir():
        have = [
            p.stem for p in sorted(REPORTS.glob("*.md"))
            if not p.name.startswith("_")
            and monday.isoformat() <= p.stem <= friday.isoformat()
        ]
        print(f"  この週の日次: {len(have)}本 {have if have else ''}")
        if len(have) < 2:
            print("  注意: 日次が少ないため、週次を書く材料が不足している可能性があります。")

    print("\n書き上げたら draft: false にして、以下で検査してください。")
    print("  python tools/check-report.py")


if __name__ == "__main__":
    main()
