# -*- coding: utf-8 -*-
"""
「世界の定点」の前週の論調を、当週の週次 JSON の前週比で機械判定する（docs/SPEC.md §5 world）。

    python tools/review-world.py 2026-w47            # 判定を表示（第46週の論調 × 第47週の JSON）
    python tools/review-world.py 2026-w47 --write    # src/content/world/2026-w47.md の review に書き込む
    python tools/review-world.py 2026-w47 --write --en   # 英語版 src/content/world-en/2026-w47.md に、英語の note で書き込む

規則
  - 金（xau）・ドル指数（dxy）は前週比 ±0.5%、米10年（us10y）は ±5bp を閾値にする
  - 閾値を超えた上昇は bull、下落は bear、閾値内は neutral が hit
  - 方向は合ったが閾値内なら partial、逆なら miss。neutral の論調で閾値を超えたら miss
  - stance が split / unknown の論点は判定しない（items に入れない）
  - 期限の無い論調なので pending は使わない。JSON が無い週は判定できないので終了コード 2

人の印象で判定しない。手で書いた review は check-report.py がこのスクリプトの結果と突き合わせる。
"""
import sys
import re
import json
from pathlib import Path

import yaml

WORLD = Path("src/content/world")
WORLD_EN = Path("src/content/world-en")
WEEKLY_DATA = Path("src/data/weekly")
TOPIC_LABEL_EN = {"gold": "Gold", "dollar": "Dollar index", "rates": "10-year yield"}

# 論点 → 週次 JSON の key・単位・閾値。src/lib/world.ts の JUDGE と同じ値
JUDGE = {
    "gold":   ("xau",   "%",  0.5),
    "dollar": ("dxy",   "%",  0.5),
    "rates":  ("us10y", "bp", 5.0),
}
TOPICS = ["gold", "dollar", "rates"]
REGION_LABEL = {"na": "北米", "eu": "欧州", "ru": "ロシア", "cn": "中国", "in": "インド", "me": "中東"}
TOPIC_LABEL = {"gold": "金", "dollar": "ドル指数", "rates": "米10年"}
STANCE_LABEL = {"bull": "強気", "neutral": "中立", "bear": "弱気"}

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def prev_slug(slug):
    import datetime
    y, w = re.match(r"^(\d{4})-w(\d{2})$", slug).groups()
    y, w = int(y), int(w)
    if w > 1:
        return f"{y}-w{w - 1:02d}"
    last = datetime.date(y - 1, 12, 28).isocalendar()
    return f"{last[0]}-w{last[1]:02d}"


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        sys.exit(f"{path}: frontmatter がありません")
    return yaml.safe_load(m.group(1)), text


def moves(slug):
    """当週の JSON から3系列の前週比を出す。{topic: (move, unit, asof, prev_asof)}"""
    path = WEEKLY_DATA / f"{slug}.json"
    if not path.exists():
        return None
    assets = {a["key"]: a for a in json.loads(path.read_text(encoding="utf-8")).get("assets", [])}
    out = {}
    for topic, (key, unit, _th) in JUDGE.items():
        a = assets.get(key)
        if not a or a.get("close") is None or a.get("prev") is None:
            continue
        if unit == "bp":
            mv = (a["close"] - a["prev"]) * 100
        else:
            mv = (a["close"] - a["prev"]) / a["prev"] * 100
        out[topic] = (mv, unit, a.get("asof", ""), a.get("prev_asof", ""))
    return out


def judge(stance, move, threshold):
    """(result, actual_dir)。actual_dir は閾値を超えた向き（up / down / flat）"""
    actual = "up" if move > threshold else "down" if move < -threshold else "flat"
    want = {"bull": "up", "bear": "down", "neutral": "flat"}[stance]
    if actual == want:
        return "hit", actual
    if stance == "neutral":
        return "miss", actual
    # 閾値内で、向きだけ合っている
    if actual == "flat" and ((stance == "bull" and move > 0) or (stance == "bear" and move < 0)):
        return "partial", actual
    return "miss", actual


def fmt(move, unit):
    if unit == "bp":
        s = f"{abs(move):.0f}bp"
    else:
        s = f"{abs(move):.2f}%"
    sign = "+" if move > 0 else "−" if move < 0 else "±"
    return f"{sign}{s}"


def build(slug, lang="ja"):
    """前週の論調（日本語の原本）を当週の JSON で判定する。lang は note の言語だけに効く"""
    prev = prev_slug(slug)
    prev_path = WORLD / f"{prev}.md"
    if not prev_path.exists():
        print(f"前週の号 {prev_path} がありません。初号なので review は空のままにします。")
        return {"of": "", "items": []}, prev
    mv = moves(slug)
    if mv is None:
        print(f"{WEEKLY_DATA / (slug + '.json')} がありません。先に python tools/fetch-weekly.py --write を実行してください。")
        sys.exit(2)
    fm, _ = frontmatter(prev_path)
    items = []
    for w in fm.get("windows", []):
        if w.get("status") == "未確認":
            continue
        for topic in TOPICS:
            take = w.get(topic) or {}
            stance = take.get("stance")
            if stance not in ("bull", "neutral", "bear"):
                continue
            if topic not in mv:
                continue
            move, unit, asof, pasof = mv[topic]
            _key, _u, th = JUDGE[topic]
            result, actual = judge(stance, move, th)
            if lang == "en":
                note = (f"{TOPIC_LABEL_EN[topic]} {fmt(move, unit)} week on week "
                        f"({pasof[5:].replace('-', '/')} to {asof[5:].replace('-', '/')})")
            else:
                note = (f"{TOPIC_LABEL[topic]}は前週比 {fmt(move, unit)}"
                        f"（{pasof[5:].replace('-', '/')}→{asof[5:].replace('-', '/')}）")
            items.append({"region": w["region"], "topic": topic, "stance": stance,
                          "result": result, "note": note})
    return {"of": prev, "items": items}, prev


def to_yaml(review):
    lines = [f'review:', f'  of: "{review["of"]}"']
    if not review["items"]:
        lines.append("  items: []")
    else:
        lines.append("  items:")
        for it in review["items"]:
            lines.append(f'    - {{ region: {it["region"]}, topic: {it["topic"]}, stance: {it["stance"]}, '
                         f'result: {it["result"]}, note: "{it["note"]}" }}')
    return "\n".join(lines) + "\n"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args or not re.match(r"^\d{4}-w\d{2}$", args[0]):
        sys.exit(__doc__)
    slug = args[0]
    write = "--write" in sys.argv
    lang = "en" if "--en" in sys.argv else "ja"

    review, prev = build(slug, lang)
    block = to_yaml(review)
    print(block)
    if review["items"]:
        n = {k: sum(1 for i in review["items"] if i["result"] == k) for k in ("hit", "partial", "miss")}
        print(f"第{prev[-2:]}週の論調 {len(review['items'])}論点：想定どおり {n['hit']}・方向は合った {n['partial']}・想定と違った {n['miss']}")

    if not write:
        return
    path = (WORLD_EN if lang == "en" else WORLD) / f"{slug}.md"
    if not path.exists():
        sys.exit(f"{path} がありません。先に python tools/new-world.py{' --en ' + slug if lang == 'en' else ''} を実行してください。")
    text = path.read_text(encoding="utf-8")
    # frontmatter の review: ブロック（次のトップレベルのキーまで）を差し替える
    new, n = re.subn(r"^review:\n(?:[ \t]+.*\n|[ \t]*\n)*?(?=^\S)", block, text, count=1, flags=re.M)
    if n == 0:
        sys.exit("review: のブロックが見つかりません")
    path.write_text(new, encoding="utf-8", newline="\n")
    print(f"書き込み: {path}")


if __name__ == "__main__":
    main()
