from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.meal_log import MealLog

class MealService:
    def __init__(self, db: Session):
        self.db = db

    def create_meal_log(
        self,
        food_name: str,
        meal_type: str,
        portion_size: str,
        nutrition: Dict[str, float],
        meal_date: datetime,
        image_url: Optional[str] = None,
        ai_analysis: Optional[Dict[str, Any]] = None
    ) -> MealLog:
        """創建新的用餐記錄"""
        meal_log = MealLog(
            food_name=food_name,
            meal_type=meal_type,
            portion_size=portion_size,
            calories=float(nutrition.get('calories', 0)),
            protein=float(nutrition.get('protein', 0)),
            carbs=float(nutrition.get('carbs', 0)),
            fat=float(nutrition.get('fat', 0)),
            fiber=float(nutrition.get('fiber', 0)),
            meal_date=meal_date,
            image_url=image_url,
            ai_analysis=ai_analysis,
            created_at=datetime.utcnow()
        )
        self.db.add(meal_log)
        self.db.commit()
        self.db.refresh(meal_log)
        return meal_log

    def get_meal_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        meal_type: Optional[str] = None
    ) -> List[MealLog]:
        """獲取用餐記錄"""
        query = self.db.query(MealLog)
        if start_date:
            query = query.filter(MealLog.meal_date >= start_date)
        if end_date:
            query = query.filter(MealLog.meal_date <= end_date)
        if meal_type:
            query = query.filter(MealLog.meal_type == meal_type)
        return query.order_by(MealLog.meal_date.desc()).all()

    def get_nutrition_summary(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """獲取指定時間範圍內的營養攝入總結"""
        meals = self.get_meal_logs(start_date, end_date)
        summary: Dict[str, float] = {
            'total_calories': 0.0,
            'total_protein': 0.0,
            'total_carbs': 0.0,
            'total_fat': 0.0,
            'total_fiber': 0.0
        }
        for meal in meals:
            portion_size = getattr(meal, 'portion_size', 'medium')
            calories = getattr(meal, 'calories', 0.0)
            protein = getattr(meal, 'protein', 0.0)
            carbs = getattr(meal, 'carbs', 0.0)
            fat = getattr(meal, 'fat', 0.0)
            fiber = getattr(meal, 'fiber', 0.0)
            multiplier = {
                'small': 0.7,
                'medium': 1.0,
                'large': 1.3
            }.get(portion_size, 1.0)
            summary['total_calories'] += float(calories) * multiplier
            summary['total_protein'] += float(protein) * multiplier
            summary['total_carbs'] += float(carbs) * multiplier
            summary['total_fat'] += float(fat) * multiplier
            summary['total_fiber'] += float(fiber) * multiplier
        return summary
