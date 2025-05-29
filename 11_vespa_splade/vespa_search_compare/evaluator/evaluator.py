from evaluator.load_data import load_df
from evaluator.runner import runner
from ranx import compare, evaluate
from pathlib import Path
import numpy as np

DEFAULT_CACHE_PATH = Path(__file__).parent / ".tmp/eval_results"


def eval(args):
    if args.no_data_cache:
        cache_path = None
    else:
        cache_path = DEFAULT_CACHE_PATH

    df = load_df(cache_path=cache_path)

    if args.no_run_cache:
        cache_path = None
    else:
        cache_path = DEFAULT_CACHE_PATH

    # runnerからelapsed_listも受け取る
    qrel, runs, meta = runner(
        df=df,
        mode=args.mode,
        cache_path=cache_path,
    )

    if meta:
        elapsed_list = meta["elapsed_list"]
        avg_time = sum(elapsed_list) / len(elapsed_list)
        median = np.median(elapsed_list)
        p90 = np.percentile(elapsed_list, 90)
        p95 = np.percentile(elapsed_list, 95)
        p99 = np.percentile(elapsed_list, 99)
        print(f"Vespaリクエスト平均時間: {avg_time:.3f}秒 (n={len(elapsed_list)})")
        print(f"Vespaリクエスト中央値: {median:.3f}秒")
        print(f"Vespaリクエスト90%tile: {p90:.3f}秒")
        print(f"Vespaリクエスト95%tile: {p95:.3f}秒")
        print(f"Vespaリクエスト99%tile: {p99:.3f}秒")
        print(f"Vespaリクエスト全体時間: {sum(elapsed_list):.3f}秒")

        coverage_percent_list = meta["coverage_percent_list"]
        coverage_documents_list = meta["coverage_documents_list"]
        avg_coverage_percent = sum(coverage_percent_list) / len(coverage_percent_list)
        avg_coverage_documents = sum(coverage_documents_list) / len(
            coverage_documents_list
        )
        print(
            f"Vespaカバレッジ平均: {avg_coverage_percent:.3f} (n={len(coverage_percent_list)})"
        )
        print(
            f"Vespaカバレッジドキュメント平均: {avg_coverage_documents:.3f} (n={len(coverage_documents_list)})"
        )

    report_metrics = args.report_metrics.split(",")

    report = compare(qrels=qrel, runs=runs, metrics=report_metrics)
    print(report)

    scores = evaluate(qrel, runs[0], ["map@5", "mrr"])
    print(scores)

    run0 = runs[0]

    # 差分の確認
    if args.debug:
        for q_id in qrel.qrels:
            relevant_docs = set(qrel.qrels[q_id].keys())
            retrieved_docs = set(run0.to_dict()[q_id].keys())

            missing = relevant_docs - retrieved_docs
            extra = retrieved_docs - relevant_docs

            print(f"Query ID: {q_id}")
            if missing:
                print(f"  Missing relevant docs: {', '.join(missing)}")
            if extra:
                print(f"  Retrieved but not relevant: {', '.join(extra)}")
            if not missing and not extra:
                print("  All relevant documents retrieved correctly.")
