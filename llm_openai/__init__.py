"""
   Created on Tue May 30 2023
   Copyright (c) 2023 Subramanya N
"""
import os
import openai
from llm_openai.llm_utils import create_chat_completion, create_embeddings

# Set the OpenAI API key using the "OPENAI_API_KEY" environment variable.
openai.api_key = os.environ.get("OPENAI_API_KEY")

__all__ = [
    "create_chat_completion",
    "create_embeddings",
]
