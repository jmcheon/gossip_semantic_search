from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services import search_service

router = APIRouter()


class QueryResquest(BaseModel):
    query: str
    top_k: int


class SearchResult(BaseModel):
    link: str
    score: float


@router.post("/embedding", response_model=List[float])
async def get_embedding(request: QueryResquest):
    try:
        query_embedding = search_service.generate_embedding(request.query)
        return query_embedding.tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[SearchResult])
async def search(request: QueryResquest):
    try:
        query_embedding = search_service.generate_embedding(request.query)
        # print(f"query embedding: {query_embedding}")
        res = search_service.search_links(query_embedding, request.top_k)
        # print(res)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
