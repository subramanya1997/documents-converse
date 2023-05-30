"""
   Created on Tue May 30 2023
   Copyright (c) 2023 Subramanya N
"""
import os
import argparse


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Flask server to handle files using OCR"
    )
    parser.add_argument(
        "--embeddings-model",
        type=str,
        default="text-embedding-ada-002",
        help="The name of the text embedding model to use. Defaults to text-embedding-ada-002",
    )
    parser.add_argument(
        "--chat-model",
        type=str,
        default="gpt-3.5-turbo",
        help="The name of the GPT-3 model to use. Defaults to gpt-3.5-turbo",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Controls the randomness of the output. Higher values make the output more random, lower values make it more deterministic. Defaults to 0",
    )
    parser.add_argument(
        "--top-n",
        type=float,
        default=5,
        help="Number of files to consider for relatedness. Defaults to 5",
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs",
        help="Directory to store logs. Defaults to logs",
    )
    parser.add_argument(
        "--logger-config-file",
        type=str,
        default="configs/logging_config.yml",
        help="Path to logger config file. Defaults to configs/logger_config.yaml",
    )

    args = parser.parse_args()

    if not os.path.exists(args.log_dir):
        os.makedirs(args.log_dir)
    return args
