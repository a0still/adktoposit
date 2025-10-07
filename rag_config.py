# rag_config.py

import os

# Directory containing your markdown training documents
DOC_DIRECTORY = 'Shrink_Documentation'

# Directory to store the Chroma vector database
VECTOR_DB_DIRECTORY = 'vector_db'

# Configuration for the text splitter
CHUNK_SIZE = 1000  # Adjust based on testing - start around 500-1500
CHUNK_OVERLAP = 200 # Helps maintain context between chunks

# Name of the Vertex AI embedding model to use
EMBEDDING_MODEL_NAME = "text-embedding-005"

# Google Cloud Project ID and Location for Vertex AI
GCP_PROJECT = "wmt-e2e-datafoundations-dev" 
GCP_LOCATION = "us-central1"     

# Ensure the documentation directory exists
if not os.path.exists(DOC_DIRECTORY):
    print(f"Error: Documentation directory '{DOC_DIRECTORY}' not found.")
    print("Please create this directory and place your .md files inside.")