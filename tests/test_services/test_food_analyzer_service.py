import pytest
from unittest.mock import patch, MagicMock, ANY
from PIL import Image
from io import BytesIO
import json
import sys
import os
import torch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app.services.food_analyzer_service import HybridFoodAnalyzer

# Test data
SAMPLE_NUTRITION_DATA = {
    "calories": 95,
    "protein": 0.5,
    "fat": 0.3,
    "carbohydrates": 25.0,
    "fiber": 4.4,
    "sugar": 19.0,
    "sodium": 2,
    "cholesterol": 0,
    "saturated_fat": 0.1,
    "calcium": 1,
    "iron": 1,
    "potassium": 195,
    "vitamin_a": 2,
    "vitamin_c": 14,
    "vitamin_d": 0
}

SAMPLE_IMAGE = None

def create_test_image():
    """Helper function to create a test image"""
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

@pytest.fixture
def mock_analyzer():
    with patch('transformers.AutoImageProcessor.from_pretrained') as mock_processor, \
         patch('transformers.AutoModelForImageClassification.from_pretrained') as mock_model, \
         patch('anthropic.Anthropic') as mock_anthropic:
        
        # Setup mock processor
        mock_processor.return_value = MagicMock()
        
        # Setup mock model
        mock_model.return_value = MagicMock()
        mock_model.return_value.config.id2label = {0: "apple"}
        mock_model.return_value.return_value = MagicMock(logits=torch.tensor([[0.9, 0.1]]))
        
        # Setup mock anthropic
        mock_anthropic.return_value = MagicMock()
        mock_anthropic.return_value.messages.create.return_value.content = [
            MagicMock(text=json.dumps(SAMPLE_NUTRITION_DATA))
        ]
        
        analyzer = HybridFoodAnalyzer("test_api_key")
        analyzer.processor = mock_processor.return_value
        analyzer.model = mock_model.return_value
        analyzer.claude_client = mock_anthropic.return_value
        
        yield analyzer

def test_hybrid_food_analyzer_init(mock_analyzer):
    """Test initialization of HybridFoodAnalyzer"""
    assert mock_analyzer is not None
    assert hasattr(mock_analyzer, 'processor')
    assert hasattr(mock_analyzer, 'model')
    assert hasattr(mock_analyzer, 'claude_client')

def test_recognize_food_success(mock_analyzer):
    """Test successful food recognition"""
    # Create test image
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    
    # Call method
    result = mock_analyzer.recognize_food(img_byte_arr.getvalue())
    
    # Assertions
    assert result["success"] is True
    assert "food_name" in result
    assert "chinese_name" in result
    assert "confidence" in result
    assert result["food_name"] == "apple"
    assert result["chinese_name"] == "蘋果"

def test_recognize_food_error(mock_analyzer):
    """Test error handling in food recognition"""
    # Setup mock to raise exception
    mock_analyzer.model.side_effect = Exception("Test error")
    
    # Call method with invalid image
    result = mock_analyzer.recognize_food(b"invalid_image")
    
    # Assertions
    assert result["success"] is False
    assert "error" in result

def test_analyze_nutrition_success(mock_analyzer):
    """Test successful nutrition analysis"""
    # Call method
    result = mock_analyzer.analyze_nutrition("apple")
    
    # Assertions
    assert result["success"] is True
    assert "nutrition" in result
    assert result["nutrition"] == SAMPLE_NUTRITION_DATA
    mock_analyzer.claude_client.messages.create.assert_called_once()

def test_analyze_nutrition_error(mock_analyzer):
    """Test error handling in nutrition analysis"""
    # Setup mock to raise exception
    mock_analyzer.claude_client.messages.create.side_effect = Exception("API error")
    
    # Call method
    result = mock_analyzer.analyze_nutrition("invalid_food")
    
    # Assertions
    assert result["success"] is False
    assert "error" in result

def test_process_image_success(mock_analyzer):
    """Test successful image processing"""
    # Setup
    test_image = create_test_image()
    
    # Call method
    result = mock_analyzer.process_image(test_image)
    
    # Assertions
    assert result["success"] is True
    assert "food_name" in result
    assert "nutrition" in result
    assert "analysis" in result
    assert "healthScore" in result["analysis"]
    assert "recommendations" in result["analysis"]
    assert "warnings" in result["analysis"]

def test_calculate_health_score(mock_analyzer):
    """Test health score calculation"""
    # Test with sample nutrition data
    score = mock_analyzer.calculate_health_score(SAMPLE_NUTRITION_DATA)
    
    # Assert score is within expected range
    assert isinstance(score, (int, float))
    assert 0 <= score <= 100

def test_generate_recommendations(mock_analyzer):
    """Test generation of dietary recommendations"""
    # Call method
    recommendations = mock_analyzer.generate_recommendations(SAMPLE_NUTRITION_DATA)
    
    # Assertions
    assert isinstance(recommendations, list)
    assert all(isinstance(rec, str) for rec in recommendations)

def test_generate_warnings(mock_analyzer):
    """Test generation of dietary warnings"""
    # Call method
    warnings = mock_analyzer.generate_warnings(SAMPLE_NUTRITION_DATA)
    
    # Assertions
    assert isinstance(warnings, list)
    assert all(isinstance(warning, str) for warning in warnings)

def test_calculate_health_score_incomplete_data(mock_analyzer):
    """Test health score calculation with incomplete nutrition data"""
    # Test with incomplete nutrition data
    incomplete_nutrition = {"calories": 100}
    health_score = mock_analyzer.calculate_health_score(incomplete_nutrition)
    assert 0 <= health_score <= 100
