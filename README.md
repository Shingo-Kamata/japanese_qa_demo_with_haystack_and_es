# Haystack と Elasticsearch を用いた日本語QA応答システムサンプル

## 概要
- Elasticsearch + Haystack を用いて Open-book な Question Answering システムを動かすサンプル
  - https://zenn.dev/shingo_kamata/articles/8a182ff5acfa62
- 基本的には、Haystack の https://haystack.deepset.ai/tutorials/01_basic_qa_pipeline と https://docs.haystack.deepset.ai/docs/languages の内容を参考にしているだけ
- サンプルのElasticsearchを利用する場合、Wikipedia(ja) が格納される

## 前提
- Poetry（Python3.9) が必要
- 自前で検証用のElasticsearchが使えるか、sample_es ディレクトリのElasticsearchを起動して使える前提
- できればGPUがある環境を推奨するが、CPUでも動作可能

## 使い方

### 自前のElasticsearchに接続する場合
- [haystack_qa.py](haystack_qa.py) に接続先のElasticsearch情報を記載してください
- 注意点
  - **必ず検証に用いても問題の無いElasticsearchを利用してください**
    - create_index などのオプションがあり、デフォルトがTrueでありTrueだとMappingが追加されるなど不明な挙動があるため
- すべてのドキュメントに `content_type: keyword型` がないとエラーになるようです。。。
  - content_type には Retriever 対象のフィールドのmapping type（text）などを記載します
    - 参考： [Mapping](https://github.com/Shingo-Kamata/japanese_qa_demo_with_haystack_and_es/blob/main/sample_es/analyzer.json#L64-L65) [値](https://github.com/Shingo-Kamata/japanese_qa_demo_with_haystack_and_es/blob/main/sample_es/wiki_index_create.py#L34)
    - これを追加するこが困難な場合、local にインストールされた Hyastack コードの [search_engine.py](https://github.com/deepset-ai/haystack/blob/v1.10.0/haystack/document_stores/search_engine.py#L1126) の content_type の `None` を `"text"` に編集するワークアラウンドをすれば回避できます
- https://zenn.dev/shingo_kamata/articles/8a182ff5acfa62 に記載したように、Reader が走査するテキストは500単語くらいが良いので、場合によっては、Readerの対象フィールドを変更するか、ドキュメントの内容を分割することを検討してください

### サンプルのElasticsearchを利用する場合
- [sample_es にある README](sample_es/README.md) に従って作成してください
  - 記事のデータは別途用意する必要があります（上記README参照）

### GPUがない場合
- [haystack_qa.py](haystack_qa.py) の該当設定値を変更してください

### poetry install （初回時のみ）
```
$ poetry install
```

### QAの実行例（sample_es利用）
```
$ poetry run python haystack_qa.py
(中略)
INFO:haystack.modeling.utils:Using devices: CUDA:0 - Number of GPUs: 1
質問を入力してください（exit で終了）>>ラグビーの日本監督は？
Inferencing Samples: 100%|█| 1/1 [00:00<00:00,  4.41 Batches/s

Query: ラグビーの日本監督は？
Answers:
[   <Answer {'answer': '神戸製鋼コベルコスティーラーズ', 'type': 'extractive', 'score': 0.9501436948776245, 'context': '大会と日本選手権の2冠連覇を成し遂げた。また日本代表としても第2～4回ラグビーワールドカップに出場した。\n2004年4月、現役を引退し、神戸製鋼コベルコスティーラーズの監督に就任。\n（2012年）早稲田大学ラグビー部アドバイザー(2015年退任)及び女子ラグビー７人制チーム【ラガール７】の総監督を務', 'offsets_in_document': [{'start': 524, 'end': 539}], 'offsets_in_context': [{'start': 68, 'end': 83}], 'document_id': 'VvhNJYUBLyfAJxXYRL5-', 'meta': {'article_id': '322679', 'revid': '1980193', 'url': 'https://ja.wikipedia.org/wiki?curid=322679', 'title': '増保輝則'}}>,
    <Answer {'answer': '萩本光威', 'type': 'extractive', 'score': 0.842361569404602, 'context': 'クネームつけるラグビ日本代表愛称向井監督世界背中見えるコメント大会終了後解任2004年3月22日神戸神戸製鋼製鋼コベルコスティーラーズヘッドコーチ萩本光威監督就任当初同年スーパスーパーパワーズカップパワーズカップロシアカナダ破る優勝導く幸先よいスタート思う続くイタリア敗戦11月欧州遠征スコットランド', 'offsets_in_document': [{'start': 390, 'end': 394}], 'offsets_in_context': [{'start': 73, 'end': 77}], 'document_id': 'afpNJYUBLyfAJxXY7zWG', 'meta': {'article_id': '190986', 'revid': '703098', 'url': 'https://ja.wikipedia.org/wiki?curid=190986', 'title': 'ラグビー日本代表'}}>,
...
```
初回実行時に、`farm_reader_model/` に https://huggingface.co/ybelkada/japanese-roberta-question-answering のモデルがDLされます

## フォルダ構成
```
.
├── README.md
├── farm_reader_model・・・Readerのモデルを保存（キャッシュ）しておく置き場
│   └── .gitkeep
├── haystack_qa.py・・・QAモジュール
├── poetry.lock
├── pyproject.toml
└── sample_es・・・サンプル用のEs
    ├── README.md・・・サンプルEs構築のREADME
    ├── analyzer.json・・・サンプルEsのAnalyzer設定
    ├── docker-compose.yml・・・サンプルEsのDocker
    ├── （output・・・wikiextractの結果を保存する）
    ├── test_wiki_iindex_create.py・・・のテストコード
    └── wiki_iindex_create.py
```