# 🇵🇹 Portuguese Wikipedia Hybrid Search Engine (IR + Neural Reranking + RAG)

A full-stack **information retrieval system for Portuguese Wikipedia**, combining classical inverted-index search, neural reranking, and retrieval-augmented generation (RAG). The project demonstrates an end-to-end search engine pipeline inspired by modern production IR systems.

---

## Overview

This project implements a **hybrid search engine architecture** capable of:

- Efficient large-scale document indexing (2.5GB+ inverted index)
- Fast lexical retrieval using BM25
- Neural reranking for improved relevance
- Query understanding and rewriting
- Retrieval-Augmented Generation (RAG) for question answering in Portuguese
- Snippet-level semantic extraction for user-friendly results

The system is designed as a **production-style IR pipeline**, combining classical information retrieval with modern neural and LLM-based techniques.

---

## Tech Stack

- Python  
- SQLite (forward index storage)  
- NumPy / SciPy (IR computations)  
- PyTorch (neural reranker)  
- HuggingFace Transformers  
- BM25 ranking (custom implementation)  
- SPIMI indexing (disk-based inverted index)  
- Google Gemini API (RAG + query rewriting)  
- CUDA (GPU acceleration for inference)  
- JSONL / custom file-based storage system  

## Project Organization

The project is structured as a production-style information retrieval system, separating core retrieval logic, API services, and user-facing interfaces.

```text
Assignment 2/
├── src/
│   └── sapien/
│       ├── core/                          # Core IR pipeline
│       │   ├── indexer.py                 # SPIMI indexing + inverted index construction
│       │   ├── tokenizer.py               # Shared tokenizer for indexing and querying
│       │   ├── search_engine.py           # BM25 retrieval engine
│       │   ├── neural_reranker.py         # MiniLM neural reranking
│       │   ├── rag_agent_gemini.py        # Gemini-based RAG answer generation
│       │   ├── rag_agent_groq.py          # Groq-based RAG prototype
│       │   ├── model.py                   # Document models
│       │   ├── logging.py                 # Logging utilities
│       │   └── limit_memory.py            # Memory monitoring and constraints
│       │
│       ├── entrypoints/                   # Application entrypoints
│       │   ├── cli.py                     # Command-line indexing interface
│       │   ├── asgi.py                    # ASGI server entrypoint
│       │   │
│       │   └── api/                       # FastAPI REST API
│       │       ├── app.py                 # FastAPI application setup
│       │       ├── model.py               # API request/response models
│       │       │
│       │       └── routes/
│       │           ├── search.py          # Search endpoints
│       │           └── healthcheck.py     # Service health monitoring
│
├── output/                                # Generated index files and artifacts
│   ├── block_*.jsonl                      # Intermediate SPIMI blocks
│   ├── documents_stats.jsonl              # Document length statistics
│   └── indexer_metadata.jsonl             # Index metadata
│
├── static_pages/
│   └── index.html                         # Frontend interface connected via REST API
│
├── ptwiki-articles-with-redirects.arrow   # Portuguese Wikipedia dataset
│
├── requirements.txt
├── README.md
└── .gitignore
```

## System Architecture
User Query
↓
Tokenizer (same for indexing & search)
↓
Inverted Index Retrieval (BM25)
↓
Top-100 Candidate Documents
↓
Neural Reranker (MiniLM)
↓
Top-K Final Results
↓
Optional Enhancements:
├── Snippet Extraction
├── Query Rewriting (LLM)
└── RAG Answer Generation




# Core Information Retrieval System

## Tokenization Pipeline

The tokenizer ensures consistent preprocessing across indexing and querying:

- lowercase conversion  
- URL removal  
- email removal  
- tokenization  
- alphanumeric splitting (optional)  
- number removal (optional)  
- stopword removal (optional)  
- stemming (optional)  
- minimum token length filtering  

### Optimizations
- precompiled regex for URLs/emails  
- LRU caching for stemming (100k entries)  
- indexing speed improved from ~60 min → ~40 min  

### Default Configuration

```python
lowercase = True
remove_urls = True
remove_emails = True
separate_alphanumerics = True
remove_numbers = True
min_token_length = 1
stopwords = False
stemming = True
```


## Indexing System

The system builds a full disk-based inverted index:
```
Generated Files
 - final_index.jsonl → inverted index (term → postings list)
 - forward_index.db → SQLite document store
 - documents_metadata.jsonl → corpus statistics
 - documents_stats.jsonl → document lengths
 - indexer_metadata.jsonl → configuration metadata
 - offset_index.json → fast lookup index
```
To handle memory constraints (≤2GB RAM), the system uses SPIMI.


## Disk-Based Search Optimization
```
To support large indexes (~2.5GB):
- offset_index.json stores term → byte offset
- system performs direct file seek into final_index.jsonl
- avoids loading full index into memory
```

## BM25 Ranking
```
Search is performed using BM25:
query is tokenized using same pipeline as indexing
postings retrieved via offset index
documents scored using BM25
results sorted by relevance
```

## Similarity Search
```
A document-to-query expansion feature:
document is converted into TF-IDF representation
top weighted terms extracted
terms used as pseudo-query
BM25 applied to retrieve similar documents
```


## Neural Reranking System
The system uses mmarco-mMiniLMv2-L12-H384-v1, a transformer model optimized for semantic ranking tasks.

### Reranking Pipeline
BM25 retrieves top 100 documents
Neural model reranks candidates
Top-K documents returned to user

### Performance Optimization
GPU Acceleration
CPU inference: ~10 seconds/query
GPU (RTX 3050): ~1.4–1.9 seconds/query

Implemented using CUDA-enabled PyTorch inference.


## Retrieval-Augmented Generation (RAG)
Initial model was Groq openai/gpt-oss-20b (limited by token constraints), but in the end we settled for gemini-2.5-flash and gemini-2.5-flash-lite.

###
Step 1 — Query Classification
Respond only with "yes" or "no".
Is this sentence a question?

Step 2 — Answer Generation
If the query is a question:
Use only the following text to answer the question.
If not found in the text, respond:
"Desculpe. Eu não sei."


## Additional AI Enhancements
### Best Snippet Extraction
After reranking:
split document into paragraphs
score each paragraph using neural reranker
select most relevant paragraph
```
Result:

focused preview of document
faster user consumption of results
```
### Query Improvement (LLM-assisted)

The system suggests improved queries:
Rules:
valid query → unchanged
unclear query → corrected version
output always in Portuguese


## Usage

### Running the Search API

Start the FastAPI server:
```bash
uv run uvicorn sapien.entrypoints.asgi:app --reload
```
- **Static Web Interface**: `http://localhost:8000`
- **API docs**: `http://localhost:8000/docs`

### Running the CLI Indexer

The CLI indexer runs with memory monitoring enabled to enforce the 2GB memory limit:
```bash
uv run cli [arguments]
```
OR
```bash
uv run src/sapien/entrypoints/cli [arguments]
```


## Teachers
- José Luís Oliveira - jlo@ua.pt
- Tiago Almeida - tiagomeloalmeida@ua.pt
