from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .app.search import generate_embedding, search_links

app = FastAPI()


# List of allowed origins
origins = [
    "http://localhost:3000",
    "http://localhost:8501",
]


def add(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],  # Allows all HTTP methods
        allow_headers=["*"],  # Allows all headers
    )


add(app)


class QueryResquest(BaseModel):
    query: str
    top_k: int


class SearchResult(BaseModel):
    link: str
    score: float


@app.post("/embedding", response_model=List[float])
async def get_embedding(request: QueryResquest):
    try:
        query_embedding = generate_embedding(request.query)
        return query_embedding.tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=List[SearchResult])
async def search(request: QueryResquest):
    try:
        query_embedding = generate_embedding(request.query)
        # print(f"query embedding: {query_embedding}")
        res = search_links(query_embedding, request.top_k)
        # print(res)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
