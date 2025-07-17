# 檔案路徑: backend/app/routers/ai_router.py

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from ..services.ai_service import classify_food_image  # 直接引入分類函式
from ..services.nutrition_api_service import fetch_nutrition_data  # 匯入營養查詢函式
from ..services.weight_estimation_service import estimate_food_weight  # 新增重量估算服務

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)

# 新增 Pydantic 模型定義
class WeightEstimationResponse(BaseModel):
    food_type: str
    estimated_weight: float
    weight_confidence: float
    weight_error_range: List[float]
    nutrition: Dict[str, Any]
    reference_object: Optional[str] = None
    note: str

class FoodAnalysisResponse(BaseModel):
    food_name: str
    nutrition_info: Dict[str, Any]

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

@router.post("/analyze-food-image-with-weight/", response_model=WeightEstimationResponse)
async def analyze_food_image_with_weight_endpoint(file: UploadFile = File(...)):
    """
    整合食物辨識、重量估算與營養分析的端點。
    包含信心度與誤差範圍，支援參考物偵測。
    """
    # 檢查上傳的檔案是否為圖片格式
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="上傳的檔案不是圖片格式。")

    # 讀取圖片的二進位制內容
    image_bytes = await file.read()
    
    try:
        # 整合分析：食物辨識 + 重量估算 + 營養查詢
        result = await estimate_food_weight(image_bytes)
        
        return WeightEstimationResponse(
            food_type=result["food_type"],
            estimated_weight=result["estimated_weight"],
            weight_confidence=result["weight_confidence"],
            weight_error_range=result["weight_error_range"],
            nutrition=result["nutrition"],
            reference_object=result.get("reference_object"),
            note=result["note"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析過程中發生錯誤: {str(e)}")

@router.get("/health")
async def health_check():
    """
    健康檢查端點，確認 AI 服務是否正常運作
    """
    return {
        "status": "healthy",
        "services": {
            "food_classification": "available",
            "weight_estimation": "available",
            "nutrition_api": "available"
        }
    }