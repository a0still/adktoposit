"""
Knowledge Base Service
A modular service for managing and accessing the retail knowledge base.
"""

import os
from typing import List, Dict, Optional
from langchain.docstore.document import Document
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import MarkdownTextSplitter
import logging
from datetime import datetime

from rag_config import (
    KNOWLEDGE_BASE_DIR,
    DOC_DIRECTORY,
    RAG_DIRECTORY,
    VECTOR_DB_DIRECTORY,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    GCP_PROJECT,
    GCP_LOCATION,
    EMBEDDING_MODEL_NAME
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'knowledge_base.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    """Service for managing and accessing the knowledge base."""
    
    def __init__(self):
        """Initialize the knowledge base service."""
        self.embeddings = None
        self.vector_store = None
        self.initialize_embeddings()
        self.initialize_vector_store()
        
    def initialize_embeddings(self):
        """Initialize the embedding model."""
        try:
            self.embeddings = VertexAIEmbeddings(
                model_name=EMBEDDING_MODEL_NAME,
                project=GCP_PROJECT,
                location=GCP_LOCATION
            )
            logger.info("Embeddings initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing embeddings: {str(e)}")
            raise
            
    def initialize_vector_store(self):
        """Initialize or load the vector store."""
        try:
            if os.path.exists(VECTOR_DB_DIRECTORY):
                self.vector_store = Chroma(
                    persist_directory=VECTOR_DB_DIRECTORY,
                    embedding_function=self.embeddings
                )
                logger.info("Loaded existing vector store")
            else:
                logger.info("No existing vector store found")
                self.vector_store = None
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise

    def add_documents(self, documents: List[Document], category: str = None) -> bool:
        """
        Add new documents to the knowledge base.
        Args:
            documents: List of Document objects to add
            category: Optional category for the documents
        Returns:
            bool: Success status
        """
        try:
            # Add category to metadata if provided
            if category:
                for doc in documents:
                    doc.metadata['category'] = category
                    doc.metadata['added_date'] = datetime.now().isoformat()

            # Split documents
            splitter = MarkdownTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP
            )
            
            splits = []
            for doc in documents:
                text_splits = splitter.split_text(doc.page_content)
                for split_text in text_splits:
                    splits.append(Document(
                        page_content=split_text,
                        metadata=doc.metadata
                    ))

            # Create or update vector store
            if self.vector_store is None:
                self.vector_store = Chroma.from_documents(
                    documents=splits,
                    embedding=self.embeddings,
                    persist_directory=VECTOR_DB_DIRECTORY
                )
            else:
                self.vector_store.add_documents(splits)
            
            logger.info(f"Added {len(splits)} document chunks to knowledge base")
            return True
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return False

    def search(self, query: str, 
              category: str = None, 
              max_results: int = 3, 
              min_relevance: float = 0.5) -> List[Dict]:
        """
        Search the knowledge base.
        Args:
            query: Search query
            category: Optional category to filter results
            max_results: Maximum number of results to return
            min_relevance: Minimum relevance score (0-1)
        Returns:
            List of relevant documents with metadata
        """
        try:
            if self.vector_store is None:
                return []
                
            # Perform the search
            results = self.vector_store.similarity_search_with_relevance_scores(
                query,
                k=max_results
            )
            
            # Filter and format results
            filtered_results = []
            for doc, score in results:
                if score < min_relevance:
                    continue
                if category and doc.metadata.get('category') != category:
                    continue
                    
                filtered_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'relevance_score': score
                })
                
            return filtered_results
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []

    def get_categories(self) -> List[str]:
        """Get list of available categories in the knowledge base."""
        try:
            if self.vector_store is None:
                return []
            
            # Use collection.get() to retrieve all documents and extract unique categories
            all_metadata = self.vector_store._collection.get()['metadatas']
            categories = set()
            for metadata in all_metadata:
                if metadata and 'category' in metadata:
                    categories.add(metadata['category'])
            
            return sorted(list(categories))
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            return []

    def get_document_count(self, category: str = None) -> int:
        """
        Get count of documents in the knowledge base.
        Args:
            category: Optional category to filter count
        Returns:
            int: Number of documents
        """
        try:
            if self.vector_store is None:
                return 0
                
            if category:
                # Filter by category
                return len([m for m in self.vector_store._collection.get()['metadatas'] 
                          if m and m.get('category') == category])
            else:
                # Total count
                return len(self.vector_store._collection.get()['ids'])
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            return 0

    def get_statistics(self) -> Dict:
        """Get statistics about the knowledge base."""
        try:
            stats = {
                'total_documents': self.get_document_count(),
                'categories': {},
                'last_updated': None
            }
            
            # Get counts per category
            categories = self.get_categories()
            for category in categories:
                stats['categories'][category] = self.get_document_count(category)
            
            # Get last update time
            all_metadata = self.vector_store._collection.get()['metadatas']
            dates = [m.get('added_date') for m in all_metadata if m and 'added_date' in m]
            if dates:
                stats['last_updated'] = max(dates)
            
            return stats
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}