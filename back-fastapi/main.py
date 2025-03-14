from app.controllers import embedding_controller, search_controller
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app.include_router(search_controller.router)
app.include_router(embedding_controller.router)
