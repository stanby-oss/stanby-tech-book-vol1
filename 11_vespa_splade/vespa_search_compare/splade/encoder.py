import sys
import os

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForMaskedLM
from logger import logger

# ── デバイス設定 ─────────────────────────────────────────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")

# ── SPLADEモデルロード ────────────────────────────────────
model_name = "hotchpotch/japanese-splade-v2"
cache_dir = os.path.join(os.path.dirname(__file__), "..", ".tmp")
os.makedirs(cache_dir, exist_ok=True)

try:
    logger.info(f"Loading tokenizer for {model_name} (cache_dir={cache_dir})...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, use_fast=True, cache_dir=cache_dir
    )
    logger.info(
        f"Loading model for {model_name} on {device} (cache_dir={cache_dir})..."
    )
    model = AutoModelForMaskedLM.from_pretrained(model_name, cache_dir=cache_dir).to(
        device
    )
    model.eval()
    logger.info(f"Model {model_name} loaded successfully.")
except Exception as e:
    logger.exception(f"Failed to load SPLADE model or tokenizer '{model_name}': {e}")
    sys.exit(1)


# ── バッチエンコード関数 ─────────────────────────────────
def encode_splade_batch(texts: list[str]):
    inputs = tokenizer(
        texts, return_tensors="pt", truncation=True, max_length=512, padding=True
    ).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    # [batch, seq_len, vocab_size]
    logits = outputs.logits
    relu_logits = F.relu(logits)
    log_relu = torch.log1p(relu_logits)
    mask = inputs.attention_mask.unsqueeze(-1)
    weighted = log_relu * mask
    # [batch, vocab_size]
    sparse_tensor = torch.max(weighted, dim=1).values

    batch_indices = []
    batch_values = []
    threshold = 0.0
    for vec in sparse_tensor:
        nz = torch.nonzero(vec > threshold).squeeze(1)
        vals = vec[nz]
        batch_indices.append(nz.cpu().tolist())
        batch_values.append(vals.cpu().tolist())
    return batch_indices, batch_values
