# -*- coding: utf-8 -*-
"""
Created on Sat May 13 19:40:27 2023

@author: Tasheer
"""

import os
import tiktoken
from tqdm import tqdm
from uuid import uuid4
import pandas as pd
import pinecone
from llm_openai import create_embedding
from time import sleep
from langchain.text_splitter import RecursiveCharacterTextSplitter

tokenizer = tiktoken.get_encoding("cl100k_base")

# create the length function
def tiktoken_len(text):
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)


# Reading all the documents
def read_text_files(base_dir):
    documents = []
    for root, dirs, files in os.walk(base_dir):
        document_type = os.path.basename(root)
        for file in files:
            if file.endswith(".txt"):
                document_name = os.path.splitext(file)[0]
                file_path = os.path.join(root, file)

                with open(file_path, "r", encoding="utf-8") as input_file:
                    content = input_file.read()

                document = {
                    "DocumentType": document_type,
                    "DocumentName": document_name,
                    "Content": content,
                }
                documents.append(document)

    return documents

def GenerateEmbeddingsAndStoreInPinecone(chunks):
    index_name = 'lab101'
    if index_name not in pinecone.list_indexes():
        # we create a new index
        pinecone.create_index(
            name=index_name,
            metric='cosine',
            dimension=1536  # 1536 dim of text-embedding-ada-002
        )

    #Then we connect to the new created index
    index = pinecone.GRPCIndex(index_name)
    batch_size = 100  # how many embeddings we create and insert at once
    for i in tqdm(range(0, len(chunks), batch_size)):
        # find end of batch
        i_end = min(len(chunks), i + batch_size)
        batch = chunks[i:i_end]
        ids_batch = [x['id'] for x in meta_batch]
        texts = [x["text"] for x in batch]
        res = create_embedding(text=texts)
        embeds = [record["embedding"] for record in res["data"]]
        # cleanup metadata
        meta_batch = [
            {"title": x["title"], "type": x["type"], "text": x["text"], "chunk": x["chunk"]}
            for x in batch
        ]
        to_upsert = list(zip(ids_batch, embeds, meta_batch))
        # upsert to Pinecone
        index.upsert(vectors=to_upsert)


base_directory = "BASE_DIR"

documents = read_text_files(base_directory)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=100,
    length_function=tiktoken_len,
    separators=["\n\n", "\n", " ", ""],
)

chunks = []

for record in tqdm(documents):
    texts = text_splitter.split_text(record["Content"])
    chunks.extend(
        [
            {
                "id": str(uuid4()),
                "text": texts[i],
                "chunk": i,
                "title": record["DocumentName"],
                "type": record["DocumentType"],
            }
            for i in range(len(texts))
        ]
    )
GenerateEmbeddingsAndStoreInPinecone(chunks)

