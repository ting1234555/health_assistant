from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import ai_router, meal_router
from .database import engine, Base

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
app.include_router(meal_router.router)

@app.get("/")
async def root():
    return {"message": "Health Assistant API is running"}
