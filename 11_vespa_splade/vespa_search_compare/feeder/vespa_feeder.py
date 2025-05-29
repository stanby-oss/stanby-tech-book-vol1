import os
import requests
import pandas as pd
from datetime import datetime
from tqdm import tqdm

import torch
from torch.utils.data import Dataset, DataLoader
from vespa.application import Vespa
from splade.encoder import encode_splade_batch
from config import VESPA_ENDPOINT, SCALE, FEED_BATCH_SIZE
from logger import logger


def convert_date(date_str):
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return int(dt.timestamp())
    except Exception as e:
        logger.error(f"Error converting date: {date_str} - {e}")
        return 0


def get_parquet_file(local_path, url):
    if not os.path.exists(local_path):
        logger.info(f"Downloading {url} to {local_path}...")
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        resp = requests.get(url)
        resp.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(resp.content)
    return local_path


class JacwirDataset(Dataset):
    def __init__(self, df: pd.DataFrame):
        self.df = df.reset_index(drop=True)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, i):
        row = self.df.iloc[i]
        return {
            "doc_id": str(row.get("doc_id", i)),
            "title": row.get("title", ""),
            "description": row.get("description", ""),
            "link": row.get("link", ""),
            "date": convert_date(row.get("date", "")),
            "text": f"{row.get('title', '')} {row.get('description', '')}",
        }


# ── バルクバッファ生成（DataLoaderから）───────────────────
def generate_bulk_buffer(dataloader: DataLoader):
    """
    DataLoaderからバルクバッファを生成するジェネレータ関数
    """
    for batch in dataloader:
        # まず date フィールド全体をリスト化（Tensor → Python list）
        dates = batch["date"]
        if isinstance(dates, torch.Tensor):
            dates = dates.cpu().tolist()

        texts = batch["text"]
        indices_list, values_list = encode_splade_batch(texts)
        docs = []
        for idx, doc_id in enumerate(batch["doc_id"]):
            date = dates[idx]
            # values内のテンソルをPythonのfloatに変換
            sparse_map = {
                str(token_idx): weight.item()
                if isinstance(weight, torch.Tensor)
                else weight
                for token_idx, weight in zip(indices_list[idx], values_list[idx])
            }
            sparse_map_int = {}
            for token_idx, weight in zip(indices_list[idx], values_list[idx]):
                w = weight.item() if isinstance(weight, torch.Tensor) else weight
                sparse_map_int[str(token_idx)] = int(round(w * SCALE))

            docs.append(
                {
                    "id": doc_id,
                    "fields": {
                        "doc_id": doc_id,
                        "title": batch["title"][idx],
                        "description": batch["description"][idx],
                        "link": batch["link"][idx],
                        "date": date,
                        "sparse_rep": sparse_map,
                        "sparse_weight": sparse_map_int,
                    },
                }
            )
        yield docs


def callback(response, doc_id):
    if not response.is_successful():
        logger.error(
            f"Failed to feed {doc_id}: {response.status_code} {response.get_json()}"
        )


def feed():
    # データ取得
    url = "https://huggingface.co/datasets/hotchpotch/JaCWIR/resolve/main/collection/collection-00000-of-00001.parquet"
    parquet = get_parquet_file(".tmp/collection.parquet", url)
    df = pd.read_parquet(parquet, engine="pyarrow")
    total = len(df)
    num_batches = (total + FEED_BATCH_SIZE - 1) // FEED_BATCH_SIZE
    logger.info(f"Total docs: {total}, batches: {num_batches}")

    # DataLoader
    dataset = JacwirDataset(df)
    loader = DataLoader(
        dataset, batch_size=FEED_BATCH_SIZE, shuffle=False, num_workers=2
    )

    client = Vespa(url=VESPA_ENDPOINT)

    for i, docs in enumerate(
        tqdm(generate_bulk_buffer(loader), total=num_batches, desc="Feeding")
    ):
        logger.info(f"Feeding batch {i + 1}/{num_batches}, docs={len(docs)}")
        client.feed_iterable(docs, schema="jacwir", callback=callback)
