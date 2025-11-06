import logging
import sys

logging.basicConfig(
    level=logging.WARNING,  # Default level for root logger
    format="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logging.getLogger("optexity").setLevel(logging.DEBUG)
