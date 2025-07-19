# Import the FastAPI app from test_app.py
from test_app import app

# This file exists to satisfy Hugging Face Spaces' Dockerfile
# which expects: uvicorn main:app
# Using test_app.py to isolate the router import issue 