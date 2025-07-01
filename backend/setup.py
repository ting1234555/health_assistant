import os
import sys
from pathlib import Path

def setup_project():
    """設置專案目錄結構和必要檔案"""
    # 獲取專案根目錄
    project_root = Path(__file__).parent
    
    # 創建必要的目錄
    directories = [
        'data',  # 資料庫目錄
        'logs',  # 日誌目錄
        'uploads'  # 上傳檔案目錄
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # 創建 .env 檔案（如果不存在）
    env_file = project_root / '.env'
    if not env_file.exists():
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("""# 資料庫設定
DATABASE_URL=sqlite:///./data/health_assistant.db

# Redis 設定
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API 設定
API_HOST=localhost
API_PORT=8000
""")
        print(f"Created .env file: {env_file}")
    
    print("\nProject setup completed successfully!")
    print("\nNext steps:")
    print("1. Install required packages: pip install -r requirements.txt")
    print("2. Start the Redis server")
    print("3. Run the application: uvicorn app.main:app --reload")

if __name__ == "__main__":
    setup_project()
