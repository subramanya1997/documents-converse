"""
   Created on Mon May 29 2023
   Copyright (c) 2023 Subramanya N
"""
import os
from datetime import datetime
import logging
from utils import parse_args, setup_logging, validate_zip_file, process_zip
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from llm_openai import create_chat_completion, create_embeddings
from pineconesearch import pinecone_search

logger = logging.getLogger(__name__)
app = Flask(__name__)

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/uploadzip", methods=["POST"])
def upload_zip():
    if 'file' not in request.files:
        return jsonify({"error": "No file selected for uploading"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400
    
    if file:
        curr_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{secure_filename(file.filename).split('.zip')[0]}_{curr_timestamp}.zip"
        if not app.config['use_cloud_storage']:
            if not os.path.exists(app.config['upload_folder']):
                os.makedirs(app.config['upload_folder'])
            file.save(os.path.join(app.config['upload_folder'], filename))
        
        return jsonify({
            "message": "File successfully uploaded",
            "filename": filename
        }), 200
    
@app.route("/validateuploadedzip", methods=["GET"])
def validate_uploaded_zip():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({"error": "No filename provided"}), 400
    file_path = os.path.join(app.config['upload_folder'], filename)
    if validate_zip_file(file_path):
        return jsonify({"message": "File is valid"}), 200
    else:
        return jsonify({"error": "File is invalid"}), 400
    

@app.route("/deletefile", methods=["POST"])
def delete_file():
    filename = request.form.get("filename")
    if not filename:
        return jsonify({"error": "No filename provided"}), 400
    file_path = os.path.join(app.config['upload_folder'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"message": "File deleted successfully"}), 200
    else:
        return jsonify({"error": "File does not exist"}), 400

@app.route("/processuploadedzip", methods=["GET"])
def process_uploaded_zip():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({"error": "No filename provided"}), 400
    file_path = os.path.join(app.config['upload_folder'], filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File does not exist"}), 400
    if not process_zip(file_path):
        return jsonify({"error": "No text extracted from the file"}), 400
    return jsonify({"message": "File processed successfully"}), 200

@app.route("/generateAnswer", methods=["POST"])
def generate_answer():
    query = request.form.get("query")
    language = request.form.get("language")
    query_embed = create_embeddings(text=query)[0]
    augmented_query = pinecone_search.query_and_combine(query_embed, top_k=app.config["top_n"])
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
        model = app.config["chat_model"],
        temperature=app.config["temperature"],
    )

    return jsonify({"answer": text})


if __name__ == "__main__":
    args = parse_args()
    setup_logging(logger_config_file=args.logger_config_file)
    # Update config
    app.config.update(args.__dict__)
    CORS(app)
    app.run(host="0.0.0.0", port=8000)
