# process_docs.py
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import Chroma
import rag_config
from dotenv import load_dotenv

# Load environment variables (needed for Vertex AI authentication)
load_dotenv()

def process_and_embed_docs():
    """
    Loads, chunks, embeds documents from the specified directory,
    and stores them in a Chroma vector database.
    """
    print(f"Loading documents from directory: {rag_config.DOC_DIRECTORY}")
    try:
        # Initialize the loader for markdown files
        loader = DirectoryLoader(
            rag_config.DOC_DIRECTORY,
            glob="**/*.md",
            loader_cls=TextLoader
        )
        documents = loader.load()
        print(f"Loaded {len(documents)} documents.")

    except Exception as e:
        print(f"Error loading documents: {str(e)}")
        return False

    if not documents:
        print("No documents found to process.")
        return False

    print(f"Splitting documents into chunks...")
    # Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=rag_config.CHUNK_SIZE,
        chunk_overlap=rag_config.CHUNK_OVERLAP,
        length_function=len
    )

    # Split documents into chunks
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    print(f"Initializing embedding model: {rag_config.EMBEDDING_MODEL_NAME}")
    try:
        embeddings = VertexAIEmbeddings(
            model_name=rag_config.EMBEDDING_MODEL_NAME,
            project=rag_config.GCP_PROJECT,
            location=rag_config.GCP_LOCATION
        )
    except Exception as e:
        print(f"Error initializing embedding model: {str(e)}")
        return False

    print(f"Creating/loading Chroma vector database...")
    try:
        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=rag_config.VECTOR_DB_DIRECTORY
        )
        vectordb.persist()
        print(f"Successfully created and persisted vector database.")
        return True

    except Exception as e:
        print(f"Error creating vector database: {str(e)}")
        return False

if __name__ == "__main__":
    process_and_embed_docs()