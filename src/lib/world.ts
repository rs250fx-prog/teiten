/**
 * 「世界の定点」（src/content/world・world-en）の表示用の補助と、答え合わせの判定。
 *
 * 判定の規則は docs/SPEC.md §5「world」の「論調の判定規則」。tools/review-world.py と
 * 同じ閾値をここにも持つのは、ページ側で「当週の実績」を添えて描くため。
 * **判定そのものは review-world.py が書いた frontmatter の review を使い、ここでは判定し直さない。**
 *
 * 表示の文言は日本語が既定で、lang === 'en' のときだけ src/i18n.ts の EN_LABELS を引く。
 */
import { weeklyData, signed, dirOf } from './weekly';
import { EN_LABELS, type Lang } from '../i18n';

export const REGIONS = [
  { key: 'na', label: '北米' },
  { key: 'eu', label: '欧州' },
  { key: 'ru', label: 'ロシア' },
  { key: 'cn', label: '中国' },
  { key: 'in', label: 'インド' },
  { key: 'me', label: '中東' },
] as const;
export type RegionKey = (typeof REGIONS)[number]['key'];
export const regionLabel = (k: string, lang: Lang = 'ja') =>
  lang === 'en' ? (EN_LABELS.region[k] ?? k) : (REGIONS.find((r) => r.key === k)?.label ?? k);

/** 3つの論点。表示順もこの順 */
export const TOPICS_W = [
  { key: 'gold', label: '金', short: '金' },
  { key: 'dollar', label: 'ドル', short: 'ドル' },
  { key: 'rates', label: '米金利', short: '金利' },
] as const;
export type TopicKey = (typeof TOPICS_W)[number]['key'];
export const topicLabel = (k: string, lang: Lang = 'ja') =>
  lang === 'en' ? (EN_LABELS.topic[k] ?? k) : (TOPICS_W.find((t) => t.key === k)?.label ?? k);

export type Stance = 'bull' | 'neutral' | 'bear' | 'split' | 'unknown';

/** 論調の表示。split は「割れ」、unknown は「未確認」。中立に丸めない */
export const STANCE: Record<Stance, { label: string; mark: string }> = {
  bull: { label: '強気', mark: '▲' },
  neutral: { label: '中立', mark: '─' },
  bear: { label: '弱気', mark: '▼' },
  split: { label: '割れ', mark: '◐' },
  unknown: { label: '未確認', mark: '' },
};
export const stanceLabel = (s: Stance, lang: Lang = 'ja') =>
  lang === 'en' ? EN_LABELS.stance[s] : STANCE[s].label;

export const RESULT: Record<'hit' | 'partial' | 'miss', string> = {
  hit: '想定どおり',
  partial: '方向は合った',
  miss: '想定と違った',
};
export const resultLabel = (r: 'hit' | 'partial' | 'miss', lang: Lang = 'ja') =>
  lang === 'en' ? EN_LABELS.result[r] : RESULT[r];

export const statusLabel = (s: '確定' | '未確認', lang: Lang = 'ja') =>
  lang === 'en' ? EN_LABELS.status[s] : s;

/**
 * 答え合わせに使う3系列（週次の JSON の key）と閾値。
 * 金・ドル指数は前週比 ±0.5%、米10年は ±5bp。review-world.py と同じ値
 */
export const JUDGE = {
  gold: { key: 'xau', label: '金（XAU/USD）', unit: '%', threshold: 0.5 },
  dollar: { key: 'dxy', label: 'ドル指数 DXY', unit: '%', threshold: 0.5 },
  rates: { key: 'us10y', label: '米10年債利回り', unit: 'bp', threshold: 5 },
} as const;

export interface Actual {
  topic: TopicKey;
  label: string;
  close: number;
  prev: number;
  asof: string;
  prevAsof: string;
  /** 前週比。% か bp */
  move: number;
  unit: '%' | 'bp';
  text: string;
  dir: 'up' | 'down' | 'flat';
}

/** 当週の週次 JSON から、答え合わせに使う3系列の前週比を取る。JSON が無ければ空 */
export function actuals(slug: string, lang: Lang = 'ja'): Actual[] {
  const wd = weeklyData(slug);
  if (!wd) return [];
  const out: Actual[] = [];
  for (const t of TOPICS_W) {
    const j = JUDGE[t.key];
    const a = wd.assets?.find((x) => x.key === j.key);
    if (!a || a.close == null || a.prev == null) continue;
    const move = j.unit === 'bp' ? (a.close - a.prev) * 100 : ((a.close - a.prev) / a.prev) * 100;
    out.push({
      topic: t.key,
      label: lang === 'en' ? EN_LABELS.series[t.key] : j.label,
      close: a.close,
      prev: a.prev,
      asof: a.asof,
      prevAsof: a.prev_asof,
      move,
      unit: j.unit,
      text: signed(move, j.unit === 'bp' ? 0 : 2, j.unit),
      dir: dirOf(move),
    });
  }
  return out;
}

/** 'YYYY-wNN' → 前の週のスラッグ（ISO週。年またぎは直前の木曜から数える） */
export function prevSlug(slug: string): string {
  const m = /^(\d{4})-w(\d{2})$/.exec(slug);
  if (!m) return '';
  const y = Number(m[1]);
  const w = Number(m[2]);
  if (w > 1) return `${y}-w${String(w - 1).padStart(2, '0')}`;
  // 前年の最終週は 12/28 を含む週
  const d = new Date(Date.UTC(y - 1, 11, 28));
  const day = (d.getUTCDay() + 6) % 7;
  d.setUTCDate(d.getUTCDate() - day + 3);
  const first = new Date(Date.UTC(d.getUTCFullYear(), 0, 4));
  const wk = 1 + Math.round(((d.getTime() - first.getTime()) / 86400000 - 3 + ((first.getUTCDay() + 6) % 7)) / 7);
  return `${y - 1}-w${String(wk).padStart(2, '0')}`;
}
