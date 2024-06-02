import logging
from logging import Logger

import yaml


def load_yml(file):
    with open(file, 'r', encoding='utf-8') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)


def load_txt(file):
    with open(file, 'r', encoding='utf-8') as f:
        return f.read().splitlines()


def get_logger(name: str) -> Logger:
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s [%(levelname)s] %(message)s", level=logging.INFO
    )
    # set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpx").setLevel(logging.WARNING)
    return logging.getLogger(name)
