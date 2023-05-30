"""
   Created on Mon May 29 2023
   Copyright (c) 2023 Subramanya N
"""
import os
import logging
from utils import parse_args, setup_logging
from flask import Flask, render_template, request, jsonify
from scipy import spatial
import pandas as pd
import pinecone
import ast
from llm_openai import create_chat_completion, create_embedding
from flask_cors import CORS

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load Embeddings
df = pd.read_csv("data/DocumentsEmbeddings.csv")

def retrieve_related_docs_from_pinecone(
        query: str,
        top_n: int = 5
):
    # find API key in console at app.pinecone.io
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    # find ENV (cloud region) next to API key in console
    PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
    index_name = 'lab101'
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENVIRONMENT
    )
    #Then we connect to the index
    index = pinecone.GRPCIndex(index_name)
    query_embedding = create_embedding(text=query,model = args.embeddings_model)
    res = index.query(query_embedding, top_k=top_n, include_metadata=True)
    contexts = [
        x['metadata']['text'] for x in res['matches']
    ]
    return contexts
 

def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 100,
):
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding = create_embedding(text=query,model = args.embeddings_model)

    strings_and_relatednesses = [
        (
            row["Content"],
            relatedness_fn(query_embedding, ast.literal_eval(row["Embeddings"])),
        )
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]

def create_augmented_query_from_df(query,df):
    strings, relatednesses = strings_ranked_by_relatedness(query, df, top_n=args.top_n)
    # Creating Context from retrieved data
    augmented_query = "\n\n---\n\n".join(strings) + "\n\n-----\n\n" + query
    return augmented_query

def create_augmented_query_from_pinecone(query):
    contexts = retrieve_related_docs_from_pinecone(query,top_n=args.top_n)
    augmented_query = "\n\n---\n\n".join(contexts) + "\n\n-----\n\n" + query
    return augmented_query

@app.route("/")
def root():
    return render_template("UI.html")


@app.route("/generateAnswer", methods=["POST"])
def generate_answer():
    query = request.form.get("query")
    language = request.form.get("language")
    augmented_query = create_augmented_query_from_df(query,df)
    #augmented_query = create_augmented_query_from_pinecone(query)
    ## Creating the prompt for model
    primer = """You are Q&A bot. A highly intelligent system that answers
    user questions based on the information provided by the user above
    each question. If the information can not be found in the information
    provided by the user you truthfully say "I don't know". 
    """

    text, usage = create_chat_completion(
        messages=[
            {"role": "system", "content": primer},
            {
                "role": "user",
                "content": augmented_query + "\n Answer in {}".format(language),
            },
        ],
        model = args.chat_model,
        temperature=args.temperature
    )

    return jsonify({"answer": text})


if __name__ == "__main__":
    args = parse_args()
    setup_logging(logger_config_file=args.logger_config_file)
    app.run(host="0.0.0.0", port=8000)
