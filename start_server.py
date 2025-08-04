#!/usr/bin/env python3
"""
簡化的健康助手啟動腳本
避免重複載入 AI 模型的問題
"""

import uvicorn
import logging
import os
import sys

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函數"""
    try:
        logger.info("正在啟動 Health Assistant API...")
        logger.info("使用簡化模式，AI 模型將在首次使用時載入")
        
        # 啟動 FastAPI 服務器
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("收到中斷信號，正在關閉服務器...")
    except Exception as e:
        logger.error(f"啟動失敗: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 