"""Uvicorn entry point for the local synthetic integration service."""

from src.integration.service import create_app

app = create_app()
