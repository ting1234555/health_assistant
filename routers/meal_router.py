from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from services.meal_service import MealService
from database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/api/meals", tags=["Meals"])

class MealCreate(BaseModel):
    food_name: str
    meal_type: str
    portion_size: str
    meal_date: datetime
    nutrition: Dict[str, float]
    image_url: Optional[str] = None
    ai_analysis: Optional[Dict[str, Any]] = None

class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime
    meal_type: Optional[str] = None

@router.post("/log")
async def create_meal_log(
    meal: MealCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """創建新的用餐記錄"""
    meal_service = MealService(db)
    try:
        meal_log = meal_service.create_meal_log(
            food_name=meal.food_name,
            meal_type=meal.meal_type,
            portion_size=meal.portion_size,
            nutrition=meal.nutrition,
            meal_date=meal.meal_date,
            image_url=meal.image_url,
            ai_analysis=meal.ai_analysis
        )
        return {
            "success": True,
            "message": "用餐記錄已創建",
            "data": {
                "id": meal_log.id,
                "food_name": meal_log.food_name,
                "meal_type": meal_log.meal_type,
                "meal_date": meal_log.meal_date
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list")
async def get_meal_logs(
    date_range: DateRange,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """獲取用餐記錄列表"""
    meal_service = MealService(db)
    try:
        logs = meal_service.get_meal_logs(
            start_date=date_range.start_date,
            end_date=date_range.end_date,
            meal_type=date_range.meal_type
        )
        return {
            "success": True,
            "data": [{
                "id": log.id,
                "food_name": log.food_name,
                "meal_type": log.meal_type,
                "portion_size": log.portion_size,
                "calories": log.calories,
                "protein": log.protein,
                "carbs": log.carbs,
                "fat": log.fat,
                "meal_date": log.meal_date,
                "image_url": log.image_url
            } for log in logs]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nutrition-summary")
async def get_nutrition_summary(
    date_range: DateRange,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """獲取營養攝入總結"""
    meal_service = MealService(db)
    try:
        summary = meal_service.get_nutrition_summary(
            start_date=date_range.start_date,
            end_date=date_range.end_date
        )
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
