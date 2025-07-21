"""Main entrypoint for Grant Research AI API server."""

from fastapi import FastAPI

from .endpoints import router

app = FastAPI(title="Grant Research AI API")
app.include_router(router)

# To run: uvicorn src.grant_ai.api.main:app --reload
