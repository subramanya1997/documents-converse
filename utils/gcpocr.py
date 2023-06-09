# -*- coding: utf-8 -*-
"""
Created on Wed May 10 22:31:12 2023

@author: Tasheer
"""
import os
import json
from google.api_core.client_options import ClientOptions
from google.cloud import documentai


class GCPOCR_Credentials:
    def __init__(self):
        self._project_id = self.get_project_id_from_config()
        self._location = os.environ["GOOGLE_PROJECT_LOCATION"]
        self._processor_id = os.environ["GOOGLE_PROCESSOR_ID"]

    def get_project_id_from_config(self):
        with open(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]) as f:
            data = json.load(f)
        return data["project_id"]

    @property
    def project_id(self):
        return self._project_id

    @property
    def location(self):
        return self._location

    @property
    def processor_id(self):
        return self._processor_id


def convertPDFToText(file_path):
    extention = file_path.split(".")[-1].strip()
    if extention == "pdf":
        mime_type = "application/pdf"
    elif extention == "png":
        mime_type = "image/png"
    elif extention == "jpg" or extention == "jpeg":
        mime_type = "image/jpeg"
    opts = ClientOptions(
        api_endpoint=f"{gcpocr_cred.location}-documentai.googleapis.com"
    )
    client = documentai.DocumentProcessorServiceClient(client_options=opts)
    name = client.processor_path(
        gcpocr_cred.project_id, gcpocr_cred.location, gcpocr_cred.processor_id
    )
    # Read the file into memory
    with open(file_path, "rb") as image:
        image_content = image.read()
    # Load Binary Data into Document AI RawDocument Object
    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)
    # Configure the process request
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = client.process_document(request=request)
    # For a full list of Document object attributes, please reference this page:
    # https://cloud.google.com/python/docs/reference/documentai/latest/google.cloud.documentai_v1.types.Document
    document = result.document
    text = document.text
    return text


gcpocr_cred = GCPOCR_Credentials()
