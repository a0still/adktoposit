# tools.py
import os
import logging
from typing import List, Optional
from langchain.tools import tool
# We switch from Chroma (Local) to Vertex AI Search (Cloud)
# NEW / CORRECT - VertexAISearchRetriever is in langchain-google-community
from langchain_google_community import VertexAISearchRetriever
from google.cloud import bigquery
from src.report_recommender import ReportRecommender

# Setup logging
logger = logging.getLogger('adk_chat.tools')

# Initialize report recommender
report_recommender = ReportRecommender()

# Configuration - Pull from Env or use defaults
PROJECT_ID = os.getenv('GCP_PROJECT', 'wmt-us-gg-shrnk-prod')
LOCATION = "global" 
# *** REVERT TO DATA STORE ID (The raw ID, not the App ID) ***
DATA_STORE_ID = "positirr_1764279062880"

# Initialize BigQuery client
try:
    client = bigquery.Client()
except Exception as e:
    logger.error(f"Error initializing BigQuery client: {str(e)}")

# Initialize Vertex AI Search Retriever (Cloud Knowledge Base)
try:
    # We must use 'data_store_id' to satisfy the library validation
    retriever = VertexAISearchRetriever(
        project_id=PROJECT_ID,
        location_id=LOCATION,
        data_store_id=DATA_STORE_ID,  # <--- Switch back to this
        max_documents=3,
        engine_data_type=0 
    )
    logger.info(f"Vertex AI Search Retriever initialized for store: {DATA_STORE_ID}")
except Exception as e:
    logger.error(f"Error initializing Vertex AI Search: {str(e)}")
    retriever = None

@tool("retrieve_knowledge")
def retrieve_knowledge(query: str) -> str:
    """
    Useful for finding relevant information about retail operations, inventory
    management, and shrink prevention from the knowledge base.
    
    Args:
        query (str): The search query (e.g. "What causes high markdowns?")
        
    Returns:
        str: Relevant information found in the knowledge base
    """
    try:
        logger.info(f"[TOOL] Searching Cloud Knowledge Base for: {query}")
        
        if retriever is None:
            return "Knowledge base connection is not available."
        
        # Invoke the Cloud Search
        docs = retriever.invoke(query)
        
        if not docs:
            logger.info("[TOOL] No documents found.")
            return "I searched the knowledge base but couldn't find specific details on that topic."
        
        # Format the results
        results = []
        for i, doc in enumerate(docs):
            # metadata usually contains 'source' or 'id'
            source = doc.metadata.get('source', f'Document {i+1}')
            # Clean up source path for display (e.g. 'gs://bucket/folder/file.md' -> 'file.md')
            if '/' in source:
                source = source.split('/')[-1]
                
            results.append(f"**Source:** {source}\n{doc.page_content}\n")
            
        combined_results = "\n---\n".join(results)
        logger.info(f"[TOOL] Found {len(docs)} documents.")
        
        return combined_results
        
    except Exception as e:
        logger.error(f"[TOOL ERROR] {str(e)}", exc_info=True)
        return f"I encountered an error searching the knowledge base: {str(e)}"


@tool("recommend_report")
def recommend_report(user_query: str) -> str:
    """
    Analyzes a user's query to recommend the appropriate Custom Report.
    Use this when users ask for specific data, details, transactions, or want to see information
    that would come from a report.
    """
    try:
        logger.info(f"[REPORT TOOL] Analyzing query: {user_query}")
        
        recommendation = report_recommender.analyze_query(user_query)
        
        if recommendation and recommendation['confidence'] > 0.5:
            report_name = recommendation['report_name']
            params = recommendation.get('extracted_params', {})
            
            response = f"📊 **Report Recommendation:** {report_name}\n\n"
            response += "This report is available in the **Custom Reports** tab.\n\n"
            
            if params:
                response += "**Detected Parameters:**\n"
                for k, v in params.items():
                    response += f"- {k.replace('_', ' ').title()}: {v}\n"
                response += "\n"
            
            response += "**What this report shows:**\n"
            for use_case in recommendation['use_cases'][:3]:
                response += f"- {use_case}\n"
            
            return response
        else:
            return "No specific report recommendation found. Please check the Custom Reports tab for available options."
            
    except Exception as e:
        logger.error(f"[REPORT TOOL ERROR] {str(e)}", exc_info=True)
        return "Unable to provide report recommendation at this time."