import os
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

VESPA_ENDPOINT = config["VESPA_ENDPOINT"]
SCALE = config["SCALE"]
FEED_BATCH_SIZE = config["FEED_BATCH_SIZE"]
