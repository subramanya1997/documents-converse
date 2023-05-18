# -*- coding: utf-8 -*-
"""
Created on Wed May 10 22:31:12 2023

@author: Tasheer
"""

from google.api_core.client_options import ClientOptions
from google.cloud import documentai

project_id = 'PROJECT-ID'
location = 'LOCATION'
processor_id = 'PROCESSOR ID' #  Create processor before running sample

def convertPDFToText(file_path):
    
    mime_type = 'application/pdf' 
    
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    
    client = documentai.DocumentProcessorServiceClient(client_options=opts)
    
    name = client.processor_path(project_id, location, processor_id)
    
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
    