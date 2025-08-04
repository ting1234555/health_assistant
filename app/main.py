from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ai_router, meal_router
# from app.routers import ai_router_v2  # 暫時註釋掉有問題的路由器
from app.database import engine, Base
from app.routers import nutrition_router  # 引入新的營養路由器
import logging

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
