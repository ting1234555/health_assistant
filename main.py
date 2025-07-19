from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ai_router

app = FastAPI(title="Health Assistant API")


import sys
print("PYTHONPATH:", sys.path)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由 - 暫時只包含 ai_router
app.include_router(ai_router.router)

@app.get("/")
async def root():
    return {"message": "Health Assistant API is running"}

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "routers": ["ai_router"],
        "endpoints": [
            "/ai/analyze-food-image/",
            "/ai/analyze-food-image-with-weight/",
            "/ai/health"
        ]
    } 