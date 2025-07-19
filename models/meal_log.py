from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from database import Base

class MealLog(Base):
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, index=True)
    food_name = Column(String, index=True)
    meal_type = Column(String)  # breakfast, lunch, dinner, snack
    portion_size = Column(String)  # small, medium, large
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    fiber = Column(Float)
    meal_date = Column(DateTime, index=True)
    image_url = Column(String)
    ai_analysis = Column(JSON)  # 儲存完整的 AI 分析結果
    created_at = Column(DateTime)
