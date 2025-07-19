# Import the FastAPI app from app.py
from app import app

# This file exists to satisfy Hugging Face Spaces' Dockerfile
# which expects: uvicorn main:app
# The actual app is defined in app.py 