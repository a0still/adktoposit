# tools.py
import platform
from typing import List, Tuple
from google.cloud import bigquery
from langchain.tools import tool
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import Chroma
import rag_config

# Initialize BigQuery client (credentials should be picked up from the environment variable)
try:
    client = bigquery.Client()
except Exception as e:
    print(f"Error initializing BigQuery client: {str(e)}")

# Initialize the embedding model
try:
    embeddings = VertexAIEmbeddings(
        model_name=rag_config.EMBEDDING_MODEL_NAME,
        project=rag_config.GCP_PROJECT,
        location=rag_config.GCP_LOCATION
    )
except Exception as e:
    print(f"Error initializing embeddings: {str(e)}")

@tool("retrieve_training_docs")
def retrieve_training_docs(query: str) -> str:
    """
    Retrieves relevant documentation based on the query using embeddings search.
    Args:
        query (str): The search query
    Returns:
        str: Retrieved relevant documentation text
    """
    try:
        vectordb = Chroma(
            persist_directory=rag_config.VECTOR_DB_DIRECTORY,
            embedding_function=embeddings
        )
        
        # Search the vector database
        docs = vectordb.similarity_search(
            query,
            k=3  # Number of documents to retrieve
        )
        
        # Format the results
        results = []
        for doc in docs:
            results.append(doc.page_content)
        
        return "\n\n---\n\n".join(results)
        
    except Exception as e:
        return f"Error retrieving documentation: {str(e)}"