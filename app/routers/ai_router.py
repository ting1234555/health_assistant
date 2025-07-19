# 檔案路徑: app/routers/ai_router.py

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

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

    # 暫時返回測試回應
    return {"food_name": "測試食物", "nutrition_info": {"calories": 100}}

@router.post("/analyze-food-image-with-weight/", response_model=WeightEstimationResponse)
async def analyze_food_image_with_weight_endpoint(file: UploadFile = File(...)):
    """
    整合食物辨識、重量估算與營養分析的端點。
    包含信心度與誤差範圍，支援參考物偵測。
    """
    # 檢查上傳的檔案是否為圖片格式
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="上傳的檔案不是圖片格式。")

    # 暫時返回測試回應
    return WeightEstimationResponse(
        food_type="測試食物",
        estimated_weight=150.0,
        weight_confidence=0.85,
        weight_error_range=[130.0, 170.0],
        nutrition={"calories": 100, "protein": 5, "fat": 2, "carbs": 15},
        reference_object="硬幣",
        note="測試重量估算結果"
    )

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