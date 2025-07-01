import pytest
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

# Test the root endpoint
def test_read_root(test_app):
    response = test_app.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Health Assistant API is running"}

# Test food recognition endpoint
@patch('backend.app.services.food_analyzer_service.HybridFoodAnalyzer.analyze_food')
def test_recognize_food(mock_analyze_food, test_app, sample_image):
    # Mock the response from the analyzer
    mock_analyze_food.return_value = {
        "food_name": "apple",
        "chinese_name": "蘋果",
        "confidence": 0.95,
        "success": True
    }
    
    # Create a test file
    files = {"file": ("test_image.jpg", sample_image, "image/jpeg")}
    
    # Make the request
    response = test_app.post("/recognize-food", files=files)
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "food_name" in data
    assert "chinese_name" in data
    assert "confidence" in data

# Test nutrition analysis endpoint
@patch('app.services.food_analyzer_service.HybridFoodAnalyzer.analyze_nutrition')
def test_analyze_nutrition(mock_analyze_nutrition, test_app):
    # Mock the response from the analyzer
    mock_analyze_nutrition.return_value = {
        "nutrition": {
            "calories": 95,
            "protein": 0.5,
            "fat": 0.3,
            "carbohydrates": 25.0
        },
        "success": True
    }
    
    # Test data
    test_data = {"food_name": "apple"}
    
    # Make the request
    response = test_app.post("/analyze-nutrition", json=test_data)
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "nutrition" in data
    assert "analysis" in data

# Test error handling for invalid image
def test_recognize_food_invalid_file(test_app):
    # Create an invalid file
    files = {"file": ("test.txt", b"not an image", "text/plain")}
    
    # Make the request
    response = test_app.post("/recognize-food", files=files)
    
    # Check the response
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid image file"

# Test error handling for missing food name
@patch('app.services.food_analyzer_service.HybridFoodAnalyzer.analyze_nutrition')
def test_analyze_nutrition_missing_food(mock_analyze_nutrition, test_app):
    # Configure the mock to raise an exception
    mock_analyze_nutrition.side_effect = ValueError("Food name is required")
    
    # Test data with missing food name
    test_data = {}
    
    # Make the request
    response = test_app.post("/analyze-nutrition", json=test_data)
    
    # Check the response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
