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
