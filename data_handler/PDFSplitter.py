# -*- coding: utf-8 -*-
"""
Created on Thu May 11 00:18:19 2023

@author: Tasheer
"""

import os
from PyPDF2 import PdfReader, PdfWriter
import GCPOCR
import tqdm

def split_pdf(input_path, output_prefix, max_pages):
    with open(input_path, 'rb') as input_file:
        pdf = PdfReader(input_file)
        total_pages = len(pdf.pages)

        num_chunks = (total_pages + max_pages - 1) // max_pages

        for i in range(num_chunks):
            start_page = i * max_pages
            end_page = min((i + 1) * max_pages, total_pages)

            output_path = f"{output_prefix}$${i+1}.pdf"
            with open(output_path, 'wb') as output_file:
                output_pdf = PdfWriter()
                for page in range(start_page, end_page):
                    output_pdf.add_page(pdf.pages[page])

                output_pdf.write(output_file)
            print(f"Created: {output_path}")
            text = GCPOCR.convertPDFToText(output_path)
            #use the text further to create chunks or wait until all the splitting is done and then combine the text files and then do the chunking

def process_directory(base_dir, max_pages):
    for root, dirs, files in os.walk(base_dir):
        for file in tqdm.tqdm(files):
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                try:
                    with open(pdf_path, 'rb') as input_file:
                        pdf = PdfReader(input_file)
                        total_pages = len(pdf.pages)
                except:
                    #Handling when the PDFs are corrupt
                    print("PDF Not good")
                    print(pdf_path)
                    os.remove(pdf_path)
                    continue
                if total_pages > max_pages:
                    output_prefix = pdf_path.split('.pdf')[0]
                    split_pdf(pdf_path, output_prefix, max_pages)
                else:
                    text = GCPOCR.convertPDFToText(pdf_path)
                    #use the text further to create chunks

# Example usage
base_directory = 'BASE_PATH'
max_pages_per_pdf = 15

process_directory(base_directory, max_pages_per_pdf)
