# Knowledge Base API Documentation

## Overview

The Retail Knowledge Base is a centralized system for managing and accessing retail operations documentation, particularly focused on shrink prevention and inventory management. This API provides programmatic access to the knowledge base for integration with other applications.

## Components

1. **Knowledge Base Service** (`service.py`)
   - Core functionality for document management
   - Vector storage and retrieval
   - Category management
   - Document statistics

2. **REST API** (`api.py`)
   - HTTP interface for the knowledge base
   - Support for search, statistics, and health checks
   - JSON-based responses
   - Swagger/OpenAPI documentation

3. **CLI Tool** (`cli.py`)
   - Command-line management interface
   - Document import capabilities
   - Search functionality
   - Statistics reporting

## Quick Start Guide

1. **Installation**
```bash
pip install -r requirements.txt
```

2. **Start the API Server**
```bash
python -m knowledge_base.api
```

3. **Use the CLI Tool**
```bash
# Add documents
python -m knowledge_base.cli add-directory ./docs/shrink -c shrink_docs

# Search
python -m knowledge_base.cli search "What is shrink?"

# View stats
python -m knowledge_base.cli stats
```

## Integration Examples

See the following documentation files for detailed integration guides:
- [API Reference](api.md)
- [Service Integration](service.md)
- [CLI Reference](cli.md)