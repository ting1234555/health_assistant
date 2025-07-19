from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

app = FastAPI(title="Health Assistant API - Test Version")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 直接在這個檔案中定義 router 和端點
class WeightEstimationResponse(BaseModel):
    food_type: str
    estimated_weight: float
    weight_confidence: float
    weight_error_range: List[float]
    nutrition: Dict[str, Any]
    reference_object: Optional[str] = None
    note: str

@app.get("/")
async def root():
    return {"message": "Health Assistant API - Test Version is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "test",
        "endpoints": [
            "/ai/analyze-food-image/",
            "/ai/analyze-food-image-with-weight/",
            "/ai/health"
        ]
    }

@app.post("/ai/analyze-food-image/")
async def analyze_food_image_endpoint(file: UploadFile = File(...)):
    """測試食物圖片分析端點"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="上傳的檔案不是圖片格式。")
    
    return {"food_name": "測試食物", "nutrition_info": {"calories": 100}}

@app.post("/ai/analyze-food-image-with-weight/", response_model=WeightEstimationResponse)
async def analyze_food_image_with_weight_endpoint(file: UploadFile = File(...)):
    """測試重量估算端點"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="上傳的檔案不是圖片格式。")
    
    return WeightEstimationResponse(
        food_type="測試食物",
        estimated_weight=150.0,
        weight_confidence=0.85,
        weight_error_range=[130.0, 170.0],
        nutrition={"calories": 100, "protein": 5, "fat": 2, "carbs": 15},
        reference_object="硬幣",
        note="測試重量估算結果"
    )

@app.get("/ai/health")
async def ai_health_check():
    """AI 服務健康檢查"""
    return {
        "status": "healthy",
        "services": {
            "food_classification": "available",
            "weight_estimation": "available"
        }
    } 