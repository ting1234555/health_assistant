import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from unittest.mock import patch, MagicMock

@pytest.fixture
def test_app():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def sample_image():
    """Create a sample in-memory image for testing"""
    from PIL import Image
    from io import BytesIO
    
    # Create a simple red image
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    # Return the image data as bytes
    return img_byte_arr.getvalue()

@pytest.fixture
def mock_analyzer():
    with patch('transformers.AutoImageProcessor') as mock_processor, \
         patch('transformers.AutoModelForImageClassification') as mock_model, \
         patch('anthropic.Anthropic') as mock_anthropic:
        
        # Setup mock processor
        mock_processor.from_pretrained.return_value = MagicMock()
        
        # Setup mock model
        mock_model.from_pretrained.return_value = MagicMock()
        
        # Setup mock anthropic
        mock_anthropic.return_value = MagicMock()
        
        yield (
            mock_processor.from_pretrained.return_value,
            mock_model.from_pretrained.return_value,
            mock_anthropic.return_value
        )
