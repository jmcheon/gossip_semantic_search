from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PINECONE_API_KEY: str
    PINECONE_ENV: str
    PINECONE_INDEX_NAME: str
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
