import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import base64
from io import BytesIO
from PIL import Image
import json
from dotenv import load_dotenv
from app.database import engine, Base
from app.routers import ai_router, meal_router

# 設定 Hugging Face 及 Torch 快取目錄
os.environ["TRANSFORMERS_CACHE"] = "/tmp/hf_cache"
os.environ["HF_HOME"] = "/tmp/hf_home"
os.environ["TORCH_HOME"] = "/tmp/torch_home"
os.environ["HF_DATASETS_CACHE"] = "/tmp/hf_datasets"
os.environ["XDG_CACHE_HOME"] = "/tmp/xdg_cache"
os.environ["DATASET_CACHE_DIR"] = "/tmp/dataset_cache"

# 創建資料庫表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Health Assistant API")
app.include_router(ai_router.router)
app.include_router(meal_router.router) 

# Load environment variables
load_dotenv()

# CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Health Assistant API is running"}

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "routers": ["ai_router", "meal_router"],
        "endpoints": [
            "/ai/analyze-food-image/",
            "/ai/analyze-food-image-with-weight/",
            "/ai/health"
        ]
    } 
