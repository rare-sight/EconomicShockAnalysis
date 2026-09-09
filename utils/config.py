from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_config():
    with (PROJECT_ROOT / "sources.yaml").open(encoding="utf-8") as file:
        return yaml.safe_load(file)