import logging
import pathlib

from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import BM25Retriever, FARMReader
from haystack.pipelines import ExtractiveQAPipeline
from haystack.utils import print_answers

if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING
    )
    logging.getLogger("haystack").setLevel(logging.INFO)

    # 以下の設定は各自で変更してください
    use_gpu: bool = True
    setting_dict = {
        "host": "localhost",
        "port": 9200,
        "index": "ja",
        "create_index": False, # これがないと "embedding":{"type":"dense_vector","dims":768} というマッピングが勝手に追加されてしまうので注意（Default True ）
        # 以下の3つの引数の役割については、 https://github.com/deepset-ai/haystack/blob/v1.10.0/haystack/document_stores/elasticsearch.py#L63 を参照
        "search_fields": ["text"],
        "content_field": "text",
        "name_field": "title.keyword",
    }

    path: pathlib.Path = pathlib.Path("farm_reader_model")
    try:
        reader = FARMReader(model_name_or_path=path.name, use_gpu=use_gpu)
    except Exception:
        FARMReader(
            model_name_or_path="ybelkada/japanese-roberta-question-answering",
            use_gpu=use_gpu,
        ).save(directory=path)
        reader = FARMReader(model_name_or_path=path.name, use_gpu=use_gpu)
    document_store = ElasticsearchDocumentStore(**setting_dict)
    retriever = BM25Retriever(document_store=document_store)
    pipe = ExtractiveQAPipeline(reader, retriever)

    while True:
        query = input("質問を入力してください（exit で終了）>>")
        if query == "exit":
            break
        prediction = pipe.run(
            query=query, params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 5}}
        )
        print_answers(prediction, details="all")
