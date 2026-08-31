from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request

from search_engine.api.auth import verify_api_key
from search_engine.api.rate_limiter import RateLimiter, rate_limit_dependency

router = APIRouter()

_search_rate_limiter = RateLimiter(max_requests=30, window_seconds=60.0)
_suggest_rate_limiter = RateLimiter(max_requests=60, window_seconds=60.0)

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/search", dependencies=[Depends(rate_limit_dependency(_search_rate_limiter))])
def search(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query"),
    source_type: str | None = Query(
        default=None, description="Filter results to one source type: txt, pdf, html, markdown"
    ),
    top_k: int = Query(default=10, ge=1, le=100),
    x_api_key: str | None = Header(default=None),
):
    engine = request.app.state.engine
    results = engine.search_ranked(q, source_type=source_type, top_k=top_k)

    history = request.app.state.history
    history.record(api_key=x_api_key or "anonymous", query=q, result_count=len(results))

    return {"query": q, "count": len(results), "results": results}


@router.get(
    "/suggest", dependencies=[Depends(rate_limit_dependency(_suggest_rate_limiter))]
)
def suggest(
    request: Request,
    prefix: str = Query(..., min_length=1, description="Prefix to autocomplete"),
    limit: int = Query(default=10, ge=1, le=50),
):
    engine = request.app.state.engine
    return {"prefix": prefix, "suggestions": engine.suggest(prefix, limit=limit)}

@router.post("/index")
def index_directory(directory: str, request: Request, api_key: str = Depends(verify_api_key)):
    engine = request.app.state.engine
    try:
        count = engine.index_directory(directory)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "indexed": count,
        "document_count": engine.document_count,
        "vocabulary_size": engine.vocabulary_size,
    }


@router.get("/stats")
def stats(request: Request):
    engine = request.app.state.engine
    return {
        "document_count": engine.document_count,
        "vocabulary_size": engine.vocabulary_size,
    }

@router.get("/history")
def history(request: Request, api_key: str = Depends(verify_api_key), limit: int = 50):
    store = request.app.state.history
    return {
        "api_key": api_key,
        "total_queries": store.total_queries(api_key),
        "recent": store.history_for(api_key, limit=limit),
    }

@router.get("/analytics")
def analytics(request: Request, api_key: str = Depends(verify_api_key)):
    store = request.app.state.history
    return {
        "total_queries": store.total_queries(),
        "top_queries": store.top_queries(limit=10),
        "queries_per_user": store.queries_per_user(),
        "average_result_count": store.average_result_count(),
    }