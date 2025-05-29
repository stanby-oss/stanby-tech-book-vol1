import re
from pathlib import Path
import pandas as pd
from ranx import Qrels, Run
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

from searcher.vespa_searcher import search
from logger import logger


def _pick_qrels(df: pd.DataFrame) -> Qrels:
    logger.debug("Pick qrels")
    qrel_dict = {}
    for group_keys, (doc_ids, labels, texts, titles) in tqdm(
        df.iterrows(), total=len(df), desc="pick qrels"
    ):
        q_id, _ = group_keys
        combine_passage_labels = dict(zip(doc_ids, labels))

        # labels == 1 のものだけを取り出す
        combine_passage_labels = {
            k: v for k, v in combine_passage_labels.items() if v == 1
        }
        qrel_dict[q_id] = combine_passage_labels

    return Qrels(qrel_dict)


def _qrels(df: pd.DataFrame, cache_path: Path | None = None) -> Qrels:
    if cache_path is not None:
        qrels_file_name = "qrels"
        qrels_file_path = cache_path / f"qrels/{qrels_file_name}.trec"
        if qrels_file_path.exists():
            logger.debug(f"Load qrels from cache: {qrels_file_path}")
            return Qrels.from_file(str(qrels_file_path))
    qrel = _pick_qrels(df)
    if cache_path is not None:
        logger.debug(f"Save qrels to cache: {qrels_file_path}")
        qrels_file_path.parent.mkdir(parents=True, exist_ok=True)
        qrel.save(str(qrels_file_path))
    return qrel


def _run_rerank_parallel_threads(
    run_name,
    df: pd.DataFrame,
    mode: str,
    max_workers: int = 4,
) -> tuple[Run, dict]:
    run_dict = {}
    meta = {
        "elapsed_list": [],
        "total_counts": [],
        "coverage_percent_list": [],
        "coverage_documents_list": [],
    }

    tasks = [(q_id, question) for (q_id, question), _ in df.iterrows()]

    with ThreadPoolExecutor(max_workers=max_workers) as exe:
        future_to_q = {
            exe.submit(search, question, mode): q_id for q_id, question in tasks
        }
        for future in tqdm(
            as_completed(future_to_q), total=len(future_to_q), desc="search"
        ):
            q_id = future_to_q[future]
            try:
                result = future.result()
                dic = {}
                for doc in result["results"]:
                    dic[doc["doc_id"]] = doc["score"]
                run_dict[q_id] = dic

                meta["elapsed_list"].append(result["elapsed"])
                meta["total_counts"].append(result["totalCount"])
                meta["coverage_percent_list"].append(result["coverage.percent"])
                meta["coverage_documents_list"].append(result["coverage.documents"])
            except Exception as e:
                logger.error(f"Query {q_id} failed: {e}")
    return Run(run_dict, name=run_name), meta


def _run(
    df: pd.DataFrame,
    mode: str,
    cache_path: Path | None = None,
) -> tuple[Run, dict]:
    run_name = re.sub(r"/+$", "", "vespa").split("/")[-1]

    if cache_path is not None:
        runs_file_name = f"{run_name}"
        runs_file_path = cache_path / f"runs/{runs_file_name}.lz4"
        if runs_file_path.exists():
            logger.debug(f"Load run from cache: {runs_file_path}")
            return Run.from_file(str(runs_file_path), name=run_name), []

    run, meta = _run_rerank_parallel_threads(
        df=df,
        mode=mode,
        run_name=run_name,
    )
    if cache_path is not None:
        logger.debug(f"Save run to cache: {runs_file_path}")
        runs_file_path.parent.mkdir(parents=True, exist_ok=True)
        run.save(str(runs_file_path))

    return run, meta


def runner(
    df: pd.DataFrame,
    mode: str,
    cache_path: Path | None = None,
) -> tuple[Qrels, list[Run], dict]:
    """
    Run the evaluation on the Vespa search engine.
    """
    qrel = _qrels(df, cache_path=cache_path)

    runs: list[Run] = []
    run_result, meta = _run(
        df=df,
        mode=mode,
        cache_path=cache_path,
    )
    runs.append(run_result)

    return qrel, runs, meta
