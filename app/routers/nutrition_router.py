import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any

from app.services.nutrition_api_service import fetch_nutrition_data

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/lookup", response_model=Dict[str, Any])
async def lookup_nutrition(food_name: str = Query(..., min_length=1, description="要查詢的食物名稱")):
    """
    根據食物名稱查詢其每 100g 的營養資訊。
    """
    logger.info(f"收到手動營養查詢請求：{food_name}")
    nutrition_info = fetch_nutrition_data(food_name)
    
    if nutrition_info is None:
        raise HTTPException(
            status_code=404, 
            detail=f"在營養資料庫中找不到關於 '{food_name}' 的資訊。請嘗試不同的關鍵字。"
        )
        
    if 'error' in nutrition_info and nutrition_info.get('calories', -1) == 0:
         raise HTTPException(
            status_code=503,
            detail=f"查詢 '{food_name}' 營養資訊時發生問題。可能是暫時的網路錯誤或 API 請求次數達到上限。"
        )

    return nutrition_info 