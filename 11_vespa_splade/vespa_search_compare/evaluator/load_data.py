from pathlib import Path
from datasets import load_dataset
import pandas as pd
import ast

DATASET_NAME = "hotchpotch/JaCWIR"


def load_ds():
    return load_dataset(DATASET_NAME, "eval", split="eval"), load_dataset(
        DATASET_NAME, "collection", split="collection"
    )


def load_df(cache_path: Path | None = None):
    if cache_path is not None:
        data_file_path = cache_path / f"datasets/{DATASET_NAME}.csv"
        if data_file_path.exists():
            return pd.read_csv(
                data_file_path,
                index_col=[0, 1],
                converters={"doc_id": ast.literal_eval, "label": ast.literal_eval},
            )

    eval_ds, collection_ds = load_ds()
    collection_df = collection_ds.to_pandas()
    collection_df = collection_df.rename(columns={"description": "text"})
    collection_dict = collection_df.set_index("doc_id").to_dict(orient="index")

    def get_contents(doc_id):
        data = collection_dict[doc_id]
        return {
            "title": data["title"],
            "text": data["text"],
            "doc_id": doc_id,
        }

    def expand_eval(example):
        q_id = "q_id##" + example["positive"][0]
        question = example["query"][0]
        positive = example["positive"][0]
        negatives = example["negatives"][0]
        labels = [1] + [0] * len(negatives)
        q_ids = [q_id] * (1 + len(negatives))
        questions = [question] * (1 + len(negatives))
        positive_data = get_contents(positive)
        negatives_data = [get_contents(n) for n in negatives]
        return {
            "question": questions,
            "q_id": q_ids,
            "doc_id": [positive_data["doc_id"]] + [n["doc_id"] for n in negatives_data],
            "title": [positive_data["title"]] + [n["title"] for n in negatives_data],
            "text": [positive_data["text"]] + [n["text"] for n in negatives_data],
            "label": labels,
        }

    eval_ds = eval_ds.map(
        expand_eval,
        num_proc=4,
        remove_columns=eval_ds.column_names,
        batch_size=1,
        batched=True,
    )

    df_q_id = (
        eval_ds.to_pandas()
        .groupby(["q_id", "question"])
        .agg({"doc_id": list, "label": list, "text": list, "title": list})
    )

    if cache_path is not None:
        data_file_path.parent.mkdir(parents=True, exist_ok=True)
        df_q_id.to_csv(data_file_path, index=True)

    return df_q_id
