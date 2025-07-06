# This file makes the services directory a Python package
# Import the HybridFoodAnalyzer class to make it available when importing from app.services
from .food_analyzer_service import HybridFoodAnalyzer

__all__ = ['HybridFoodAnalyzer']
