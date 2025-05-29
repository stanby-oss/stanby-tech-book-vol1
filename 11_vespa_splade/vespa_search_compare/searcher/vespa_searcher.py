import json
import requests
import time  # 追加

from logger import logger
from splade.encoder import encode_splade_batch
from config import VESPA_ENDPOINT, SCALE


def query_vespa(query_text: str, top_k: int, mode: str) -> tuple[dict, float]:
    # 1. クエリテキストをスパースベクトルに変換
    batch_text = [query_text]
    indices, values = encode_splade_batch(batch_text)

    q_sparse = {str(idx): float(w) for idx, w in zip(indices[0], values[0])}
    q_sparse_int = {
        str(idx): int(round(w * SCALE)) for idx, w in zip(indices[0], values[0])
    }

    # 2. YQL 文の組み立て（モードによって切り替え）
    if mode == "wand":
        yql = (
            "select doc_id, title, description, summaryfeatures from jacwir where"
            "({targetHits:%d} wand(sparse_weight, @query_sparse_int))" % top_k
        )
    else:  # default or weakand
        yql = (
            "select doc_id, title, description, summaryfeatures from jacwir where"
            "({targetHits:%d} userInput(@userInput))" % top_k
        )

    # 3. パラメータとしてクエリベクトルを注入
    body = {
        "yql": yql,
        "model.locale": "ja-JP",
    }
    if mode == "wand":
        body["query_sparse_int"] = str(q_sparse_int)
        body["ranking"] = "wand"
    else:
        body["userInput"] = query_text
        body["input.query(q_splade)"] = q_sparse

    logger.debug(
        f"Sending sparse query to Vespa: hits={top_k}, vec_size={len(q_sparse)}, mode={mode}"
    )
    start_time = time.time()
    resp = requests.post(f"{VESPA_ENDPOINT}/search/", json=body)
    elapsed = time.time() - start_time
    logger.debug(f"Vespa request took {elapsed:.3f} seconds")

    if resp.status_code != 200:
        logger.error(
            f"Vespa request failed: [status] {resp.status_code}\n [resp]: {resp.text}\n [req]: {json.dumps(body)}"
        )
        resp.raise_for_status()

    return resp.json(), elapsed


def convert_vespa_results(vespa_results) -> list[dict]:
    result = []
    children = vespa_results["root"].get("children")
    if children is None:
        return result

    for hit in children:
        doc_id = hit["fields"]["doc_id"]
        title = hit["fields"]["title"]
        description = hit["fields"].get("description", "")
        score = hit["relevance"]
        matchfeatures = hit["fields"].get("matchfeatures")
        summaryfeatures = hit["fields"].get("summaryfeatures")
        result.append(
            {
                "doc_id": doc_id,
                "title": title,
                "description": description,
                "score": score,
                "matchfeatures": matchfeatures,
                "summaryfeatures": summaryfeatures,
            }
        )
    return result


def search(query_text, mode, top_k=10) -> dict:
    res, elapsed = query_vespa(query_text, top_k, mode=mode)
    return {
        "results": convert_vespa_results(res),
        "elapsed": elapsed,
        "totalCount": res["root"]["fields"][
            "totalCount"
        ],  # first-phase通過後のヒット数
        "coverage.percent": res["root"]["coverage"][
            "coverage"
        ],  # スキャンされたドキュメント数の割合
        "coverage.documents": res["root"]["coverage"][
            "documents"
        ],  # マッチングフェーズで評価されたドキュメント数
    }
