# 檔案路徑: backend/app/routers/ai_router.py

from fastapi import APIRouter, File, UploadFile, HTTPException
from ..services.ai_service import classify_food_image  # 直接引入分類函式
from ..services.nutrition_api_service import fetch_nutrition_data  # 匯入營養查詢函式
from app.services.weight_estimation_service import estimate_food_weight

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
    food_name = classify_food_image(image_bytes)

    # 查詢營養資訊
    nutrition_info = fetch_nutrition_data(food_name)
    if nutrition_info is None:
        raise HTTPException(status_code=404, detail=f"找不到 {food_name} 的營養資訊。")

    # TODO: 在下一階段，我們會在這裡加入從資料庫查詢營養資訊的邏輯
    # 目前，我們先直接回傳辨識出的食物名稱
    
    return {"food_name": food_name, "nutrition_info": nutrition_info}

@router.post("/analyze-food-image-with-weight/")
async def analyze_food_image_with_weight_endpoint(file: UploadFile = File(...)):
    """
    這個端點接收使用者上傳的食物圖片，進行食物辨識、重量估算與營養分析。
    回傳食物名稱、估算重量、信心度、誤差範圍、調整後營養素等。
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="上傳的檔案不是圖片格式。")
    image_bytes = await file.read()
    result = await estimate_food_weight(image_bytes)
    return result