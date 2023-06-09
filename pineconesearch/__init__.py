"""
   Created on Thu Jun 01 2023
   Copyright (c) 2023 Subramanya N
"""
import os
from pineconesearch.search import PineConeSearch

# get the Pinecone API key using the "PINECONE_API_KEY" environment variable.
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_ENV = os.environ["PINECONE_ENV"]
PINECONE_INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]

# initialize PineConeSearch
pinecone_search = PineConeSearch(
    pinecone_api_key=PINECONE_API_KEY,
    pinecone_env=PINECONE_ENV,
    pinecone_index=PINECONE_INDEX_NAME,
)

__all__ = ["pinecone_search"]
