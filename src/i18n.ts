/**
 * 英語版（/en/）の定型文。
 *
 * 日本語が正で、英語は「世界の定点」とサイト紹介だけ（docs/SPEC.md §5「world」の「英語版」）。
 * 記事本文の翻訳は src/content/world-en/ に置き、ここには見出し・ラベル・免責など
 * ページの枠に出る文言だけを持つ。日本語の文言は各コンポーネントの既定値のままにして、
 * lang === 'en' のときだけこの辞書を引く（日本語側の表示を変えないため）。
 */
export type Lang = 'ja' | 'en';

export const LOCALE_PREFIX: Record<Lang, string> = { ja: '', en: '/en' };

export const EN = {
  tagline: 'Reading the market through money flows',
  cadence: 'Weekly',
  skip: 'Skip to content',
  home: 'Home',
  nav: [
    { href: '/en/', label: 'Home' },
    { href: '/en/weekly/', label: 'Weekly Summary' },
    { href: '/en/world/', label: 'World Windows' },
    { href: '/en/about/', label: 'About' },
  ],
  langSwitch: { label: '日本語', title: 'Japanese edition' },
  themeToggle: 'Toggle color scheme',
  /**
   * 免責。日本語の DISCLAIMER の訳に、海外の読者向けの2文（どの国の規制にも服していない、
   * 日本語版が正本）を足している。法的な確認は未了（docs/HANDOVER.md）
   */
  disclaimer:
    'This site provides market information and analysis only. It does not recommend buying or selling any financial product. The publisher is not a registered financial instruments business operator in Japan and is not registered as an investment adviser in Japan or in any other jurisdiction. We take care over accuracy but do not guarantee completeness. Investment decisions are your own responsibility. The English edition is a translation of the Japanese original; where they differ, the Japanese edition prevails.',
  disclaimerHead: 'Disclaimer',
  footer: {
    about: 'About',
    publisher: 'Publisher',
    privacy: 'Privacy policy (Japanese)',
    japanese: 'Japanese edition',
  },
  siteDescription:
    'TEITEN is a Japanese daily market report that reads the market through real yields, the dollar index, commodities and money flows. The English edition carries World Windows: six regional media windows on gold, the dollar and US rates, logged weekly and checked the following week.',
  world: {
    title: 'World Windows',
    lead:
      'Six fixed windows, North America, Europe, Russia, China, India and the Middle East, record how each region’s market media explained gold, the US dollar and US rates in the same week, with the same three questions every week. Readings are logged as bullish, neutral or bearish and checked the following week against the weekly change in gold, the dollar index and the 10-year Treasury yield. A window we could not read is left as unconfirmed, never filled from a nearby outlet.',
    count: (n: number) => `${n} issue${n === 1 ? '' : 's'}`,
    empty: 'No issue of World Windows has been published yet.',
    read: 'Read →',
    week: 'WEEK',
    points: 'This week in brief',
    windows: 'Six windows',
    unconfirmedWindow:
      'No article on any of the three questions this week. Left unconfirmed; not filled from a nearby outlet or a search result.',
    physical: 'Physical',
    distribution: 'Distribution of readings',
    window: 'Window',
    count_: 'Count',
    distNote:
      'Bullish, neutral and bearish are the readings of each window’s outlets. Split means the window’s two outlets pointed in opposite directions; unconfirmed means no article addressed that question.',
    review: 'Last week’s check',
    reviewIssue: (w: string) => `Week ${w} issue →`,
    reviewCols: ['Window', 'Question', 'Last week’s reading', 'Result', 'Note'],
    reviewNote: (hit: number, partial: number, miss: number, n: number) =>
      `As expected ${hit} · direction right ${partial} · not as expected ${miss} (${n} readings). The check is mechanical: ±0.5% week on week for gold and the dollar index, ±5bp for the 10-year yield. Split and unconfirmed readings are not counted.`,
    reviewNoData: ' The weekly data file for this week is missing, so actual values are not shown.',
    weekOnWeek: 'week on week',
    threshold: 'threshold',
    railQuotes: 'The three series checked (week on week)',
    railWeekly: 'Japanese weekly summary, same week',
    railWeeklyMore: 'Weekly summaries →',
    published: 'Published',
    updated: 'Updated',
    editor: 'Editor',
    how: 'How this is observed',
    howText:
      'The six windows and the outlet for each are fixed. Summaries are in our own words; quotations are short and sourced. A window we could not read is left unconfirmed, never filled from a nearby outlet or a search result. Readings are checked the following week, mechanically: ±0.5% week on week for gold and the dollar index, ±5bp for the 10-year Treasury yield. No figures are copied from the articles; values come from the same series as the Japanese weekly summary.',
    translated: 'Translated from the Japanese edition. Where they differ, the Japanese edition prevails.',
    original: 'Japanese original →',
  },
  en_index: {
    title: 'TEITEN, English edition',
    lead:
      'TEITEN (定点, “fixed point”) is a Japanese market report published by Financial and Marketing M16. Every weekday it reads the market through the same indicators, in the same format, and every week it checks what it said. The English edition carries one section for now: World Windows.',
    latest: 'Latest World Windows',
    all: 'All issues →',
    aboutLink: 'About this site →',
    jaNote: 'The daily and weekly reports are in Japanese only.',
  },
} as const;

/**
 * 週次まとめの英語版（/en/weekly/）で使う文言。
 *
 * 記事側（title / deck / points / performance の note など）は `src/content/weekly-en/` で訳す。
 * ここに置くのはページ部品の文言と、`src/data/weekly/<slug>.json` から描く系列の名前。
 * **JSON は日本語のまま**（`fetch-weekly.py` が書く取得値の原本で、言語ごとに持たない）なので、
 * 英語ページは日本語のラベルをこの表で引き直す。表に無いラベルは日本語のまま出す（欠けても描画は壊さない）。
 */
export const EN_WEEKLY = {
  title: 'Weekly Summary',
  lead:
    'A week of daily reports, re-read as movements of money rather than as separate price moves: what happened, and where next week turns. Figures come from the same fixed series as the Japanese edition.',
  count: (n: number) => `${n} issue${n === 1 ? '' : 's'}`,
  empty: 'No weekly summary has been published in English yet.',
  week: 'WEEK',
  points: 'This week in brief',
  performance: 'Weekly performance by asset',
  instruments: (n: number) => `${n} instruments`,
  other: 'Other',
  /** src/lib/weekly.ts の GROUPS のキー */
  groups: {
    metals: 'Precious metals',
    rates: 'Rates',
    fx: 'FX',
    commodities: 'Commodities',
    equities: 'Equities',
    crypto: 'Crypto',
    vol: 'Volatility',
    credit: 'Credit',
  } as Record<string, string>,
  unconfirmed: 'Unconfirmed',
  reading: 'Reading',
  readingTitle: 'An intraday or partial figure, not a closing value',
  ratios: 'Ratios of the week',
  lastWeeks: (n: number) => `last ${n} weeks`,
  range: 'range',
  ratiosSrc:
    'All ratios are COMEX front-month futures: gold (GC=F) against silver (SI=F), WTI crude (CL=F) and copper (HG=F, USD per pound), taken from the last trading day of each week (Yahoo Finance). In a week when the front month rolls, the ratio spans two contracts.',
  flows: 'Positioning and flows',
  fomc: 'What the market prices for the FOMC',
  meeting: 'meeting',
  hikesOf: (dir: 'hike' | 'cut', n: string) => `${n} moves of 0.25% (${dir})`,
  fomcSrc: (effr: string, asof: string) =>
    `The policy rate implied after each meeting, derived from fed funds futures (CBOT). The starting point is the effective fed funds rate of ${effr}% (${asof}, FRED EFFR). This follows the same method as CME FedWatch but is not FedWatch's own figure.`,
  cot: 'CFTC positioning (net speculative, 4 weeks)',
  wow: 'week on week',
  cotSrc:
    'CFTC Commitments of Traders. Positions as of Tuesday, published on Friday. Gold, silver and crude are managed money; the yen is leveraged funds. Units are contracts.',
  etf: 'ETF flows',
  btcEtf: 'US spot bitcoin ETFs (total)',
  millionUsd: 'm',
  notTallied: 'not yet tallied',
  missing: 'Unconfirmed:',
  correlation: 'Weekly correlation',
  corrWords: {
    none: 'little relation',
    weakPos: 'weakly positive',
    weakNeg: 'weakly negative',
    pos: 'positive',
    neg: 'negative',
  },
  corrSrc: (base: string, source: string) =>
    `Correlation between ${base} and the weekly change in each indicator (bp for the real yield, percent for the rest). −1 means they moved in opposite directions, +1 that they moved together. Eight weeks is a short window and one large week can flip the sign. It does not show causation. ${source}`,
  ranges: 'Weekly ranges',
  high: 'High',
  low: 'Low',
  span: 'Range',
  openClose: 'Open',
  rangesSrc:
    'Yahoo Finance (gold and silver are COMEX front-month futures, daily; USD/JPY is hourly, cut at 17:00 New York). Levels differ slightly from spot gold (USAGOLD).',
  ladder: 'Technical levels',
  ladderAt: (asset: string) => `Technical levels: ${asset}`,
  ladderWeek: 'Technical levels (week end)',
  kind: { resistance: 'Resistance', current: 'Last', support: 'Support' },
  scenarios: 'Scenarios for next week',
  cases: (n: number) => `${n} cases`,
  caseName: { bull: 'Bull Case', base: 'Base Case', bear: 'Bear Case' },
  caseJa: { bull: 'Upside', base: 'Base', bear: 'Downside' },
  target: 'Price target',
  schedule: 'Key events next week',
  starNote: '★ is the one to watch',
  mostImportant: 'Most important',
  bias: 'Market Bias (next week)',
  railNumbers: 'Figures of the week',
  railDaily: 'Daily reports in this week',
  railDailyMore: 'Archive (Japanese) →',
  dailyJa: 'The daily reports behind this summary are published in Japanese only.',
  snapshot: 'Market snapshot',
} as const;

/**
 * `src/data/weekly/<slug>.json` に入っている日本語のラベルを英語に引き直す表。
 * JSON は言語ごとに持たないので、ここが唯一の対応表になる。
 */
export const EN_SERIES: Record<string, string> = {
  // 週足のレンジ・相関・建玉の銘柄
  '金（COMEX 先物）': 'Gold (COMEX futures)',
  '銀（COMEX 先物）': 'Silver (COMEX futures)',
  '金（COMEX）': 'Gold (COMEX)',
  '銀（COMEX）': 'Silver (COMEX)',
  'WTI原油（NYMEX）': 'WTI crude (NYMEX)',
  '円（CME）': 'Japanese yen (CME)',
  'USD/JPY': 'USD/JPY',
  '実質金利（TIPS10年）': 'Real yield (10-year TIPS)',
  'ドル指数 DXY': 'Dollar index (DXY)',
  'Nasdaq総合': 'Nasdaq Composite',
  'BTC/USD': 'BTC/USD',
  // 建玉の主体
  'マネージド・マネー': 'Managed money',
  'レバレッジド・ファンド': 'Leveraged funds',
  // 相関の基準と出典
  '金（COMEX 先物 GC=F）の週間変化率': 'the weekly change in gold (COMEX futures, GC=F)',
  '算出：Yahoo Finance・FRED DFII10・CoinGecko。各週の最後の取引日どうしの変化':
    'Derived from Yahoo Finance, FRED DFII10 and CoinGecko, comparing the last trading day of each week.',
};

/** レシオの名前と説明。キーは JSON の `key` */
export const EN_RATIOS: Record<string, { label: string; gloss: string }> = {
  gold_silver: {
    label: 'Gold/silver',
    gloss: 'How many ounces of silver one ounce of gold buys. A rising week points to fear buying, a falling week to buying across commodities.',
  },
  gold_oil: {
    label: 'Gold/oil',
    gloss: 'How many barrels of crude one ounce of gold buys. A rising week points to worries about growth, a falling week to inflation or supply.',
  },
  gold_copper: {
    label: 'Gold/copper',
    gloss: 'Gold against copper, the proxy for the economy. A rising week points to worries about growth, a falling week to confidence in it.',
  },
};

/** JSON の日本語ラベルを言語に合わせて返す。表に無ければ日本語のまま */
export const seriesLabel = (label: string, lang: Lang = 'ja') =>
  lang === 'en' ? (EN_SERIES[label] ?? label) : label;

/** 窓の地域名・論点・論調・判定の英語表記 */
export const EN_LABELS = {
  region: { na: 'North America', eu: 'Europe', ru: 'Russia', cn: 'China', in: 'India', me: 'Middle East' } as Record<string, string>,
  topic: { gold: 'Gold', dollar: 'Dollar', rates: 'US rates' } as Record<string, string>,
  topicShort: { gold: 'Gold', dollar: 'USD', rates: 'Rates' } as Record<string, string>,
  stance: { bull: 'Bullish', neutral: 'Neutral', bear: 'Bearish', split: 'Split', unknown: 'Unconfirmed' } as Record<string, string>,
  result: { hit: 'As expected', partial: 'Direction right', miss: 'Not as expected' } as Record<string, string>,
  status: { 確定: 'Confirmed', 未確認: 'Unconfirmed' } as Record<string, string>,
  series: { gold: 'Gold (XAU/USD)', dollar: 'Dollar index (DXY)', rates: '10-year Treasury yield' } as Record<string, string>,
};
