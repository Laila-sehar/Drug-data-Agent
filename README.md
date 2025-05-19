# Agentic AI for Bioinformatics

## Overview
Wraps KEGG REST API in an agentic AI module using LangChain.

## Structure
- `config.py` – loads env vars  
- `tools.py` – KEGG wrappers  
- `cache.py` – LRU caching  
- `main.py` – agent orchestration  
- `tests/` – unit & integration tests  

## Setup
```bash
poetry install
