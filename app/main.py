from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ai_router, meal_router
# from app.routers import ai_router_v2  # 暫時註釋掉有問題的路由器
from app.database import engine, Base
from app.routers import nutrition_router  # 引入新的營養路由器
import logging
from datetime import datetime

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建資料庫表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Health Assistant API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React 開發伺服器的位址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(ai_router.router)
# app.include_router(ai_router_v2.router)  # 暫時註釋掉有問題的路由器
app.include_router(meal_router.router)
app.include_router(nutrition_router.router, prefix="/api/nutrition", tags=["nutrition"]) # 註冊新的營養路由器

@app.get("/")
async def root():
    return {"message": "Health Assistant API is running"}

@app.on_event("startup")
async def startup_event():
    """應用程序啟動時的事件"""
    logger.info("Health Assistant API 正在啟動...")
    logger.info("AI 模型將在首次使用時載入，以節省啟動時間")

@app.on_event("shutdown")
async def shutdown_event():
    """應用程序關閉時的事件"""
    logger.info("Health Assistant API 正在關閉...")

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "routers": ["ai_router", "meal_router", "nutrition_router"],
        "endpoints": [
            "/ai/analyze-food-image/",
            "/ai/analyze-food-image-with-weight/",
            "/ai/health",
            "/api/nutrition/lookup",
            "/api/logs"
        ]
    }

@app.get("/api/logs")
async def get_logs():
    """獲取系統日誌"""
    try:
        return {
            "logs": [
                f"系統啟動時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "API 狀態: 正常運行",
                "後端服務: FastAPI",
                "前端服務: React + Vite",
                "AI 模型: 延遲載入模式",
                "資料庫: SQLAlchemy"
            ],
            "total_lines": 6,
            "timestamp": datetime.now().isoformat(),
            "environment": "local-development"
        }
    except Exception as e:
        return {
            "logs": [f"日誌查詢錯誤: {str(e)}"],
            "total_lines": 0,
            "timestamp": datetime.now().isoformat()
        }
