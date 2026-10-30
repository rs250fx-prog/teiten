---
# 「世界の定点」サンプル記事（第44週）。SPEC §5「world」の形式の試作。
# 2026-10-30（金）JST 午前に作成。金曜の米国セッションは未了で、正式号は土曜 14:00 の実行で作る。
# ビルド対象外（docs/research/ に置く）。段階1なので論調の層だけ。現物の層は末尾に「試し取り」として参考に載せた。
year: 2026
week: 44
title: 世界の定点 第44週：利上げ観測で金は4,000ドル攻防、ドルは「もう上がらない」という読みが欧州から
deck: 6つの窓のうち5つが金に弱気。ドルの読みは割れ、北米と欧州は「利回り低下で上値が重い」、中国は「高止まり」。インドは論調が取れず未確認。
start: 2026-10-26
end: 2026-10-30
date: 2026-10-30
tags: [XAU/USD, DXY, 米10年債, FOMC, ECB]
description: 北米・欧州・ロシア・中国・インド・中東の6つの窓から、第44週の金・ドル・米金利の読みを同じ形で観測する。
draft: true
access: public

windows:
  - region: na
    media:
      - { name: Kitco News, url: "https://www.kitco.com/news" }
      - { name: investingLive, url: "https://investinglive.com/" }
    gold:
      stance: bear
      summary: FOMC後も4,000ドルの維持に苦戦。「タカ派の様子見で足止め」（TDS）、「3,900ドルも」（Sucden）。5,000ドルの道を残す声は少数派。
    dollar:
      stance: neutral
      summary: 利上げ観測は下支えだが、AI株安の逃避で米債利回りが1か月ぶり低水準に下がり、ドルの上値を抑えた。方向感は出ていない。
    rates:
      stance: neutral
      summary: 12月利上げ（Natixis）とタカ派の据え置きが主題。一方で10年債は4.90%へ低下。政策はタカ派、利回りは下、で読みが割れる。
    quote:
      text: "Gold prices are holding support above $4,000 after the Federal Reserve left interest rates unchanged on Wednesday"
      source: Kitco News（10/29）
      url: "https://www.kitco.com/news/article/2026-10-29/gold-remains-stuck-fed-takes-hawkish-pause-tds-melek"
    status: 確定

  - region: eu
    media:
      - { name: ING Think, url: "https://think.ing.com/" }
      - { name: FXStreet, url: "https://www.fxstreet.com/news" }
    gold:
      stance: bear
      summary: 米PCEで12月利上げ観測が強まり、金は4,000ドル目前まで下落。「強い米経済は本来は金を沈める」という整理で弱気が前提。
    dollar:
      stance: bear
      summary: 「タカ派のFedはもうドルを持ち上げられない」。利上げ3回分は織り込み済みで、他の中銀も引き締め側。DXYは米イラン協議の期待で下落。
    rates:
      stance: bear
      summary: INGは12月のECB・Fed利上げを見込みつつ「利回りは下がる方を選んだ」。キャリーの観点で債券市場は動じていない、という読み。
    quote:
      text: "Rate hikes are coming in December, but bond markets are not fretting from a carry perspective"
      source: ING Think「Rates Spark」（10/29）
      url: "https://think.ing.com/articles/rates-spark-hikes-coming-but-bond-yields-choosing-to-fall/"
    status: 確定

  - region: ru
    media:
      - { name: ProFinance.ru, url: "https://www.profinance.ru/news/" }
    gold:
      stance: bear
      summary: 「米インフレ指標を前に利上げ観測が残り、金は値下がり」。ロシア語圏の速報も、金の下落をFedの利上げ観測一本で説明している。
    dollar:
      stance: neutral
      summary: FOMC前は「ドルは安定」、ECB後は「ユーロが下落」。ドル自体の強弱より、中銀イベントの前後関係で記述している。
    rates:
      stance: bull
      summary: 利上げ観測の継続が主題。利回りの低下には触れていない。ルーブル固有の論点は今週は無し（公式レートは80.68、前日比わずかに高）。
    quote:
      text: "金は、米インフレ指標を前に利上げ観測が残るなかで値下がりしている（訳）"
      source: ProFinance.ru（10/29 15:15）
      url: "https://www.profinance.ru/live/2026-10-29/1000544-zoloto-desheveet-na-fone-sokhranyayushchikhsya-ozhidaniy-povysheniya"
    status: 確定

  - region: cn
    media:
      - { name: 汇通財経 FX678, url: "https://www.fx678.com/" }
    gold:
      stance: bear
      summary: 4,000ドル近辺のレンジで、利上げ観測が圧迫。「実質金利の高止まりが金の保有コストを上げる」。地政学は支えとして併記。
    dollar:
      stance: bull
      summary: 「高止まりして往来」。タカ派のFed期待と安全需要が支え、と整理。DXYは101.75前後を表示。北米・欧州より強気側。
    rates:
      stance: bull
      summary: 第3四半期GDPとコアPCEで12月利上げ確率が上昇、実質金利は高いまま。ウォルシュ議長の「来年の会合から規則を変える」発言も報じる。
    quote:
      text: "米第3四半期GDPとコアPCEが12月利上げ観測を強め、高い実質金利が金の保有コストを押し上げる（訳）"
      source: 汇通財経（10/30 11:26）
      url: "https://news.fx678.com/202610301126509063.shtml"
    status: 確定

  - region: in
    media:
      - { name: Business Today, url: "https://www.businesstoday.in/markets" }
    status: 未確認
    # 市場面に今週の金・ルピー・Fedの記事が無かった（株式の個別銘柄が中心）。Goodreturns は小売価格のみで論調を持たない。
    # 規則どおり、他の媒体や検索結果で埋めない。

  - region: me
    media:
      - { name: Economies.com, url: "https://www.economies.com/" }
      - { name: Argaam, url: "https://www.argaam.com/en" }
    gold:
      stance: bear
      summary: 「Fedのシグナルが12月利上げ観測を保ち、金と銀は下落」。明示の強弱は無いが、下落を利上げ観測に結びつける書き方。
    dollar:
      stance: bear
      summary: 「強いGDPにもかかわらずドルは後退」。インフレ加速とFedが12月利上げを明言しない不確実さを理由にしている。
    rates:
      stance: neutral
      summary: Argaamは「12月利上げをアナリストが予想」、Economies.comは「Fedは次の利上げを示唆したがらない」。湾岸の読みは割れている。
    quote:
      text: "The US dollar declined against major currencies on Thursday, October 29"
      source: Economies.com（10/29）
      url: "https://www.economies.com/stocks/united-states-news/us-dollar-retreats-despite-strong-gdp-growth-as-fed-rate-outlook-remains-uncertain-50396"
    status: 確定
    # 主のArgaamは金・ドルの記事が無く（Fed予想の1本のみ）、代替のZawyaも企業ニュースのみ。第2代替のEconomies.comで確定した。

physicalNotes: {}

review:
  of: ""
  items: []
  # 初号のため前週の論調が無い。第45週から判定を出す。
---

## 要点

- 6つの窓のうち論調が取れた5つは、金に**すべて弱気**。理由も揃っていて、米PCEと第3四半期GDPによる12月利上げ観測の一点。
- ドルは割れた。北米は中立、欧州と中東は弱気（「タカ派でも上がらない」「強いGDPでも後退」）、中国だけ強気（「高止まり」）。
- 米金利は、政策（タカ派・12月利上げ）と利回り（1か月ぶり低水準）で向きが逆。北米は中立、欧州は利回り側を取って弱気、ロシアと中国は政策側を取って強気。
- インドは今週の論調が取れず未確認。中東は主媒体に記事が無く、第2代替で確定。

## 総括

今週の6つの窓は、金については珍しく一致した。北米・欧州・ロシア・中国・中東のどこを読んでも、金の下落を説明する言葉は「12月利上げ観測」の一つだけで、地域による解釈の差が無い。差が出たのは、その先のドルと金利の読み方である。

欧州（FXStreet・ING）は「利上げはもう織り込まれていて、ドルも利回りもこれ以上は上がらない」と読む。中国（汇通財経）は逆に「ドルは高止まり、実質金利は高いまま」と読み、金の保有コストの上昇を主題にする。同じ利上げ観測を、欧州は「出尽くし」、中国は「継続」として扱っている。来週、この2つのどちらが当たったかは、ドル指数と米10年債の前週比で機械的に判定できる（SPEC の閾値：ドル指数 ±0.5%、米10年 ±5bp）。

北米が中立に留まったのは、Kitco が政策（タカ派の据え置き）を、investingLive が利回り（AI株安の逃避で低下）を見ていて、2つの主媒体の間で向きが割れたためである。1つの窓に2媒体を置く設計が、ここでは「割れ」として表に出た。

中東は、湾岸の市場メディア（Argaam・Zawya）が企業決算と社債の報道に寄っていて、金・ドルの論調は取れなかった。確定させたのはヨルダン拠点の Economies.com で、これは「中東の窓」というより「アラビア語圏のFXサイトの窓」になっている。インドは主媒体の市場面に該当記事が無く、未確認のまま出す。

## 出典

- Kitco News：Gold remains stuck as the Fed takes a hawkish pause（10/29） https://www.kitco.com/news/article/2026-10-29/gold-remains-stuck-fed-takes-hawkish-pause-tds-melek
- Kitco News：Fed will hike once more in December（10/29） https://www.kitco.com/news/article/2026-10-29/fed-will-hike-once-more-december-slowing-growth-and-falling-energy-ease
- investingLive：Treasuries rally as AI selloff drives flight to safety（10/30） https://investinglive.com/news/some-good-news-treasuries-rally-as-ai-selloff-drives-flight-to-safety-10-year-yield-at-one-month-low/
- ING Think：Rates Spark: Hikes coming, but bond yields choosing to fall（10/29） https://think.ing.com/articles/rates-spark-hikes-coming-but-bond-yields-choosing-to-fall/
- ING Think：Fed holds rates steady despite inflation being too high（10/29） https://think.ing.com/articles/fed-holds-rates-steady-despite-inflation-being-too-high/
- FXStreet：The hawkish Fed can't lift the US Dollar anymore（10/29） https://www.fxstreet.com/analysis/the-hawkish-fed-cant-lift-the-us-dollar-anymore-202610291850
- FXStreet：United States Dollar Index slips as US-Iran hopes cap safe-haven bid（10/30） https://www.fxstreet.com/news/united-states-dollar-index-slips-as-us-iran-hopes-cap-safe-haven-bid-202610300248
- ProFinance.ru：金は利上げ観測を前に値下がり（10/29） https://www.profinance.ru/live/2026-10-29/1000544-zoloto-desheveet-na-fone-sokhranyayushchikhsya-ozhidaniy-povysheniya
- ProFinance.ru：ドルはFed決定を前に安定（10/28） https://www.profinance.ru/news/2026/10/28/ckcv-dollar-ostaetsya-stabilnym-v-preddverii-resheniya-frs.html
- 汇通財経：米PCEが利上げ観測を強め金は4,000ドル前後へ（10/30） https://www.fx678.com/C/20261030/202610301029359061.html
- 汇通財経：Fedは10月据え置き、ウォルシュ氏「来年の会合から規則変更」（10/29） https://www.fx678.com/C/20261029/202610290954141711.html
- Economies.com：US dollar retreats despite strong GDP growth（10/29） https://www.economies.com/stocks/united-states-news/us-dollar-retreats-despite-strong-gdp-growth-as-fed-rate-outlook-remains-uncertain-50396
- Argaam：Analysts expect Fed rate hike in December（10/28） https://www.argaam.com/en/article/articledetail/id/1948020

---

## 参考：現物の層の試し取り（段階2の前倒し。正式号には載せない）

インドの窓の系列「国内小売価格（24K）」を Goodreturns から取った。国際価格との差（プレミアム）は、USAGOLD の金とドルルピーが要るので今回は出していない。
GST・TCS 等を含まない指標値。

| 日付 | 24K 1gあたり | 前日比 |
|---|---|---|
| 10/26 | ₹14,275 | +17 |
| 10/27 | ₹14,329 | +54 |
| 10/28 | ₹14,395 | +66 |
| 10/29 | ₹14,395 | 0 |
| 10/30 | ₹14,394 | −1 |

週間では +₹119（約 +0.8%）。同じ週に国際価格（ドル建て）は 4,000 ドル近辺へ下げているので、ルピー建ての小売価格は逆方向に動いた。
インドの窓は論調が未確認でも、現物の層だけで「国際価格の下落をルピー安が打ち消している」という観測が成り立つ。2層にした意味が初号から出る形。

---

## この試作で分かったこと（SPEC への反映候補）

1. **論点ごとの未確認が要る。**中東は主媒体（Argaam）に金利の記事だけがあり、金・ドルは第2代替で埋めた。いまの形式は窓単位の `status` しか無いので、`gold` / `dollar` / `rates` のそれぞれに `未確認` を置けるようにしたい（Take の `stance` に `unknown` を足すか、`status` を論点ごとに持つ）
2. **FX678 は `news.fx678.com` が不安定**（2回とも接続が切れた）。`www.fx678.com` を主にする
3. **インドの主媒体の見直し。**Business Today の市場面は株式の個別銘柄が中心で、金・ルピー・Fed の記事が週に1本も無かった。Goodreturns は現物のみ。インドの論調は、同サイトの「Gold & Silver Rates」ページか、別の媒体（取れる候補は少ない）を試す
4. **中東の主媒体の見直し。**Argaam・Zawya は企業決算と社債に寄る。論調は Economies.com を主に昇格させ、Argaam は「湾岸の資金」の補助に回す
5. **ING は通貨の見解がトップページから拾えない。**「FX Daily」の記事 URL を直接取る手順にする（`WORLD_SOURCES` に一覧ページでなく記事の種類を持たせる）
6. **1窓2媒体の「割れ」の扱い。**北米は Kitco（政策）と investingLive（利回り）で向きが逆になり、中立にした。割れたときは「中立」ではなく「割れ」と表示したほうが観測として正直。`stance` に `split` を足すか、media ごとに stance を持つかを決める
7. **時刻の基準。**各媒体の時刻は現地時刻や UTC が混在する。記事 URL の日付で対象週を確定する規則は機能したが、金曜の米国セッションを含めるかどうかは「土曜 14:00 時点で読めた記事まで」と決めておく
