/**
 * 週次まとめの機械取得データ（src/data/weekly/<slug>.json）と、表示用の補助。
 *
 * JSON は `tools/fetch-weekly.py --write` が書く。**手で書き換えない。**
 * frontmatter の performance は寸評が要るので記事側に置き、レシオ・建玉・フロー・相関は
 * この JSON から直接描く。同じ数字を2か所に書くと、片方だけ直した号が出るため。
 *
 * JSON が無い週（W38 以前など）は、その節を出さない。
 */

export type Status = '確定' | '読み取り' | '未確認';

export interface RatioHist { week_end: string; value: number }
export interface Ratio {
  key: string;
  label: string;
  digits: number;
  gloss: string;
  value: number | null;
  prev: number | null;
  history: RatioHist[];
  source: string;
}
export interface Range {
  label: string;
  high?: number;
  low?: number;
  open?: number;
  close?: number;
  digits?: number;
  source?: string;
  status?: Status;
}
export interface Cot {
  label: string;
  who: string;
  history: { date: string; net: number }[];
  status: Status;
  source?: string;
}
export interface WeeklyData {
  slug: string;
  start: string;
  end: string;
  fetched: string;
  ratios: Ratio[];
  ranges: Range[];
  cot: Cot[];
  btc_etf: { status: Status; total?: number; note?: string; source?: string; days: { date: string; flow: number | null }[] };
  fedwatch: {
    status: Status;
    effr?: number;
    effr_asof?: string;
    source?: string;
    meetings: { meeting: string; contract: string; pre: number; post: number; move_bp: number; hikes: number }[];
  };
  correlation: {
    status: Status;
    window?: number;
    base?: string;
    source?: string;
    pairs: { label: string; r: number | null; n: number; unit: string }[];
  };
}

const files = import.meta.glob<WeeklyData>('../data/weekly/*.json', { eager: true, import: 'default' });

export function weeklyData(slug: string): WeeklyData | undefined {
  return files[`../data/weekly/${slug}.json`];
}

/** グループの並びと見出し。ハンドオフ（2026-10-26）の構成案の順 */
export const GROUPS = [
  { key: 'metals', label: '貴金属' },
  { key: 'rates', label: '金利' },
  { key: 'fx', label: '為替' },
  { key: 'commodities', label: '商品' },
  { key: 'equities', label: '株' },
  { key: 'crypto', label: 'Crypto' },
  { key: 'vol', label: 'Vol' },
  { key: 'credit', label: 'クレジット' },
] as const;
export type GroupKey = (typeof GROUPS)[number]['key'];

/**
 * group の無い行（W43 までの週次）を label から振り分ける。
 * 当てはまらなければ undefined（グループ見出しの外にそのまま並べる）
 */
export function inferGroup(label: string): GroupKey | undefined {
  if (/金|銀|プラチナ|XAU|XAG|XPT/.test(label) && !/金利/.test(label)) return 'metals';
  if (/利回り|金利|BEI|スプレッド|国債|債/.test(label) && !/HY/.test(label)) return 'rates';
  if (/DXY|ドル指数|USD\/JPY|EUR\/USD|ドル円|ユーロ/.test(label)) return 'fx';
  if (/原油|WTI|Brent|銅/.test(label)) return 'commodities';
  if (/S&P|Nasdaq|ダウ|日経225|日経平均|株/.test(label)) return 'equities';
  if (/BTC|ビットコイン/.test(label)) return 'crypto';
  if (/VIX|日経VI|MOVE/.test(label)) return 'vol';
  if (/HY|ハイイールド/.test(label)) return 'credit';
  return undefined;
}

/** 記事の書式の符号つき数値（全角のマイナス） */
export function signed(x: number, digits: number, unit = ''): string {
  const s = Math.abs(x).toLocaleString('en-US', { minimumFractionDigits: digits, maximumFractionDigits: digits });
  if (Number(s.replace(/,/g, '')) === 0) return `±${s}${unit}`;
  return `${x > 0 ? '+' : '−'}${s}${unit}`;
}

export function fixed(x: number, digits: number): string {
  return x.toLocaleString('en-US', { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

export const dirOf = (x: number): 'up' | 'down' | 'flat' => (x > 0 ? 'up' : x < 0 ? 'down' : 'flat');
