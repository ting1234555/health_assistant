# 檔案路徑: backend/app/routers/ai_router.py

from fastapi import APIRouter, File, UploadFile, HTTPException
from ..services import ai_service  # 引入我們的 AI 服務

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)

@router.post("/analyze-food-image/")
async def analyze_food_image_endpoint(file: UploadFile = File(...)):
    """
    這個端點接收使用者上傳的食物圖片，使用 AI 模型進行辨識，
    並返回辨識出的食物名稱。
    """
    # 檢查上傳的檔案是否為圖片格式
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="上傳的檔案不是圖片格式。")

    # 讀取圖片的二進位制內容
    image_bytes = await file.read()
    
    # 呼叫 AI 服務中的分類函式
    food_name = ai_service.classify_food_image(image_bytes)

    # 處理辨識失敗或錯誤的情況
    if "Error" in food_name or food_name == "Unknown":
        raise HTTPException(status_code=500, detail=f"無法辨識圖片中的食物。模型回傳: {food_name}")

    # TODO: 在下一階段，我們會在這裡加入從資料庫查詢營養資訊的邏輯
    # 目前，我們先直接回傳辨識出的食物名稱
    
    return {"food_name": food_name}