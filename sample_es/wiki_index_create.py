import json
import os
from copy import deepcopy
from typing import TypedDict

import esanpy
from elasticsearch import Elasticsearch, helpers  # bulkを使うために追加


class WikiDict(TypedDict):
    id: int
    revid: int
    url: str
    title: str
    text: str


class EsDocuent(TypedDict):
    article_id: int
    revid: int
    url: str
    title: str
    text: str
    content_type: str


def wikidict2esarticle(d: WikiDict) -> EsDocuent:
    return {
        "article_id": d["id"],
        "revid": d["revid"],
        "url": d["url"],
        "title": d["title"],
        "text": d["text"],
        "content_type": "text",
    }


def gen_bulk_data(documents: list[WikiDict]):
    for d in documents:
        yield {"_op_type": "create", "_index": "ja", "_source": wikidict2esarticle(d)}


def file_to_document_list(file_path: str) -> list[WikiDict]:
    result: list[WikiDict] = []
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            if line == "\n":
                continue
            j: WikiDict = json.loads(line)
            result += [
                update_text_in_dict(j, text)
                for text in split_text_of_300_words(j["text"])
            ]
    return result


def split_text_of_300_words(text: str) -> list[str]:
    n: int = 400
    tokens: list[str] = esanpy.analyzer(text, analyzer="kuromoji")
    if len(tokens) <= n:
        return [text]
    else:
        result: list[str] = []
        for i in range(0, len(tokens), n):
            new_text: str = "".join(tokens[i : i + n])
            result.append(new_text)
        return result


def update_text_in_dict(d: WikiDict, text: str) -> WikiDict:
    d2: WikiDict = deepcopy(d)
    d2["text"] = text
    return d2


if __name__ == "__main__":
    esanpy.start_server()
    with open("analyzer.json", "r") as f:
        mapping: json = json.load(f)
        es: Elasticsearch = Elasticsearch("http://localhost:9200")
        es.indices.create(
            index="ja", body=mapping, ignore=400  # ignore 400 already  code
        )

    path: str = "output/"
    documents: list[dict] = []
    for dirs, subdirs, files in os.walk(path):
        print(dirs, subdirs, files)
        for file in files:
            file_path = f"{dirs}/{file}"
            print("処理中：", file_path)
            docs: list[documents] = file_to_document_list(file_path=file_path)
            documents += docs
    helpers.bulk(es, gen_bulk_data(documents))
    esanpy.stop_server()
