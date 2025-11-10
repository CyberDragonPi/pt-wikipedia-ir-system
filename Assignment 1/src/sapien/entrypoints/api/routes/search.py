"""Search endpoints."""

from fastapi import APIRouter

from sapien.core.model import Document
from sapien.core.search_engine import SearchEngine
from sapien.entrypoints.api.model import SearchResponse

router = APIRouter(tags=["search engine"])


@router.get("/search")
def search(query: str, num_results: int = 10) -> SearchResponse:
    """Search for documents matching the given query."""
    searcher = SearchEngine()
    ranked = searcher.search(query)
    for document in ranked:
        print(f"DOC_ID {document['doc_id']}")
        print(f"SCORE: {document['score']}")
        print(f"TITLE: {document['title']}")
        print(f"TEXT: {document['text']}")
        print("-" * 60)
        
    return SearchResponse(
        results=[
            Document(id=1, title="Document 1", content="Content 1"),
            Document(id=2, title="Document 2", content="Content 2"),
            Document(id=3, title="Document 3", content="Content 3"),
        ]
    )


@router.get("/search_like")
def search_like(doc_id: int, num_results: int = 10) -> SearchResponse:
    """Search for documents similar to the given document ID."""
    return SearchResponse(results=[])
