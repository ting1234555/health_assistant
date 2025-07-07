from database import engine, Base
from models.nutrition import Nutrition
from models.meal_log import MealLog

def init_database():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
