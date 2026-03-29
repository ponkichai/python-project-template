"""エントリーポイント。"""

import logging

from src.config import load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    cfg = load_config()
    logger.info("Starting %s", cfg["app"]["name"])


if __name__ == "__main__":
    main()
