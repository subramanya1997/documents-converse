"""
   Created on Tue May 30 2023
   Copyright (c) 2023 Subramanya N
"""
import os
import logging.config
import yaml
from typing import Text


def setup_logging(logger_config_file: Text):
    """
    Setup logging configuration
    """
    with open(logger_config_file, "r") as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
