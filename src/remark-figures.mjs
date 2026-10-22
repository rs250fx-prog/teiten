import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import yaml from 'js-yaml';

/**
 * 日次レポートの本文に、図を差し込む remark プラグイン。
 *
 * 文字だけの本文は読み疲れるため、節の頭（見出し直後の最初の段落の後）に
 * 図を置いて、読む前に流れをつかめるようにする。**本文の Markdown は変えない。**
 * note に流用する原稿は素のまま残し、図はサイトの表示でだけ足す。
 *
 * 材料は2つ。どちらも新しく取りに行かない。
 *
 *   1. frontmatter の infographic（note 用の図解と同じ文言。tools/make-infographic.mjs と共用）
 *      → 資金フローの帯と反応の図、主役の指標、金利、金の綱引き、注目銘柄
 *   2. 過去の号の snapshot（定点観測の推移）
 *      → 米10年債・ドル指数・金の直近20号の折れ線
 *
 * infographic が無い号（10/15 より前）には推移の折れ線だけが出る。
 * 数値は ref で snapshot / infographic.quotes を引く（make-infographic.mjs と同じ規則）。
 */

const REPORTS_DIR = join(process.cwd(), 'src/content/reports');
const TREND_N = 20;

const esc = (s) =>
  String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
/** 改行（\n）は1つの見出しの中の改行。サイトでは空白に寄せる */
const oneLine = (s) => esc(String(s ?? '').replace(/\n/g, ' '));
const DIR_CLASS = { up: 'up', down: 'down', flat: 'flat' };
const dirCls = (d) => DIR_CLASS[d] ?? 'flat';
const ARROW = { up: '▲', down: '▼', flat: '―' };

// ── 推移（過去の号の snapshot） ─────────────────────────
function loadSeries() {
  const rows = [];
  for (const f of readdirSync(REPORTS_DIR)) {
    if (!/^\d{4}-\d{2}-\d{2}\.md$/.test(f)) continue;
    const raw = readFileSync(join(REPORTS_DIR, f), 'utf8');
    const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---/);
    if (!m) continue;
    let d;
    try {
      d = yaml.load(m[1]);
    } catch {
      continue;
    }
    if (!d || d.draft) continue;
    rows.push({ date: String(d.date ?? f.slice(0, 10)), snapshot: d.snapshot ?? [] });
  }
  return rows.sort((a, b) => a.date.localeCompare(b.date));
}

const num = (v) => {
  const n = Number(String(v ?? '').replace(/[,%ドル円\s]/g, ''));
  return Number.isFinite(n) ? n : null;
};

/** 発行日までの直近 n 号から、label が match に当たる行の値を取る */
function trend(rows, upto, match, n = TREND_N) {
  return rows
    .filter((r) => r.date <= upto)
    .map((r) => {
      const q = r.snapshot.find((s) => match.test(s.label ?? ''));
      return q ? { date: r.date, v: num(q.value), label: q.value } : null;
    })
    .filter((p) => p && p.v !== null)
    .slice(-n);
}

const md = (iso) => `${Number(iso.slice(5, 7))}/${Number(iso.slice(8, 10))}`;

/** 折れ線。色は currentColor、罫は --line。最新の点に値を添える */
function spark(points, { title, unit = '' }) {
  if (points.length < 3) return '';
  const W = 600;
  const H = 120;
  const P = { l: 8, r: 70, t: 14, b: 22 };
  const vs = points.map((p) => p.v);
  let lo = Math.min(...vs);
  let hi = Math.max(...vs);
  if (hi === lo) {
    hi += 1;
    lo -= 1;
  }
  const x = (i) => P.l + (i * (W - P.l - P.r)) / (points.length - 1);
  const y = (v) => P.t + ((hi - v) * (H - P.t - P.b)) / (hi - lo);
  const d = points.map((p, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)} ${y(p.v).toFixed(1)}`).join(' ');
  const last = points[points.length - 1];
  const first = points[0];
  const lx = x(points.length - 1);
  const ly = y(last.v);
  const hiP = points.find((p) => p.v === Math.max(...vs));
  const loP = points.find((p) => p.v === Math.min(...vs));
  const desc = `${title}の推移。${md(first.date)}の${first.label}${unit}から${md(last.date)}の${last.label}${unit}。期間の高値は${hiP.label}${unit}（${md(hiP.date)}）、安値は${loP.label}${unit}（${md(loP.date)}）`;
  return `<figure class="fig fig-trend">
<figcaption><span class="fig-k">定点</span>${esc(title)}<span class="fig-sub">直近${points.length}号</span></figcaption>
<div class="plot">
<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(desc)}" preserveAspectRatio="none">
<line x1="${P.l}" x2="${W - P.r}" y1="${y(hi)}" y2="${y(hi)}" class="grid"/>
<line x1="${P.l}" x2="${W - P.r}" y1="${y(lo)}" y2="${y(lo)}" class="grid"/>
<path d="${d}" class="line" vector-effect="non-scaling-stroke"/>
</svg>
<span class="dot" style="left:${((lx / W) * 100).toFixed(2)}%;top:${((ly / H) * 100).toFixed(2)}%"></span>
</div>
<div class="trend-meta">
<span>高 ${esc(hiP.label)}<small>${md(hiP.date)}</small></span>
<span>安 ${esc(loP.label)}<small>${md(loP.date)}</small></span>
<span class="now">${md(last.date)} <b>${esc(last.label)}${esc(unit)}</b></span>
</div>
</figure>`;
}

// ── infographic の各ブロック ─────────────────────────
function resolver(fm) {
  const quotes = [...(fm.snapshot ?? []), ...(fm.infographic?.quotes ?? [])];
  return (item) => {
    if (!item?.ref) return item;
    const q = quotes.find((s) => String(s.label).includes(item.ref));
    return q ? { label: q.label, ...q, ...item } : null;
  };
}

function flowFig(ig) {
  const flow = ig.flow ?? [];
  const r = ig.reaction;
  if (!flow.length && !r) return '';
  let html = '<figure class="fig fig-flow">\n<figcaption><span class="fig-k">資金フロー</span>今日の流れ</figcaption>\n';
  if (flow.length) {
    html += `<ol class="flow-strip">${flow
      .map((f) => `<li class="t-${esc(f.tone ?? 'navy')}">${oneLine(f.text)}</li>`)
      .join('')}</ol>\n`;
  }
  if (r) {
    const node = (n, cls) =>
      `<div class="node ${cls} ${n.dir ? dirCls(n.dir) : ''}"><b>${oneLine(n.text)}${n.dir ? ` <i aria-hidden="true">${ARROW[n.dir] ?? ''}</i>` : ''}</b>${n.sub ? `<span>${oneLine(n.sub)}</span>` : ''}</div>`;
    html += `<div class="tree">
<div class="tier tier-root">${node(r.root, 'root')}</div>
<div class="tier tier-mid">${(r.mid ?? []).map((n) => node(n, 'mid')).join('')}</div>
<div class="tier tier-leaf">${(r.leaves ?? []).map((n) => node(n, 'leaf')).join('')}</div>
</div>\n`;
    if (r.lead) html += `<p class="fig-note">${oneLine(r.lead)}</p>\n`;
  }
  return html + '</figure>';
}

function focusFig(f) {
  if (!f?.compare?.length) return '';
  const cards = f.compare
    .map((c) => {
      const fv = Number(c.forecast);
      const av = Number(c.actual);
      const max = Math.max(fv, av) || 1;
      const s = c.suffix ?? '';
      const tag = av > fv ? '上振れ' : av < fv ? '下振れ' : '予想どおり';
      return `<div class="cmp">
<div class="cmp-h"><b>${oneLine(c.label)}</b>${c.unit ? `<span>${oneLine(c.unit)}</span>` : ''}<em>${tag}</em></div>
<div class="bar"><span class="lab">予想</span><span class="track"><span class="fill fc" style="width:${((fv / max) * 100).toFixed(1)}%"></span></span><span class="val">${esc(fv)}${esc(s)}</span></div>
<div class="bar"><span class="lab">結果</span><span class="track"><span class="fill ac" style="width:${((av / max) * 100).toFixed(1)}%"></span></span><span class="val strong">${esc(av)}${esc(s)}</span></div>
</div>`;
    })
    .join('');
  const h = f.highlight;
  const hl = h
    ? `<div class="hl ${dirCls(h.dir)}"><span>${oneLine(h.label)}${h.unit ? `（${oneLine(h.unit)}）` : ''}</span><b>${oneLine(h.value)}</b>${h.note ? `<small>${oneLine(h.note)}</small>` : ''}</div>`
    : '';
  return `<figure class="fig fig-focus">
<figcaption><span class="fig-k">指標</span>${oneLine(f.title)}</figcaption>
<div class="focus-grid">${cards}${hl}</div>
<p class="fig-note">棒は0起点。予想との差が小さければ棒の差も小さい</p>
</figure>`;
}

function statCard(q) {
  return `<div class="stat ${dirCls(q.dir)}"><span class="k">${oneLine(q.name ?? q.label)}</span><b>${esc(q.value)}</b><span class="chg">${ARROW[q.dir] ?? ''} ${esc(q.change ?? '')}</span>${q.caption ? `<small>${oneLine(q.caption)}</small>` : ''}</div>`;
}

function ratesFig(r, resolve) {
  const cards = (r?.cards ?? []).map(resolve).filter(Boolean);
  if (!cards.length) return '';
  return `<figure class="fig fig-rates">
<figcaption><span class="fig-k">金利</span>${oneLine(r.title)}</figcaption>
<div class="stats">${cards.map(statCard).join('')}</div>
${r.note ? `<div class="aside"><b>${oneLine(r.note.title)}</b><p>${oneLine(r.note.text)}</p></div>` : ''}
</figure>`;
}

function goldFig(g, resolve) {
  if (!g) return '';
  const side = (items) =>
    (items ?? [])
      .map(resolve)
      .filter(Boolean)
      .map((q) => `<li class="${dirCls(q.dir)}"><b>${oneLine(q.name ?? q.label)}${q.dir ? ` <i aria-hidden="true">${ARROW[q.dir] ?? ''}</i>` : ''}</b>${q.value ? `<span>${esc(q.value)}${q.change ? `（${esc(q.change)}）` : ''}</span>` : ''}</li>`)
      .join('');
  const price = resolve({ ref: g.price_ref ?? 'XAU' });
  return `<figure class="fig fig-gold">
<figcaption><span class="fig-k">金</span>${oneLine(g.title)}</figcaption>
<div class="tug">
<div class="pan light"><span class="pan-h">軽い側</span><ul>${side(g.light)}</ul></div>
<svg class="scale" viewBox="0 0 120 80" aria-hidden="true"><line x1="10" y1="22" x2="110" y2="42" /><line x1="60" y1="30" x2="60" y2="74"/><line x1="42" y1="76" x2="78" y2="76"/><circle cx="60" cy="31" r="4"/></svg>
<div class="pan heavy"><span class="pan-h">重い側</span><ul>${side(g.heavy)}</ul></div>
</div>
${price ? `<div class="price ${dirCls(price.dir)}"><span>XAU/USD</span><b>${esc(price.value)}<small>ドル</small></b><em>${ARROW[price.dir] ?? ''} ${esc(price.change ?? '')}</em>${g.sub_price ? `<small class="sub">${oneLine(g.sub_price)}</small>` : ''}</div>` : ''}
${g.conclusion ? `<p class="fig-note">${oneLine(g.conclusion)}</p>` : ''}
</figure>`;
}

function moversFig(mv, resolve) {
  const items = (mv?.items ?? []).map(resolve).filter(Boolean);
  if (!items.length) return '';
  return `<figure class="fig fig-movers">
<figcaption><span class="fig-k">注目</span>${oneLine(mv.title ?? '注目銘柄')}</figcaption>
<ul>${items
    .map((q) => `<li class="${dirCls(q.dir)}"><b>${oneLine(q.name ?? q.label)}</b><em>${ARROW[q.dir] ?? ''} ${esc(q.change ?? '')}</em>${q.note ? `<small>${oneLine(q.note)}</small>` : ''}</li>`)
    .join('')}</ul>
</figure>`;
}

// ── 差し込み ─────────────────────────────────────────
const text = (node) =>
  (node.children ?? []).map((c) => (c.type === 'text' || c.type === 'inlineCode' ? c.value : text(c))).join('');

/**
 * 見出しの後の最初の段落の後に html を差し込む。段落が無ければ見出しの直後。
 * 次の見出しを越えては探さない
 */
function insertAfterLead(tree, test, html) {
  if (!html) return;
  const kids = tree.children;
  const h = kids.findIndex((n) => n.type === 'heading' && test(n.depth, text(n).trim()));
  if (h < 0) return;
  let at = h + 1;
  for (let i = h + 1; i < kids.length && kids[i].type !== 'heading' && kids[i].type !== 'thematicBreak'; i++) {
    if (kids[i].type === 'paragraph') {
      at = i + 1;
      break;
    }
  }
  kids.splice(at, 0, { type: 'html', value: html });
}

export function remarkFigures() {
  return (tree, file) => {
    const fm = file.data?.astro?.frontmatter;
    // 日次レポートだけ。週次・固定ページには出さない
    const path = String(file.path ?? file.history?.[0] ?? '').replace(/\\/g, '/');
    if (!fm || !/\/content\/reports\/\d{4}-\d{2}-\d{2}\.md$/.test(path)) return;

    const date = String(fm.date ?? '');
    const ig = fm.infographic;
    const resolve = resolver(fm);
    const rows = loadSeries();

    const is = (depth, re) => (d, t) => d === depth && re.test(t);

    if (ig) {
      insertAfterLead(tree, is(2, /^Macro Theme/), flowFig(ig));
      insertAfterLead(tree, is(3, /^①/), focusFig(ig.focus));
    }
    insertAfterLead(
      tree,
      is(2, /^金利/),
      (ig ? ratesFig(ig.rates, resolve) : '') + spark(trend(rows, date, /米10年/), { title: '米10年債利回り' }),
    );
    insertAfterLead(tree, is(2, /^ドル$/), spark(trend(rows, date, /DXY/), { title: 'ドル指数（DXY）' }));
    insertAfterLead(
      tree,
      is(2, /^商品/),
      spark(trend(rows, date, /XAU/), { title: '金（XAU/USD）', unit: 'ドル' }),
    );
    if (ig) {
      insertAfterLead(tree, is(3, /^Macro Drivers/), goldFig(ig.gold, resolve));
      insertAfterLead(tree, is(2, /^株$/), moversFig(ig.movers, resolve));
    }
  };
}
