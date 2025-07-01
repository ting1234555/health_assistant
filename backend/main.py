from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import base64
from io import BytesIO
from PIL import Image
import json
import os
from dotenv import load_dotenv

# Database and services
from .app.database import get_db
from sqlalchemy.orm import Session
from .app.models.nutrition import Nutrition
from .app.services import nutrition_api_service

# Routers
from .app.routers import ai_router, meal_router

app = FastAPI(title="Health Assistant API")
app.include_router(ai_router.router)
app.include_router(meal_router.router) 

# Load environment variables
load_dotenv()

# CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FoodRecognitionResponse(BaseModel):
    food_name: str
    chinese_name: str
    confidence: float
    success: bool

class NutritionAnalysisResponse(BaseModel):
    success: bool
    food_name: str
    chinese_name: Optional[str] = None
    nutrition: Dict[str, Any]
    analysis: Dict[str, Any]

class ErrorResponse(BaseModel):
    detail: str

@app.get("/")
async def root():
    return {"message": "Health Assistant API is running"}

@app.get("/api/analyze-nutrition/{food_name}", response_model=NutritionAnalysisResponse, responses={404: {"model": ErrorResponse}})
async def analyze_nutrition(food_name: str, db: Session = Depends(get_db)):
    """
    Analyze nutrition for a recognized food item by querying the database.
    If not found locally, it queries an external API and saves the new data.
    """
    try:
        # Query the database for the food item (case-insensitive search)
        food_item = db.query(Nutrition).filter(Nutrition.food_name.ilike(f"%{food_name.strip()}%")).first()
        
        if not food_item:
            # If not found, query the external API
            print(f"Food '{food_name}' not in local DB. Querying external API...")
            api_data = nutrition_api_service.fetch_nutrition_data(food_name)
            
            if not api_data:
                # If external API also doesn't find it, raise 404
                raise HTTPException(status_code=404, detail=f"Food '{food_name}' not found in local database or external API.")

            # Create a new Nutrition object from the API data
            recommendations = generate_recommendations(api_data)
            warnings = generate_warnings(api_data)
            health_score = calculate_health_score(api_data)
            
            new_food_item = Nutrition(
                food_name=api_data.get('food_name', food_name),
                chinese_name=api_data.get('chinese_name'),
                calories=api_data.get('calories', 0),
                protein=api_data.get('protein', 0),
                fat=api_data.get('fat', 0),
                carbs=api_data.get('carbs', 0),
                fiber=api_data.get('fiber', 0),
                sugar=api_data.get('sugar', 0),
                sodium=api_data.get('sodium', 0),
                health_score=health_score,
                recommendations=recommendations,
                warnings=warnings,
                details={} # API doesn't provide extra details in our format
            )
            
            # Add to DB and commit
            db.add(new_food_item)
            db.commit()
            db.refresh(new_food_item)
            print(f"Saved new food '{new_food_item.food_name}' to the database.")
            food_item = new_food_item # Use the new item for the response
        
        if not food_item:
            raise HTTPException(status_code=404, detail=f"Food '{food_name}' not found in the database.")
        
        # Structure the response
        nutrition_details = {
            "calories": food_item.calories,
            "protein": food_item.protein,
            "fat": food_item.fat,
            "carbs": food_item.carbs,
            "fiber": food_item.fiber,
            "sugar": food_item.sugar,
            "sodium": food_item.sodium,
        }

        # Safely add details if they exist and are a dictionary
        if isinstance(food_item.details, dict):
            nutrition_details.update(food_item.details)
        
        analysis_details = {
            "healthScore": food_item.health_score,
            "recommendations": food_item.recommendations,
            "warnings": food_item.warnings
        }
        
        return {
            "success": True,
            "food_name": food_item.food_name,
            "chinese_name": food_item.chinese_name,
            "nutrition": nutrition_details,
            "analysis": analysis_details
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the error for debugging
        print(f"Error in analyze_nutrition: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error while processing '{food_name}'.")

def calculate_health_score(nutrition: Dict[str, Any]) -> int:
    """Calculate a health score based on nutritional values"""
    score = 100
    
    # 熱量評分
    if nutrition.get("calories", 0) > 400:
        score -= 20
    elif nutrition.get("calories", 0) > 300:
        score -= 10
    
    # 脂肪評分
    if nutrition.get("fat", 0) > 20:
        score -= 15
    elif nutrition.get("fat", 0) > 15:
        score -= 8
    
    # 蛋白質評分
    if nutrition.get("protein", 0) > 15:
        score += 10
    elif nutrition.get("protein", 0) < 5:
        score -= 10
    
    # 鈉含量評分
    if nutrition.get("sodium", 0) > 800:
        score -= 15
    elif nutrition.get("sodium", 0) > 600:
        score -= 8
    
    return max(0, min(100, score))

def generate_recommendations(nutrition: Dict[str, Any]) -> List[str]:
    """Generate dietary recommendations based on nutrition data"""
    recommendations = []
    
    if nutrition.get("protein", 0) < 10:
        recommendations.append("建議增加蛋白質攝取，可搭配雞蛋或豆腐")
    
    if nutrition.get("fat", 0) > 20:
        recommendations.append("脂肪含量較高，建議適量食用")
    
    if nutrition.get("fiber", 0) < 3:
        recommendations.append("纖維含量不足，建議搭配蔬菜沙拉")
    
    if nutrition.get("sodium", 0) > 600:
        recommendations.append("鈉含量偏高，建議多喝水並減少其他鹽分攝取")
    
    return recommendations

def generate_warnings(nutrition: Dict[str, Any]) -> List[str]:
    """Generate dietary warnings based on nutrition data"""
    warnings = []
    
    if nutrition.get("calories", 0) > 500:
        warnings.append("高熱量食物")
    
    if nutrition.get("fat", 0) > 25:
        warnings.append("高脂肪食物")
    
    if nutrition.get("sodium", 0) > 1000:
        warnings.append("高鈉食物")
    
    return warnings

if __name__ == "__main__":
    # It's better to run with `uvicorn backend.main:app --reload` from the project root.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)