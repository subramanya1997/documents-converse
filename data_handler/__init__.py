import os
import pinecone
from data_handling import *

# find API key in console at app.pinecone.io
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
# find ENV (cloud region) next to API key in console
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')

GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

pinecone.init(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENVIRONMENT
)

