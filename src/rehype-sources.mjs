/**
 * 本文の「情報元：」と直後のリストを、閉じたアコーディオンに変換する rehype プラグイン。
 *
 * 1号に8か所・50行近い出典が並び、本文を読む流れを切っていた。
 * 原稿の書式は変えない（note への流用と check-report.py の検査が前提にしている）。
 * ビルド時に変換するので、過去の号にも今後の号にも同じように効く。
 *
 *   <details class="sources">
 *     <summary>情報元：FRED、米財務省、CNBC ほか3件</summary>
 *     <ul>…元のリストそのまま…</ul>
 *   </details>
 *
 * - 閉じていても発行根拠が分かるよう、見出しに媒体名を先頭から最大3つ出す（YMYL。SPEC §9）
 * - 件数の計算は「見出しに出した媒体数 + ほかN件 = リストの行数」。
 *   tools/check-html.mjs がビルド後にこの式を確かめる
 * - 「情報元：」だけの段落の直後にリストがなければ変換しない（次の節のリストを巻き込まない）
 */

// 日本語は「情報元：」、英語版（src/content/world-en）は「Sources:」。見出しの件数の書き方も言語で変える
const LABELS = {
  '情報元：': { more: (n) => ` ほか${n}件`, sep: '、' },
  'Sources:': { more: (n) => ` and ${n} more`, sep: ', ' },
};
const MAX_NAMES = 3;

const isWhitespace = (node) => node?.type === 'text' && !node.value.trim();

/** 要素の子孫のテキストを連結する */
function textOf(node) {
  if (node.type === 'text') return node.value;
  return (node.children ?? []).map(textOf).join('');
}

/** 「媒体名（記事名、日付）」から媒体名だけを取り出す */
const mediaName = (li) => textOf(li).trim().split(/[（(]/)[0].trim();

function summaryText(label, items) {
  const { more, sep } = LABELS[label];
  const names = [...new Set(items.map(mediaName).filter(Boolean))].slice(0, MAX_NAMES);
  const rest = items.length - names.length;
  return `${label}${label.endsWith(':') ? ' ' : ''}${names.join(sep)}${rest > 0 ? more(rest) : ''}`;
}

const element = (tagName, properties, children) => ({
  type: 'element',
  tagName,
  properties,
  children,
});

function wrapSources(parent) {
  const out = [];
  const kids = parent.children;

  for (let i = 0; i < kids.length; i++) {
    const node = kids[i];
    const label =
      node.type === 'element' && node.tagName === 'p' ? textOf(node).trim() : '';
    const isLabel = Object.hasOwn(LABELS, label);

    let next = i + 1;
    while (isWhitespace(kids[next])) next++;
    const list = kids[next];

    if (isLabel && list?.type === 'element' && list.tagName === 'ul') {
      const items = list.children.filter((c) => c.type === 'element' && c.tagName === 'li');
      out.push(
        element('details', { className: ['sources'] }, [
          element('summary', {}, [{ type: 'text', value: summaryText(label, items) }]),
          list,
        ]),
      );
      i = next;
      continue;
    }
    out.push(node);
  }
  parent.children = out;
}

export function rehypeSources() {
  return (tree) => {
    const walk = (node) => {
      if (!node.children) return;
      wrapSources(node);
      node.children.forEach(walk);
    };
    walk(tree);
  };
}
