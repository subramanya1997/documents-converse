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
import openai
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


openai.api_key = "OPEN AI API KEY"
embed_model = "text-embedding-ada-002"
batch_size = 100  # how many embeddings we create and insert at once
finalList = []
for i in tqdm(range(0, len(chunks), batch_size)):
    # find end of batch
    i_end = min(len(chunks), i + batch_size)
    meta_batch = chunks[i:i_end]
    texts = [x["text"] for x in meta_batch]
    # create embeddings (try-except added to avoid RateLimitError)
    try:
        res = openai.Embedding.create(input=texts, engine=embed_model)
    except:
        done = False
        while not done:
            sleep(5)
            try:
                res = openai.Embedding.create(input=texts, engine=embed_model)
                done = True
            except:
                pass
    embeds = [record["embedding"] for record in res["data"]]
    # cleanup metadata
    meta_batch = [
        {"title": x["title"], "type": x["type"], "text": x["text"], "chunk": x["chunk"]}
        for x in meta_batch
    ]
    finalList.extend(
        [x[0]["type"], x[0]["title"], x[0]["text"], x[0]["chunk"], x[1]]
        for x in list(zip(meta_batch, embeds))
    )

df = pd.DataFrame(
    finalList,
    columns=["DocumentType", "DocumentTitle", "Content", "Chunk", "Embeddings"],
)
df.to_csv("DocumentsEmbeddings.csv", index=False)
