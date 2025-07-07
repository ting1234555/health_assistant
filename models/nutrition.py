# backend/app/models/nutrition.py
from sqlalchemy import Column, Integer, String, Float, JSON
from database import Base

class Nutrition(Base):
    __tablename__ = "nutrition"

    id = Column(Integer, primary_key=True, index=True)
    food_name = Column(String, unique=True, index=True, nullable=False)
    chinese_name = Column(String)
    calories = Column(Float)
    protein = Column(Float)
    fat = Column(Float)
    carbs = Column(Float)
    fiber = Column(Float)
    sugar = Column(Float)
    sodium = Column(Float)
    # For more complex data like vitamins, minerals, etc.
    details = Column(JSON)
    health_score = Column(Integer)
    recommendations = Column(JSON)
    warnings = Column(JSON) 