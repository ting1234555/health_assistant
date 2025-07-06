from .database import Base, engine, SessionLocal
from .models.meal_log import MealLog
from .models.nutrition import Nutrition
import json

def init_db():
    """初始化資料庫並填入初始營養數據"""
    print("Creating database tables...")
    # 根據模型建立所有表格
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

    # 檢查是否已有資料，避免重複新增
    db = SessionLocal()
    if db.query(Nutrition).count() == 0:
        print("Populating nutrition table with initial data...")
        
        # 從 main.py 移植過來的模擬資料
        mock_nutrition_data = [
            {
                "food_name": "hamburger", "chinese_name": "漢堡", "calories": 540, "protein": 25, "fat": 31, "carbs": 40,
                "fiber": 3, "sugar": 6, "sodium": 1040, "health_score": 45,
                "recommendations": ["脂肪和鈉含量過高，建議減少食用頻率。"],
                "warnings": ["高熱量", "高脂肪", "高鈉"]
            },
            {
                "food_name": "pizza", "chinese_name": "披薩", "calories": 266, "protein": 11, "fat": 10, "carbs": 33,
                "fiber": 2, "sugar": 4, "sodium": 598, "health_score": 65,
                "recommendations": ["可搭配沙拉以增加纖維攝取。"],
                "warnings": ["高鈉"]
            },
            {
                "food_name": "sushi", "chinese_name": "壽司", "calories": 200, "protein": 12, "fat": 8, "carbs": 20,
                "fiber": 1, "sugar": 2, "sodium": 380, "health_score": 85,
                "recommendations": ["優質的蛋白質和碳水化合物來源。"],
                "warnings": []
            },
            {
                "food_name": "fried rice", "chinese_name": "炒飯", "calories": 238, "protein": 8, "fat": 12, "carbs": 26,
                "fiber": 2, "sugar": 3, "sodium": 680, "health_score": 60,
                "recommendations": ["注意油脂和鈉含量。"],
                "warnings": ["高鈉"]
            },
            {
                "food_name": "chicken wings", "chinese_name": "雞翅", "calories": 203, "protein": 18, "fat": 14, "carbs": 0,
                "fiber": 0, "sugar": 0, "sodium": 380, "health_score": 70,
                "recommendations": ["蛋白質的良好來源。"],
                "warnings": []
            },
            {
                "food_name": "salad", "chinese_name": "沙拉", "calories": 33, "protein": 3, "fat": 0.2, "carbs": 6,
                "fiber": 3, "sugar": 3, "sodium": 65, "health_score": 95,
                "recommendations": ["低熱量高纖維，是健康的選擇。"],
                "warnings": []
            }
        ]

        for food_data in mock_nutrition_data:
            db_item = Nutrition(**food_data)
            db.add(db_item)
        
        db.commit()
        print(f"{len(mock_nutrition_data)} items populated.")
    else:
        print("Nutrition table already contains data. Skipping population.")
    
    db.close()

if __name__ == "__main__":
    init_db()
