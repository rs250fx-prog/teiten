// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { unified } from '@astrojs/markdown-remark';
import fs from 'node:fs';
import path from 'node:path';
import { IS_PUBLIC, SITE_URL, TOPICS } from './src/config.ts';
import { remarkStrongFix } from './src/remark-strong-fix.mjs';
import { remarkFlow } from './src/remark-flow.mjs';
import { remarkFigures } from './src/remark-figures.mjs';
import { rehypeExternalLinks } from './src/rehype-external-links.mjs';

/**
 * frontmatter で unlisted: true が指定された記事は、サイトマップからも除外する。
 * ページ側の noindex と同じ指定が効くよう、frontmatter を唯一の情報源にする。
 * （載せたまま noindex にすると Search Console でエラーになる）
 */
function unlistedPaths(dir, prefix) {
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith('.md') && !f.startsWith('_'))
    .filter((f) => {
      const fm = fs.readFileSync(path.join(dir, f), 'utf-8').split('---')[1] ?? '';
      return /^unlisted:\s*true\s*$/m.test(fm);
    })
    .map((f) => `${prefix}/${f.replace(/\.md$/, '')}`);
}

/**
 * TOPICS に説明文を用意したトピックは記事が0件でもページが立ち、そのあいだは noindex になる
 * （src/pages/topics/[tag].astro）。同じ条件でサイトマップからも外す。
 * スラッグの作り方は src/lib/content.ts の tagSlug と同じ
 */
function emptyTopicPaths() {
  const slug = (t) => t.trim().toLowerCase().replace(/[\/\\\s]+/g, '-').replace(/[?#%&]/g, '');
  const used = new Set();
  for (const dir of ['./src/content/reports', './src/content/weekly']) {
    if (!fs.existsSync(dir)) continue;
    for (const f of fs.readdirSync(dir).filter((x) => x.endsWith('.md') && !x.startsWith('_'))) {
      const fm = fs.readFileSync(path.join(dir, f), 'utf-8').split('---')[1] ?? '';
      if (/^draft:\s*true\s*$/m.test(fm)) continue;
      const m = fm.match(/^tags:\s*\[(.*)\]\s*$/m);
      for (const t of m ? m[1].matchAll(/"([^"]+)"/g) : []) used.add(slug(t[1]));
    }
  }
  return Object.keys(TOPICS)
    .map(slug)
    .filter((s) => !used.has(s))
    .map((s) => `/topics/${s}`);
}

// 管理画面はサイトマップに載せない。恒久 noindex なので、
// 載せると Search Console がエラーを出す
const ALWAYS_EXCLUDED = ['/admin'];

const excluded = [
  ...ALWAYS_EXCLUDED,
  ...unlistedPaths('./src/content/reports', '/reports'),
  ...unlistedPaths('./src/content/weekly', '/weekly'),
  ...emptyTopicPaths(),
];

export default defineConfig({
  site: SITE_URL,
  // 本公開前はサイトマップを出さない（全ページ noindex のため）
  integrations: IS_PUBLIC
    ? [
        sitemap({
          filter: (page) =>
            !excluded.includes(decodeURIComponent(new URL(page).pathname).replace(/\/$/, '')),
          // lastmod を出さないと Search Console が更新日を推定できない
          lastmod: new Date(),
          changefreq: 'daily',
          priority: 0.7,
        }),
      ]
    : [],
  // Astro 7 の既定の Markdown 処理（Sätteri）は remark/rehype プラグインを通さないため、
  // 従来の unified の処理系を明示して使う
  markdown: {
    processor: unified({
      // 日本語で閉じられなかった強調記号を救済してから、フロー変換にかける。
      // 順序が逆だと、残ったアスタリスクがフロー表示へそのまま出る
      // 日次レポートの節の頭に図を足す（frontmatter の infographic と過去の号の snapshot から）
      remarkPlugins: [remarkStrongFix, remarkFlow, remarkFigures],
      // 本文の外部リンクに target と rel を一括付与する
      rehypePlugins: [rehypeExternalLinks],
    }),
  },
});
