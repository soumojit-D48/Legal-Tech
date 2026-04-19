from fastapi import FastAPI
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="LegalTech AI Service",
    description="AI and NLP pipelines for contract analysis",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ai"}


@app.get("/")
async def root():
    return {"message": "LegalTech AI Service", "version": "1.0.0"}
