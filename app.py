"""
   Created on Mon May 29 2023
   Copyright (c) 2023 Subramanya N
"""
import logging
from utils import parse_args, setup_logging
from flask import Flask, render_template, request, jsonify
import pandas as pd
import pinecone
from llm_openai import create_chat_completion, create_embedding
from flask_cors import CORS
from data_handler import *

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def retrieve_related_docs_from_pinecone(
        query: str,
        top_n: int = 5
):
    index_name = 'lab101'
    index = pinecone.GRPCIndex(index_name)
    response = create_embedding(text=query,model = args.embeddings_model)
    query_embedding = response["data"][0]["embedding"]
    res = index.query(query_embedding, top_k=top_n, include_metadata=True)
    contexts = [
        x['metadata']['text'] for x in res['matches']
    ]
    return contexts

def create_augmented_query_from_pinecone(query):
    contexts = retrieve_related_docs_from_pinecone(query,top_n=args.top_n)
    augmented_query = "\n\n---\n\n".join(contexts) + "\n\n-----\n\n" + query
    return augmented_query

@app.route("/")
def root():
    return render_template("index.html")


@app.route("/generateAnswer", methods=["POST"])
def generate_answer():
    return jsonify({"answer": "Hello World"})
    query = request.form.get("query")
    language = request.form.get("language")
    augmented_query = create_augmented_query_from_pinecone(query)
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
