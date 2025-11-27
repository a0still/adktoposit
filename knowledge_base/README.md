# Knowledge Base Structure

This directory contains various types of knowledge sources used by our ADK agents.

## Current Knowledge Base Contents

### Shrink Documentation
Located in `/markdown/shrink_docs/`:
* Core Concepts (01_core_concepts/)
* Processes and Procedures (02_processes/)
* Systems Documentation (03_systems/)
* Reference Materials (00_references/)

## Directory Structure

- `/markdown`: Contains Markdown documentation files
  - Use for general documentation, guides, and structured knowledge
  - Ideal for human-readable content that will be used by agents

- `/rag_documents`: RAG (Retrieval Augmented Generation) documents
  - Contains processed documents for RAG systems
  - Includes embeddings and vector stores
  - Used by agents for context-aware responses

- `/datasets`: Structured datasets
  - Contains CSV, JSON, or other structured data files
  - Used by Data Science agents for analysis and insights
  - Includes both raw and processed datasets

- `/config`: Configuration files
  - Contains configuration for different knowledge bases
  - Includes embedding settings, chunking parameters, etc.
  - RAG system configurations and indexes

## Usage

1. For adding new knowledge:
   - Place raw markdown files in `/markdown`
   - Put RAG documents in `/rag_documents`
   - Store datasets in `/datasets`
   - Update configurations in `/config`

2. For using with agents:
   - Update `rag_config.py` to point to new knowledge sources
   - Use the appropriate agent tools to access the knowledge
   - Ensure proper documentation of new additions

## Inspiration

Based on Google's ADK samples:
- Data Science Agent: https://github.com/google/adk-samples/tree/main/python/agents/data-science
- Knowledge Getter patterns