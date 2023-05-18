# -*- coding: utf-8 -*-
"""
Created on Thu May 18 19:51:46 2023

@author: Tasheer
"""

from fastapi import FastAPI
from scipy import spatial
import pandas as pd
import uvicorn
import ast
import openai
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

openai.api_key = "OPEN AI API KEY"
embed_model = "text-embedding-ada-002"

#Load Embeddings
df = pd.read_csv('DocumentsEmbeddings.csv')

def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 100
) :
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding_response = openai.Embedding.create(
        model=embed_model,
        input=query,
    )
    query_embedding = query_embedding_response["data"][0]["embedding"]
    strings_and_relatednesses = [
        (row["Content"], relatedness_fn(query_embedding, ast.literal_eval(row["Embeddings"])))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/generateAnswer")
def GenerateAnswer(query:str,language:str):

    strings, relatednesses = strings_ranked_by_relatedness(query, df, top_n=3)
    # Creating Context from retrieved data
    augmented_query = "\n\n---\n\n".join(strings)+"\n\n-----\n\n"+query
    ## Creating the prompt for model
    primer = """You are Q&A bot. A highly intelligent system that answers
    user questions based on the information provided by the user above
    each question. If the information can not be found in the information
    provided by the user you truthfully say "I don't know". 
    """

    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": primer},
            {"role": "user", "content": augmented_query + '\n Answer in {}'.format(language)}
        ]
    )
    
    text = res['choices'][0]['message']['content']
    return {"answer":text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    