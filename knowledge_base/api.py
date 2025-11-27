"""
Knowledge Base API
FastAPI service for accessing the knowledge base.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from knowledge_base.service import KnowledgeBaseService
import uvicorn
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Retail Knowledge Base API")
kb_service = KnowledgeBaseService()

class SearchQuery(BaseModel):
    query: str
    category: Optional[str] = None
    max_results: Optional[int] = 3
    min_relevance: Optional[float] = 0.5

class SearchResponse(BaseModel):
    results: List[Dict]
    total_results: int
    category: Optional[str]
    query: str

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "knowledge-base"}

@app.get("/stats")
async def get_stats():
    """Get knowledge base statistics."""
    try:
        stats = kb_service.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
async def get_categories():
    """Get available categories."""
    try:
        categories = kb_service.get_categories()
        return {"categories": categories}
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search(query: SearchQuery) -> SearchResponse:
    """
    Search the knowledge base.
    """
    try:
        results = kb_service.search(
            query=query.query,
            category=query.category,
            max_results=query.max_results,
            min_relevance=query.min_relevance
        )
        
        return SearchResponse(
            results=results,
            total_results=len(results),
            category=query.category,
            query=query.query
        )
    except Exception as e:
        logger.error(f"Error searching: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("knowledge_base.api:app", host="0.0.0.0", port=8000, reload=True)