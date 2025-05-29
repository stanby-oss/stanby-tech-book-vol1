import json
from args_parser import parse_args
from feeder.vespa_feeder import feed
from searcher.vespa_searcher import search
from evaluator.evaluator import eval


def main():
    args = parse_args()

    if args.command == "feed":
        feed()
    elif args.command == "search":
        query = args.query
        mode = args.mode
        top_k = args.top_k
        results = search(query_text=query, mode=mode, top_k=top_k)
        print(
            f"検索結果: \n{json.dumps(results['results'], indent=2, ensure_ascii=False)}"
        )
        print(f"Vespaリクエスト時間: {results['elapsed']:.3f}秒")
        print(f"Vespaカバレッジ: {results['coverage.percent']:.3f}")
        print(f"Vespaカバレッジドキュメント数: {results['coverage.documents']}")
        print(f"Vespaヒット数: {results['totalCount']}")
    elif args.command == "eval":
        eval(args)
    else:
        print(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
