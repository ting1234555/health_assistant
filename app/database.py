from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 確保資料庫目錄存在
DB_DIR = "/tmp/health_assistant_data"
os.makedirs(DB_DIR, exist_ok=True)

# 資料庫 URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'health_assistant.db')}"

# 創建資料庫引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 特定配置
)

# 創建 SessionLocal 類
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 創建 Base 類
Base = declarative_base()

# 獲取資料庫會話的依賴項
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
