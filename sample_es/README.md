# サンプル用Elasticsearchの構築
## 概要
- Wikipedia(ja)をソースとしたQAのための Elasticsearch を構築し Index の作成を行います
- Analyzerの設定は、[analyzer.json](analyzer.json) に従います
- Index 名は ja となります
- Elasticsearch は localhost:9200 で起動されます

## 前提
- Wikipedia の記事は先に下記に記載する方法で準備してください
- Wikipedia のドキュメントが格納できる空き容量が必要です
- Elasticseearch コンテナを動かすための諸々の設定（メモリの割り当など）は必要に応じて実施してください
- リポジトリカレントのpoetryで必要なライブラリがinstallがされている前提です

## Wikipedia(ja) データの準備
1. Wikipedia(ja) の [dump](https://dumps.wikimedia.org/jawiki/) から `xml-p*.bz2` のファイルをDLしてください
   - 全データだと大きすぎるので、サンプルで試すならば小さいサイズのものを推奨  
   例： `jawiki-20221201-pages-articles-multistream2.xml-p114795p390428.bz2` 387.5 MB 
   ```
   $ wget https://dumps.wikimedia.org/jawiki/20221201/jawiki-20221201-pages-articles-multistream2.xml-p114795p390428.bz2
   ```
2. wikiextractor https://github.com/attardi/wikiextractor で output の名前で json ファイルを出力してください
   ```
   $ pip install wikiextractor
   $ wikiextractor jawiki-20221201-pages-articles-multistream2.xml-p114795p390428.bz2 -o ./output --json
   ```


## 構築方法
1. Elasticsearchを起動します
    ```
    $ docker-compose up
    ```
2. Elasticsearch が起動したら、日本語対応のために、Elasticsearch にプラグインを入れます
   ```
   $ docker ps # コンテナIDを調べる

   $ docker exec ${コンテナID} elasticsearch-plugin install  analysis-kuromoji  analysis-icu 
   
   -> Installing analysis-kuromoji
   -> Downloading analysis-kuromoji from elastic
   [=================================================] 100%??
   -> Installed analysis-kuromoji
   -> Installing analysis-icu
   -> Downloading analysis-icu from elastic
   [=================================================] 100%??
   -> Installed analysis-icu
   ```
3. インストールが成功したら、再起動させてプラグインを有効化させる
    ```
    $ docker restrart ${コンテナID}
    {コンテナID}
    ```
4. 以下のコマンドで、Elasticsearch に Index 作成を行います
   ```
   $ poetry run python wiki_index_create.py
   (haystack-test-pNsJTUgx-py3.9) sample_es[master *+]$ poetry run python wiki_index_create.py 
   output/ ['AA'] []
   output/AA [] ['wiki_10', 'wiki_03', 'wiki_04', 'wiki_05', 'wiki_02', 'wiki_09',    'wiki_07', 'wiki_00', 'wiki_01', 'wiki_06', 'wiki_08']
   処理中： output/AA/wiki_10
   処理中： output/AA/wiki_03
   ...
   ```
5. 構築確認
    - index setting の確認 
    ```
    $ curl -XGET http://localhost:9200/ja?pretty
    {
      "ja" : {
      "aliases" : { },
      "mappings" : {
      "properties" : {
      "article_id" : {
      "type" : "long"
      ...
    ```
    - ドキュメントの確認
    ```
   $ curl -XGET http://localhost:9200/_search?pretty
    {
      "took" : 9,
      "timed_out" : false,
      "_shards" : {
        "total" : 2,
        "successful" : 2,
        "skipped" : 0,
        "failed" : 0
      },
      "hits" : {
        "total" : {
          "value" : 10000,
          "relation" : "gte"
        },
        "max_score" : 1.0,
        "hits" : [
          {
            "_index" : "ja",
            "_type" : "_doc",
            "_id" : "ydjFG4UBTRxrRak5qACr",
            "_score" : 1.0,
            "_source" : {
              "article_id" : "377229",
              "revid" : "1350549",
              "url" : "https://ja.wikipedia.org/wiki?curid=377229",
              "title" : "能管",
              "text" : "能管（のうかん）は、日本の横笛の一つである。能だけではなく歌舞伎、寄席囃子や祇園囃子でも用いられる。竹製のエアリード楽器の一つであるが、独特の音を生むために内径の狭い部分が作られているのが特徴である。\n概説.\n40cm程の長さで、七つの指穴を
    ```