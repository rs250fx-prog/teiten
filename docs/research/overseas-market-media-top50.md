# 海外のFX・マーケット情報メディア TOP50（AIで収集できるもの）

調査日：2026-10-30（同日に再構築）
目的：TEITEN の肉付けに使う海外メディアを、**ルーティン（AI）が実際に取りに行ける**ことを条件に、地域が偏らないように揃える。

---

## 1. 選び方

- **収集可否が第一条件**：Claude Code の WebFetch で見出しと日時が取れたものだけを載せる。取れなかった媒体は §4 に理由つきで残す
- **流入数**：Similarweb の 2026年9月推定。順位はグローバル順位、訪問数は月間
- **更新頻度**：24h（ワイヤー・速報）／日中随時／平日毎日
- **専門性**：相場・金利・為替・商品を扱う「市場専門」を優先。一般紙は各地域の代表に留める
- **地域バランス**：米6・加2・英6・欧州大陸13・ロシア5・アジア太平洋10・中東アフリカ5・中南米3

### 数字の注意

- 一般紙系（Il Sole 24 Ore、El Cronista、Fin24 など）の訪問数は**サイト全体**の数字。マーケット面だけの流入ではない
- Similarweb は推定値。再調査するなら同じ月で揃えて比べる
- 「順位」列は 50本をグローバル順位で通しで並べたもの。ING Think はサブドメインで順位が無く、訪問数で位置を決めた
- **収集可否は 2026-10-30 の手元環境の結果**。ルーティン（クラウド）も同系統のツールだが、ブロックの挙動は変わりうる。本番に組み込む前に、使う分だけ同じ方法で再確認する

### 2024〜2026 の現状変化（古いランキングは反映していない）

- **DailyFX は 2024-09-04 に閉鎖**。IG のサイトにリダイレクト
- **ForexLive は 2025-07-21 に investingLive へ改名**。旧ドメインは転送
- **Forex Crunch は事実上休眠**。FX記事は2026年1月が最後。除外

---

## 2. TOP50（地域別）

「取り方」はこの日に実際に読めた URL と方式。HTML はページそのもの、RSS／JSON は機械向けの配信。

### グローバル・北米（米6／加2）

| 順位 | メディア | 拠点 | 月間訪問 | 更新 | 取り方 | 強み・TEITENでの使いどころ |
|---|---|---|---|---|---|---|
| 1 | TradingView | 米 | 2.3億 | 24h | HTML `tradingview.com/news/` | ニュース集約（Reuters 配信を含む）。金・DXY・MOVE の図版確認 |
| 5 | Forex Factory | 米 | 3,630万 | 24h | JSON `nfs.faireconomy.media/ff_calendar_thisweek.json` | 経済指標カレンダーの標準。公式の週間JSONで予想・前回が取れる |
| 9 | Trading Economics | 米 | 2,490万 | 随時 | HTML `tradingeconomics.com/calendar` | 指標の実績・予想・コンセンサスが表で取れる。週次25銘柄の裏取りに |
| 13 | ZeroHedge | 米 | 1,610万 | 24h | HTML `zerohedge.com/markets` | 資金フロー・ポジショニングの論点が早い。偏りは強いので裏取り必須 |
| 24 | Kitco News | 加 | 1,110万 | 日中随時 | HTML `kitco.com/news` | 金・銀・プラチナ専門。中銀購入・ETFフロー・現物需給の定番 |
| 31 | CoinDesk | 米 | 290万 | 24h | HTML `coindesk.com/markets/` | BTC現物ETFフローの一次報道。暗号資産欄に |
| 38 | investingLive 旧ForexLive | 加 | 順位#67,734 | 24h | HTML `investinglive.com/` | FX実況コメントの最古参。PBOC基準値・オーダー・レベル感 |
| 49 | MarketPulse（OANDA） | 米/加 | 4万 | 平日毎日 | HTML `marketpulse.com/` | 主要通貨ペアのテクニカル日報。流入は小さいが更新が安定 |

### 英国（6）

| 順位 | メディア | 拠点 | 月間訪問 | 更新 | 取り方 | 強み・使いどころ |
|---|---|---|---|---|---|---|
| 12 | Oilprice.com | 英 | 1,970万 | 日中随時 | HTML `oilprice.com/Latest-Energy-News/World-News/` | 原油・エネルギー専門。金原油レシオの背景に |
| 25 | IG Insights | 英 | 830万 | 日中随時 | HTML `ig.com/en/news-and-trade-ideas` | 旧DailyFXの受け皿。英・豪・星の多拠点 |
| 36 | BullionVault | 英 | 150万 | 平日毎日 | HTML `bullionvault.com/gold-news/` | 金の現物市場の視点。LBMA・現物プレミアムの解説 |
| 41 | World Gold Council Goldhub | 英 | 65万 | 週次〜 | HTML `gold.org/goldhub` | 中銀購入・ETFフロー・需給の一次統計。月次・四半期の定点に |
| 44 | Pound Sterling Live | 英 | 18万 | 平日毎日 | HTML `poundsterlinglive.com/` | 大手銀行のFXリサーチを要約。GBP・EUR中心 |
| 46 | Newsquawk | 英 | 10万 | 06:30〜22:00ロンドン＋アジア | HTML `newsquawk.com/headlines`（無料の見出し） | プロ向けスクワークの見出しが無料で読める。DXY・米債の動意を分単位で |

### 欧州大陸（13）

| 順位 | メディア | 拠点 | 月間訪問 | 更新 | 取り方 | 強み・使いどころ |
|---|---|---|---|---|---|---|
| 2 | Investing.com | キプロス | 1.33億 | 24h | HTML `investing.com/news/forex-news` | 40言語超の総合ポータル。**Reuters 配信記事がここで読める** |
| 7 | Il Sole 24 Ore | 伊 | 3,120万 | 24h | HTML `ilsole24ore.com/sez/finanza` | Radiocor の速報フィード。BTP・ECB |
| 8 | Boursorama | 仏 | 2,150万 | 24h | HTML `boursorama.com/bourse/actualites/` | フランス最大の投資ポータル。Reuters 仏語配信を含む |
| 10 | Bankier.pl | ポーランド | 1,920万 | 24h | HTML `bankier.pl/wiadomosc/` | 中欧最大の金融ポータル。PLN・中東欧の金利 |
| 11 | Bloomberg HT | トルコ | 1,560万 | 24h | HTML `bloomberght.com/piyasalar` | トルコ語の Bloomberg 系。TRY・新興国リスクの現地感 |
| 14 | Handelsblatt | 独 | 1,530万 | 24h | HTML `handelsblatt.com/finanzen/`（日時なし） | ドイツの経済紙。ECB・Bund・独銀行 |
| 20 | Expansión | 西 | 850万 | 24h | RSS `e00-expansion.uecdn.es/rss/mercados.xml` | スペインの経済紙。欧州債・ECB |
| 21 | XTB | ポーランド | 800万 | 日中随時 | HTML `xtb.com/en/market-analysis` | 中欧最大のブローカー研究。FX・商品の日次まとめ |
| 28 | cash.ch | スイス | 360万 | 日中随時 | HTML `cash.ch/news` | CHF・SNB・金のスイス精錬動向 |
| 32 | stock3 旧GodmodeTrader | 独 | 260万 | 日中随時 | HTML `stock3.com/news` | ドイツ語圏テクニカル分析の本拠。金・DAX・EURUSD の水準 |
| 34 | FXStreet | 西 | 約200万 | 24h | HTML `fxstreet.com/news` | FX専門。指標速報・テクニカル・銀行見解の引用 |
| 37 | Saxo SaxoStrats | デンマーク | 順位#60,435 | 平日毎日 | HTML `home.saxo/insights/news-and-research` | 商品・FX・金利のストラテジスト解説。「The FX Trader」が定期 |
| 43 | ING Think | 蘭 | 26万 | 平日毎日 | HTML `think.ing.com/` | 銀行FXリサーチで最も読まれる無料媒体。「FX Daily」「Rates Spark」 |

### ロシア・CIS（5）

| 順位 | メディア | 拠点 | 月間訪問 | 更新 | 取り方 | 強み・使いどころ |
|---|---|---|---|---|---|---|
| 18 | Interfax | 露 | 960万 | 24h | HTML `interfax.ru/business/` | ロシアの経済ワイヤー。中銀・財務省・原油輸出の公式発表 |
| 19 | Finam | 露 | 860万 | 日中随時 | RSS `finam.ru/analysis/conews/rsspoint/` | 証券会社系の分析とニュース。ロシア株・RUB |
| 22 | ProFinance.ru | 露 | 1,120万 | 24h | HTML `profinance.ru/news/` | FX専門。Reuters・Bloomberg の為替コメントをロシア語で速報。金も厚い |
| 23 | Smart-Lab | 露 | 720万 | 24h | HTML `smart-lab.ru/` | 個人投資家コミュニティ。現地の肌感・ポジショントーク |
| 39 | Прайм（1prime.ru） | 露 | 86万 | 24h | HTML `1prime.ru/` | RIA 系の経済通信。EU 制裁・穀物・エネルギーの速報 |

### アジア太平洋（10）

| 順位 | メディア | 拠点 | 月間訪問 | 更新 | 取り方 | 強み・使いどころ |
|---|---|---|---|---|---|---|
| 3 | 東方財富 Eastmoney | 中 | 6,020万 | 24h | HTML `finance.eastmoney.com/` | 中国最大の投資ポータル。人民元・上海金・A株 |
| 6 | Goodreturns | 印 | 4,970万 | 毎日 | HTML `goodreturns.in/gold-rates/` | **インドの金小売価格（22K/24K）を日付つきで取れる**。インド現物需要の定点に |
| 17 | South China Morning Post | 香港 | 1,130万 | 24h | HTML `scmp.com/business` | 香港・中国の企業・市場。英語 |
| 26 | Business Today | 印 | 480万 | 24h | HTML `businesstoday.in/markets` | インド市場面。Sensex・INR・RBI |
| 27 | 華爾街見聞 Wallstreetcn | 中 | 420万 | 24h | HTML `wallstreetcn.com/news/global` | 中国語のマクロ専門。米中金利・資金フロー。朝の「早餐FM」 |
| 30 | Pepperstone | 豪 | 160万 | 平日毎日 | HTML `pepperstone.com/en/market-analysis/` | 豪州ブローカー研究。AUD・決算・マクロ |
| 40 | 汇通財経 FX678 | 中 | 81万 | 24h | HTML `news.fx678.com/` | 中国語FX・貴金属専門。18通貨ペアと商品のサポレジ表が毎日出る |
| 45 | Caixin Global | 中 | 16万 | 日中随時 | HTML `caixinglobal.com/finance/` | 財新の英語版。中国金融の独立系報道 |
| 48 | Action Forex | 香港 | 順位#550,598 | 日中随時 | HTML `actionforex.com/` | 通貨ペア別のテクニカルと市場概況。GMT 時刻つき |
| 50 | Westpac IQ | 豪 | 3万 | 平日毎日 | HTML `westpaciq.com.au/economics`（一部は顧客限定） | 豪銀行の「Morning Report」「ForeX Focus」。AUD・RBA |

### 中東・アフリカ（5）

| 順位 | メディア | 拠点 | 月間訪問 | 更新 | 取り方 | 強み・使いどころ |
|---|---|---|---|---|---|---|
| 16 | Fin24 | 南ア | 1,280万（news24全体） | 日中随時 | HTML `news24.com/fin24/markets` | ZAR・SARB・金鉱株。「Rand firms after Fed…」型の日次 |
| 29 | Argaam | サウジ | 290万 | 24h | HTML `argaam.com/en` | 湾岸最大の市場メディア。原油・中東資金 |
| 33 | Moneyweb | 南ア | 220万 | 日中随時 | RSS `moneyweb.co.za/feed/` | ZAR・プラチナ族金属。SARB の物価目標 |
| 42 | Zawya | UAE | 34万 | 日中随時 | HTML `zawya.com/en/markets`（日付なし） | LSEG 系の英語媒体。湾岸の債券・SWF |
| 47 | Economies.com | ヨルダン | 10万 | 日中随時 | HTML `economies.com/` | アラブ圏向けのFX・金テクニカル。英語・アラビア語 |

### 中南米（3）

| 順位 | メディア | 拠点 | 月間訪問 | 更新 | 取り方 | 強み・使いどころ |
|---|---|---|---|---|---|---|
| 4 | El Cronista | アルゼンチン | 5,650万 | 24h | HTML `cronista.com/finanzas-mercados/` | ARS・カントリーリスク・BCRA。アルゼンチン最大級 |
| 15 | InfoMoney | ブラジル | 1,270万 | 24h | HTML `infomoney.com.br/mercados/` | ブラジル最大の投資メディア。BRL・Selic・DI金利 |
| 35 | Bloomberg Línea | メキシコ/中南米 | 160万 | 24h | HTML `bloomberglinea.com/mercados/` | 中南米横断のスペイン語。格付け・MXN・中米 |

---

## 3. 内訳と、読めたが外したもの

地域の内訳：米6・加2・英6・欧州大陸13・ロシア5・アジア太平洋10・中東アフリカ5・中南米3（計50）。

読めたが 50 に入れなかったもの（必要なら差し替え候補）：

| メディア | 理由 |
|---|---|
| DailyForex（イスラエル） | 「Forex Today」日報は読めるが FXStreet と重なる |
| FXEmpire（イスラエル） | 読めるが一覧に古い記事が並び、更新の鮮度が確認できなかった |
| Finance Magnates（イスラエル） | 業界ニュース（ブローカー・規制）。相場の肉付けには向かない |
| Yicai Global（中） | 読めるが流入が小さい（6万）。Caixin Global と重なる |
| Kommersant 金融面（露） | 読める。ロシアは5本で足りるため外した |
| RBC（露） | 本体は 401。RSS `rssexport.rbc.ru/rbcnews/news/30/full.rss` は一般ニュース混在で市場向きでない |
| Gulf News 市場面（UAE） | 読める。Zawya・Argaam と重なる |

---

## 4. 取れなかった媒体（2026-10-30）

| 媒体 | 結果 | 代替 |
|---|---|---|
| Reuters | ドメイン単位で fetch 不可 | **Investing.com・TradingView・Boursorama に配信記事が載る**。検索でも拾える |
| Bloomberg | 403 | 見出しは検索で。Bloomberg HT（トルコ語）・Bloomberg Línea（西語）は読める |
| WSJ・FT | fetch 不可（RSS も不可） | 見出しは検索で |
| CNBC | 403（RSS も 403） | TradingView・Investing.com |
| finanzen.net | 403（RSS も 403） | Handelsblatt・stock3 |
| MarketScreener | ログイン壁 | Boursorama |
| Les Echos | fetch 不可 | Boursorama |
| Ámbito・El Economista（MX）・Valor | 403／fetch 不可 | El Cronista・Bloomberg Línea・InfoMoney |
| Moneycontrol・ET Markets・Mint・BusinessLine・Financial Express・NDTV Profit | fetch 不可 | Business Today・Goodreturns |
| Zee Business | 402 | 同上 |
| AFR・Business Times（SG）・CNA・The Edge（SG/MY） | fetch 不可／403／JS描画 | Pepperstone・Westpac IQ・SCMP |
| MacroMicro | 403 | Trading Economics |
| Jin10（金十数据） | JS描画で空 | FX678・Wallstreetcn |
| FinancialJuice | JS描画で空 | Newsquawk の無料見出し・investingLive |
| BCS Express | 本文が空 | Finam・ProFinance |
| Business Standard・Brecorder・Mubasher | 403 | Investing.com（Reuters 配信） |

---

## 5. 使うときの決まり

- **要約は自分の言葉で書き、引用は短く、出典リンクを付ける。**翻訳の転載はしない
- **数値は `SOURCES.md` の系列から取る。**媒体の記事は値動きの理由と裏取りに使う。例外は Goodreturns（インド金小売価格）と Forex Factory の JSON（指標予想）で、使うなら SOURCES.md に系列として登録してから
- 1回の実行で fetch するのは 6〜8 本まで。多言語の要約は翻訳ずれが起きるので、固有名詞と数字は原文を残す
- 相対時刻（「2 hours ago」「Вчера」）しか出ない媒体は、記事URLの日付で確定させる

### まず常用する6つ（地域の窓）

| 窓 | メディア | 役割 |
|---|---|---|
| 北米 | Kitco News・investingLive | 金の現物需給／FXの実況 |
| 欧州 | ING Think・FXStreet | 銀行の見通し／指標速報 |
| ロシア | ProFinance.ru | ロシア語圏の為替・金速報 |
| 中国 | FX678（汇通財経） | 中国側の金・為替速報 |
| インド | Goodreturns | 金小売価格の定点 |
| 中東 | Argaam | 湾岸の資金と原油 |

---

## 6. 出典

- Feedspot: Top 20 Forex News Websites in 2026 https://news.feedspot.com/forex_news_websites/
- Feedspot: 100 Best Forex Blogs in 2026 https://bloggers.feedspot.com/forex_blogs/
- Finance Magnates: IG Group Redirects DailyFX Website（2024-09-04） https://www.financemagnates.com/forex/ig-group-redirects-daily-fx-website-launches-trade-live-with-ig-morning-show/
- IG: DailyFX – now get your trading insights on IG https://www.ig.com/sg/trading-strategies/dailyfx--now-get-your-trading-insights-on-ig-240906
- FXStreet: ForexLive Rebrands as investingLive（2025-07-21） https://www.fxstreet.com/press-releases/forexlive-rebrands-as-investinglive-to-reflect-broader-market-coverage-202507210959
- Similarweb 各サイトページ（2026年9月） https://www.similarweb.com/website/fxstreet.com/competitors ほか
- Forex Factory 公式カレンダー配信 https://nfs.faireconomy.media/ff_calendar_thisweek.json
- 収集可否は 2026-10-30 に Claude Code の WebFetch で各URLを実際に取得して判定
