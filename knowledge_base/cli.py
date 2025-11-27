"""
Knowledge Base Management Utility
CLI tool for managing the knowledge base.
"""

import click
import os
from pathlib import Path
from typing import List
from langchain.docstore.document import Document
from knowledge_base.service import KnowledgeBaseService
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Retail Knowledge Base Management Tool"""
    pass

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--category', '-c', help='Category for the documents')
def add_directory(directory: str, category: str = None):
    """Add all markdown files from a directory to the knowledge base."""
    try:
        kb_service = KnowledgeBaseService()
        
        # Collect markdown files
        files = list(Path(directory).rglob("*.md"))
        documents = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    rel_path = os.path.relpath(file_path, directory)
                    metadata = {
                        'source': str(rel_path),
                        'title': file_path.stem,
                        'category': category or os.path.basename(directory)
                    }
                    documents.append(Document(
                        page_content=content,
                        metadata=metadata
                    ))
                logger.info(f"Loaded {rel_path}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {str(e)}")
                
        if documents:
            success = kb_service.add_documents(documents, category)
            if success:
                logger.info(f"Successfully added {len(documents)} documents")
            else:
                logger.error("Failed to add documents")
        else:
            logger.warning("No documents found to add")
            
    except Exception as e:
        logger.error(f"Error in add_directory: {str(e)}")

@cli.command()
def stats():
    """Show knowledge base statistics."""
    try:
        kb_service = KnowledgeBaseService()
        stats = kb_service.get_statistics()
        
        click.echo("\nKnowledge Base Statistics:")
        click.echo("-" * 30)
        click.echo(f"Total Documents: {stats['total_documents']}")
        click.echo("\nDocuments by Category:")
        for category, count in stats['categories'].items():
            click.echo(f"  {category}: {count}")
        if stats['last_updated']:
            click.echo(f"\nLast Updated: {stats['last_updated']}")
            
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")

@cli.command()
@click.argument('query')
@click.option('--category', '-c', help='Filter by category')
@click.option('--max-results', '-n', default=3, help='Maximum number of results')
def search(query: str, category: str = None, max_results: int = 3):
    """Search the knowledge base."""
    try:
        kb_service = KnowledgeBaseService()
        results = kb_service.search(query, category, max_results)
        
        click.echo(f"\nSearch Results for: {query}")
        click.echo("-" * 50)
        
        if not results:
            click.echo("No results found")
            return
            
        for i, result in enumerate(results, 1):
            click.echo(f"\nResult {i}:")
            click.echo(f"Source: {result['metadata'].get('source', 'Unknown')}")
            click.echo(f"Category: {result['metadata'].get('category', 'Unknown')}")
            click.echo(f"Relevance: {result['relevance_score']:.2f}")
            click.echo("\nContent:")
            click.echo(result['content'])
            click.echo("-" * 50)
            
    except Exception as e:
        logger.error(f"Error searching: {str(e)}")

if __name__ == "__main__":
    cli()