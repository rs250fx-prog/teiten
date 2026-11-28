# -*- coding: utf-8 -*-
"""
週次まとめの英語版の雛形を、日本語の号から作る（docs/SPEC.md §5「週次の英語版」）。

    python tools/new-weekly-en.py 2026-w46
    python tools/new-weekly-en.py --all      # 公開済みで英語版の無い号をまとめて作る

日本語の号が正本。**値・変化率・dir・status・key・日付・kind は写すだけで変えない**
（`check-report.py` の `check_weekly_en` が突き合わせる）。空にするのは訳す欄だけで、
元の日本語は行末に `# JA:` として残す。note 用の `thumb` と `infographic` は英語版に持たない。

既存ファイルがある場合は上書きせずに飛ばす。
"""
import sys
import re
from pathlib import Path

import yaml

WEEKLY = Path("src/content/weekly")
WEEKLY_EN = Path("src/content/weekly-en")

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

BODY = '''
## The core theme of the week

<!-- Translate the Japanese section of the same name. Keep every figure identical; do not add or drop numbers. -->

## Key events, reviewed

### 1

### 2

### 3

## How money moved this week

**  →   →  **

## Looking to next week

### The event that matters most

### Domestic politics and policy

### Geopolitics

### Nikkei and the yen

Expected range: high 　　 / low

### Gold, silver and USD/JPY

Gold: high 　　 / low
Silver: high 　　 / low
USD/JPY: high 　　 / low
'''


def q(s):
    """YAML の二重引用符つき文字列"""
    return '"' + str(s if s is not None else "").replace("\\", "\\\\").replace('"', '\\"') + '"'


def ja(*parts):
    """行末に残す日本語。空の項目は書かない"""
    txt = " / ".join(str(p) for p in parts if p)
    return f"   # JA: {txt}" if txt else ""


def scaffold(slug):
    src = WEEKLY / f"{slug}.md"
    if not src.exists():
        sys.exit(f"{src} がありません。英語版は日本語の号から作ります。")
    out = WEEKLY_EN / f"{slug}.md"
    if out.exists():
        print(f"  飛ばす: {out} はすでにあります")
        return False
    text = src.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        sys.exit(f"{src}: frontmatter がありません")
    fm = yaml.safe_load(m.group(1))

    L = [
        "---",
        f"# English edition of src/content/weekly/{slug}.md. The Japanese issue is the original.",
        "# Translate only the empty fields below and the body. Every `# JA:` comment is the source text.",
        "# Do NOT change key / value / change / dir / status / kind / dates: check-report.py compares them",
        "# with the Japanese file. Figures in a note must also appear in the Japanese note.",
        f"year: {fm['year']}",
        f"week: {fm['week']}",
        f"title: \"\"{ja(fm.get('title'))}",
        f"deck: \"\"{ja(fm.get('deck'))}",
        f"start: {q(fm['start'])}",
        f"end: {q(fm['end'])}",
        f"date: {q(fm.get('date', fm['end']))}",
        f"updated: {q(fm.get('updated', ''))}",
        "",
        # 空の配列・辞書は `points:` だけにすると null になり、スキーマが通らない（第39週など）
        "points:" if fm.get("points") else "points: []",
    ]
    for p in fm.get("points") or []:
        L.append(f'  - ""{ja(p)}')

    L += ["", "# value / change / dir / status / key are copied from the Japanese issue. Translate label and note only.",
          "performance:" if fm.get("performance") else "performance: []"]
    for r in fm.get("performance") or []:
        parts = []
        if r.get("key"):
            parts.append(f"key: {r['key']}")
        if r.get("group"):
            parts.append(f"group: {r['group']}")
        parts.append('label: ""')
        parts.append(f"value: {q(r.get('value', ''))}")
        parts.append(f"change: {q(r.get('change', ''))}")
        parts.append(f"dir: {r.get('dir', 'flat')}")
        if r.get("status") and r["status"] != "確定":
            parts.append(f"status: {r['status']}")
        parts.append('note: ""')
        L.append("  - { " + ", ".join(parts) + " }" + ja(r.get("label"), r.get("note")))

    L += ["", "ratioNotes:" if fm.get("ratioNotes") else "ratioNotes: {}"]
    for k, v in (fm.get("ratioNotes") or {}).items():
        L.append(f'  {k}: ""{ja(v)}')

    if fm.get("flows"):
        L += ["", "flows:"]
        for f in fm["flows"]:
            parts = [
                'label: ""',
                f"value: {q(f.get('value', ''))}",
                f"change: {q(f.get('change', ''))}",
                f"dir: {f.get('dir', 'flat')}",
                f"status: {f.get('status', '確定')}",
                f"source: {q(f.get('source', ''))}",
                'note: ""',
            ]
            L.append("  - { " + ", ".join(parts) + " }" + ja(f.get("label"), f.get("note")))

    if fm.get("schedule"):
        L += ["", "# Dates and the key flag are copied. Translate each label (event names).", "schedule:"]
        for d in fm["schedule"]:
            L.append(f"  - date: {q(d['date'])}")
            L.append("    items:")
            for it in d.get("items") or []:
                L.append(f'      - {{ label: "", key: {str(it.get("key", False)).lower()} }}{ja(it.get("label"))}')

    L += ["", "# kind and value are copied. Translate note only.",
          "levels:" if fm.get("levels") else "levels: []"]
    for lv in fm.get("levels") or []:
        L.append(f'  - {{ kind: {lv["kind"]}, value: {q(lv.get("value", ""))}, note: "" }}{ja(lv.get("note"))}')

    if fm.get("moreLevels"):
        L += ["", "moreLevels:"]
        for ml in fm["moreLevels"]:
            L.append(f'  - asset: ""{ja(ml.get("asset"))}')
            L.append("    levels:")
            for lv in ml.get("levels") or []:
                L.append(f'      - {{ kind: {lv["kind"]}, value: {q(lv.get("value", ""))}, note: "" }}{ja(lv.get("note"))}')

    if fm.get("scenarios"):
        L += ["", "scenarios:"]
        for s in fm["scenarios"]:
            L.append(f'  - {{ kind: {s["kind"]}, trigger: "", chain: "", target: "" }}'
                     + ja(s.get("trigger"), s.get("chain"), s.get("target")))

    L += [
        "",
        f'bias: ""{ja(fm.get("bias"))}',
        "",
        f"tags: [{', '.join(str(t) for t in fm.get('tags') or [])}]",
        '# 80 characters or more.',
        f'description: ""{ja(fm.get("description"))}',
        "draft: true",
        "---",
    ]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + BODY, encoding="utf-8", newline="\n")
    print(f"  作成: {out}")
    return True


def main():
    if not WEEKLY.is_dir():
        sys.exit("src/content/weekly が見つかりません。リポジトリ直下で実行してください。")
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if "--all" in sys.argv:
        slugs = []
        for p in sorted(WEEKLY.glob("*.md")):
            if p.name.startswith("_"):
                continue
            fm = re.match(r"^---\n(.*?)\n---\n", p.read_text(encoding="utf-8"), re.S)
            if fm and re.search(r"^draft:\s*true\s*$", fm.group(1), re.M):
                continue  # 下書きの号には英語版を作らない
            slugs.append(p.stem)
    elif args and re.match(r"^\d{4}-w\d{2}$", args[0]):
        slugs = [args[0]]
    else:
        sys.exit(__doc__)

    n = sum(1 for s in slugs if scaffold(s))
    print(f"\n{n}件を作成しました（対象 {len(slugs)}件）。")
    print("訳す欄: title / deck / description / points / label と note / ratioNotes / schedule の label /")
    print("        levels の note / moreLevels の asset と note / scenarios / bias / 本文")
    print("書き上げたら: python tools/check-report.py <YYYY-wNN>")


if __name__ == "__main__":
    main()
