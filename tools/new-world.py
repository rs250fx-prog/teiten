# -*- coding: utf-8 -*-
"""
「世界の定点」の雛形を作る（docs/SPEC.md §5 world）。

    python tools/new-world.py            # 直近に終わった週（週次と同じ週）
    python tools/new-world.py 2026-11-10 # その日を含む週
    python tools/new-world.py --en 2026-w46   # 英語版の雛形。日本語の号から論調・媒体・引用を写し、訳す欄だけ空にする

6つの窓（na / eu / ru / cn / in / me）を src/data/world-sources.json の主媒体で並べる。
論調（stance）と要約は人（定期実行）が書く。**数値は書かない。**
前週の答え合わせ（review）は tools/review-world.py が書く。

英語版（src/content/world-en/）は日本語の号が正本。論調・状態・媒体・引用・答え合わせは写すだけで、
訳すのは title / deck / description / points / summary / 本文。check-report.py が日本語版と突き合わせる。

既存ファイルがある場合は上書きせずに終了する。
"""
import sys
import re
import json
import datetime
import zoneinfo
from pathlib import Path

WORLD = Path("src/content/world")
WORLD_EN = Path("src/content/world-en")
SOURCES = Path("src/data/world-sources.json")
WEEKLY = Path("src/content/weekly")
JST = zoneinfo.ZoneInfo("Asia/Tokyo")
WD = "月火水木金土日"

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


HEAD = '''---
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

# 6つの窓。順序固定（na / eu / ru / cn / in / me）。媒体は src/data/world-sources.json の主／代替だけ。
# stance は bull / neutral / bear / split / unknown。summary は全角80字以内の自分の言葉（翻訳の転載ではない）。
#   split   … 1窓2媒体で向きが逆。中立に丸めず、summary に両方の読みを書く
#   unknown … その論点の記事が無かった。summary は理由を1行
# 3論点とも取れなかった窓は status: 未確認 にして gold 以下を消す。近い媒体や検索結果で埋めない。
# quote は原文の短い引用（30語・日本語なら60字以内）。出典 URL 必須。無くてよい。
# 対象は、対象週の月曜 0:00 JST から実行時刻（土曜 14:00 JST）までに読めた記事。記事 URL の日付で週を決める。
windows:
{windows}
# 現物の層への一言。キーは地域コード。値は書かない。src/data/world/<slug>.json に値が無い窓には書かない
physicalNotes: {{}}

# 前週の論調の答え合わせ。python tools/review-world.py {slug} --write が書く。手で判定しない
review:
  of: ""
  items: []

tags: [XAU/USD, DXY, 米10年債]
# 80〜100字。未記入だと deck が流用され、一覧で重複する
description: ""
draft: true
---

## 総括

<!-- 600字まで。「どの窓が外れたか」「地域で読みが割れた点」「論調と現物が食い違った窓」だけを書く。売買の推奨は書かない -->

情報元：

- []()
'''

WINDOW = '''  - region: {region}   # {label}
    media:
{media}
    gold:
      stance: unknown
      summary: ""
    dollar:
      stance: unknown
      summary: ""
    rates:
      stance: unknown
      summary: ""
    quote:
      text: ""
      source: ""
      url: ""
    status: 確定
'''


EN_HEAD = '''---
# English edition of src/content/world/{slug}.md. The Japanese issue is the original.
# Translate only: title / deck / description / points / each summary / the body.
# Do NOT change stance, status, media, quote text or review (check-report.py compares them with the Japanese file).
# Summaries: up to 220 characters, in our own words. No figures (values are drawn from the weekly JSON).
year: {year}
week: {week}
title: ""
deck: ""
start: "{start}"
end: "{end}"
date: "{date}"
updated: "{updated}"

points:
{points}
windows:
{windows}
physicalNotes: {{}}

{review}
tags: {tags}
description: ""
draft: true
---

## Summary

<!-- 300 to 1,200 characters. Which windows missed, where the regions split, where readings and physical flows diverged. No trading recommendations. -->

Sources:

- []()
'''


def yaml_str(s):
    """YAML の二重引用符の文字列にする"""
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def en_scaffold(slug):
    """日本語の号から英語版の雛形を作る。論調・媒体・引用・答え合わせは写し、訳す欄だけ空にする"""
    import yaml
    src = WORLD / f"{slug}.md"
    if not src.exists():
        sys.exit(f"{src} がありません。英語版は日本語の号から作ります。")
    out = WORLD_EN / f"{slug}.md"
    if out.exists():
        sys.exit(f"{out} はすでにあります。上書きしません。")
    WORLD_EN.mkdir(parents=True, exist_ok=True)
    m = re.match(r"^---\n(.*?)\n---\n", src.read_text(encoding="utf-8"), re.S)
    fm = yaml.safe_load(m.group(1))

    points = "\n".join(f'  - ""   # {p}' for p in fm.get("points") or []) or "  - \"\""
    blocks = []
    for w in fm["windows"]:
        lines = [f'  - region: {w["region"]}']
        lines.append("    media:")
        for md in w["media"]:
            lines.append(f'      - {{ name: {yaml_str(md["name"])}, url: {yaml_str(md["url"])} }}')
        if w.get("status") == "未確認":
            lines.append("    status: 未確認")
        else:
            for t in ("gold", "dollar", "rates"):
                take = w.get(t) or {}
                lines.append(f"    {t}:")
                lines.append(f'      stance: {take.get("stance", "unknown")}')
                lines.append(f'      summary: ""   # JA: {take.get("summary", "")}')
            q = w.get("quote")
            if q:
                lines.append("    quote:")
                lines.append(f'      text: {yaml_str(q.get("text", ""))}')
                lines.append(f'      source: {yaml_str(q.get("source", ""))}   # translate the source label if it contains Japanese')
                lines.append(f'      url: {yaml_str(q.get("url", ""))}')
            lines.append("    status: 確定")
        blocks.append("\n".join(lines) + "\n")

    rv = fm.get("review") or {}
    rlines = ["review:", f'  of: {yaml_str(rv.get("of", ""))}']
    items = rv.get("items") or []
    if not items:
        rlines.append("  items: []")
    else:
        rlines.append("  items:")
        for it in items:
            rlines.append(f'    - {{ region: {it["region"]}, topic: {it["topic"]}, stance: {it["stance"]}, '
                          f'result: {it["result"]}, note: "" }}   # JA: {it.get("note", "")}')
        rlines.append("  # Or run: python tools/review-world.py " + slug + " --write --en  (writes English notes)")
    tags = "[" + ", ".join(str(t) for t in fm.get("tags") or []) + "]"

    out.write_text(EN_HEAD.format(
        slug=slug, year=fm["year"], week=fm["week"], start=fm["start"], end=fm["end"],
        date=fm.get("date", fm["end"]), updated=fm.get("updated", ""),
        points=points, windows="\n".join(blocks), review="\n".join(rlines), tags=tags,
    ), encoding="utf-8", newline="\n")
    print(f"作成: {out}")
    print("  訳す欄: title / deck / description / points / summary / 本文（## Summary と Sources:）")
    print(f"  書き上げたら: python tools/check-report.py {slug}")


def main():
    if not WORLD.is_dir():
        sys.exit("src/content/world が見つかりません。リポジトリ直下で実行してください。")
    if "--en" in sys.argv:
        slugs = [a for a in sys.argv[1:] if re.match(r"^\d{4}-w\d{2}$", a)]
        if not slugs:
            sys.exit("--en には YYYY-wNN を指定してください。")
        en_scaffold(slugs[0])
        return
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))["regions"]

    now = datetime.datetime.now(JST)
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        try:
            base = datetime.date.fromisoformat(sys.argv[1])
        except ValueError:
            sys.exit("日付は YYYY-MM-DD で指定してください。")
    else:
        # 引数なしなら「直近に終わった週」。new-weekly.py と同じ決め方
        wd = now.date().weekday()
        base = now.date() - datetime.timedelta(days=wd - 4 if wd >= 5 else wd + 3)

    monday = base - datetime.timedelta(days=base.weekday())
    friday = monday + datetime.timedelta(days=4)
    year, week, _ = monday.isocalendar()
    slug = f"{year}-w{week:02d}"

    path = WORLD / f"{slug}.md"
    if path.exists():
        sys.exit(f"{path} はすでにあります。上書きしません。")

    blocks = []
    for r in sources:
        media = "\n".join(
            f'      - {{ name: "{m["name"]}", url: "{m["list"]}" }}' for m in r["primary"]
        )
        blocks.append(WINDOW.format(region=r["region"], label=r["label"], media=media))

    body = HEAD.format(
        year=year, week=week, slug=slug,
        start=monday.isoformat(), end=friday.isoformat(),
        pub=now.date().isoformat(),
        updated=now.strftime("%Y-%m-%d %H:%M JST"),
        windows="\n".join(blocks),
    )
    path.write_text(body, encoding="utf-8", newline="\n")

    print(f"作成: {path}")
    print(f"  {year}年 第{week}週　対象期間: {monday}（{WD[monday.weekday()]}）〜 {friday}（{WD[friday.weekday()]}）")
    print("  各窓の media の url は一覧ページ。読んだ記事の URL に差し替える（quote.url も）")
    wk = WEEKLY / f"{slug}.md"
    print(f"  同じ週の週次まとめ: {'あり' if wk.exists() else '無し（世界の定点は週次本体と同じコミットで出す）'}")
    print("\n書き上げたら次を実行してください。")
    print(f"  python tools/review-world.py {slug} --write   # 前週の答え合わせ")
    print(f"  python tools/check-report.py {slug}")


if __name__ == "__main__":
    main()
