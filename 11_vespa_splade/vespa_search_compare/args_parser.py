from argparse import ArgumentParser

DEFAULT_METRICS = "map@10,mrr,hit_rate@10,hits,precision,recall,f1,ndcg@10"


def add_mode_argument(parser):
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="weakand",
        choices=["weakand", "wand"],
        help="検索モードを指定（weakand, wand）",
    )


def parse_args():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    # feedコマンド
    feed_parser = subparsers.add_parser("feed", help="データをVespaに投入")

    # searchコマンド
    search_parser = subparsers.add_parser("search", help="Vespaで検索")
    search_parser.add_argument(
        "-q", "--query", type=str, required=True, help="検索クエリ"
    )
    add_mode_argument(search_parser)
    search_parser.add_argument(
        "-k", "--top_k", type=int, default=10, help="検索モード時のtop_k"
    )

    # evalコマンド
    eval_parser = subparsers.add_parser("eval", help="Vespaで評価")
    eval_parser.add_argument("-d", "--debug", action="store_true")
    eval_parser.add_argument("-v", "--verbose", action="store_true")
    add_mode_argument(eval_parser)
    eval_parser.add_argument(
        "-r",
        "--report_metrics",
        type=str,
        default=DEFAULT_METRICS,
    )
    eval_parser.add_argument(
        "-nd",
        "--no_data_cache",
        action="store_true",
    )
    eval_parser.add_argument(
        "-nr",
        "--no_run_cache",
        action="store_true",
    )
    eval_parser.add_argument(
        "-f",
        "--output_format",
        help="output format, choose from table, markdown, csv, latex",
        type=str,
        choices=["table", "markdown", "csv", "latex", "markdown_with_links"],
        default="table",
    )
    eval_parser.add_argument(
        "--max_p_value",
        type=float,
        default=0.01,
        help="Set the maximum p-value threshold for the statistical test, used only when the output format is 'table'.",
    )

    args = parser.parse_args()
    return args
