from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.meal_log import MealLog

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
            calories=nutrition.get('calories', 0),
            protein=nutrition.get('protein', 0),
            carbs=nutrition.get('carbs', 0),
            fat=nutrition.get('fat', 0),
            fiber=nutrition.get('fiber', 0),
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
        
        summary = {
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fat': 0,
            'total_fiber': 0
        }
        
        for meal in meals:
            # 根據份量大小調整營養值
            multiplier = {
                'small': 0.7,
                'medium': 1.0,
                'large': 1.3
            }.get(meal.portion_size, 1.0)
            
            summary['total_calories'] += meal.calories * multiplier
            summary['total_protein'] += meal.protein * multiplier
            summary['total_carbs'] += meal.carbs * multiplier
            summary['total_fat'] += meal.fat * multiplier
            summary['total_fiber'] += meal.fiber * multiplier
            
        return summary
