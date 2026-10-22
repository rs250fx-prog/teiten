import { Env, toItem, json, BRANCH, REPO_DEFAULT } from '../_lib';

/**
 * 記事の一覧を返す。GitHub 上の実体を読むので、ローカルのクローンは不要。
 *
 * Worker の subrequest は1リクエストあたりの回数に上限がある（無料枠は50回）。
 * 1件ずつ REST で取ると記事数に比例して増え、上限で落ちる。
 * GraphQL なら2ディレクトリ分の本文を**1回**でまとめて取れるので、
 * 記事が増えても呼び出し回数は変わらない。
 */
const LIMIT = 40;

const QUERY = `
query($owner: String!, $name: String!, $daily: String!, $weekly: String!) {
  repository(owner: $owner, name: $name) {
    daily: object(expression: $daily) { ...tree }
    weekly: object(expression: $weekly) { ...tree }
  }
}
fragment tree on Tree {
  entries { name path type object { ... on Blob { text isTruncated } } }
}`;

interface Entry {
  name: string;
  path: string;
  type: string;
  object?: { text?: string; isTruncated?: boolean } | null;
}

export const onRequestGet: PagesFunction<Env> = async (ctx) => {
  try {
    if (!ctx.env.GITHUB_TOKEN) throw new Error('GITHUB_TOKEN が未設定です');
    const [owner, name] = (ctx.env.GITHUB_REPO || REPO_DEFAULT).split('/');

    const res = await fetch('https://api.github.com/graphql', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${ctx.env.GITHUB_TOKEN}`,
        'Content-Type': 'application/json',
        'User-Agent': 'teiten-admin',
      },
      body: JSON.stringify({
        query: QUERY,
        variables: {
          owner,
          name,
          daily: `${BRANCH}:src/content/reports`,
          weekly: `${BRANCH}:src/content/weekly`,
        },
      }),
    });
    if (!res.ok) {
      throw new Error(`GitHub ${res.status}: ${(await res.text()).slice(0, 300)}`);
    }
    const out: any = await res.json();
    if (out.errors?.length) {
      throw new Error(`GitHub GraphQL: ${JSON.stringify(out.errors).slice(0, 300)}`);
    }

    // ディレクトリが無い場合は null
    const repo = out.data?.repository ?? {};
    const files: Entry[] = [
      ...(repo.daily?.entries ?? []),
      ...(repo.weekly?.entries ?? []),
    ].filter((e: Entry) => e.type === 'blob' && e.name.endsWith('.md')
      && !e.name.startsWith('_') && e.object?.text != null);

    files.sort((a, b) => (a.path < b.path ? 1 : a.path > b.path ? -1 : 0));
    const targets = files.slice(0, LIMIT);

    const items = targets.map((e) => toItem(e.path, e.object!.text!));
    items.sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0));
    return json({ ok: true, items, truncated: files.length > LIMIT });
  } catch (e: any) {
    return json({ ok: false, message: e.message }, 500);
  }
};
