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
import ast
from llm_openai import create_chat_completion, create_embedding
from flask_cors import CORS

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load Embeddings
df = pd.read_csv("data/DocumentsEmbeddings.csv")


def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 100,
):
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding = create_embedding(text=query)

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


@app.route("/")
def root():
    return render_template("UI.html")


@app.route("/generateAnswer", methods=["POST"])
def generate_answer():
    query = request.form.get("query")
    language = request.form.get("language")

    strings, relatednesses = strings_ranked_by_relatedness(query, df, top_n=3)
    # Creating Context from retrieved data
    augmented_query = "\n\n---\n\n".join(strings) + "\n\n-----\n\n" + query
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
        ]
    )

    return jsonify({"answer": text})


if __name__ == "__main__":
    args = parse_args()
    setup_logging(logger_config_file=args.logger_config_file)
    app.run(host="0.0.0.0", port=8000)
