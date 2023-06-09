"""
   Created on Tue May 30 2023
   Copyright (c) 2023 Subramanya N
"""
from utils.arg_parser import parse_args
from utils.logger_utils import setup_logging
from utils.gcpocr import convertPDFToText
from utils.app_utils import *

__all__ = [
    "parse_args", 
    "setup_logging", 
    "validate_zip_file",
    "convertPDFToText",
    "process_zip"
]
