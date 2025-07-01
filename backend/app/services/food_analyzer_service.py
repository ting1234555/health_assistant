import torch
import json
from typing import Dict, Any
from PIL import Image
from io import BytesIO
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HybridFoodAnalyzer:
    def __init__(self, claude_api_key: str = None):
        """
        Initialize the HybridFoodAnalyzer with HuggingFace model and Claude API.
        
        Args:
            claude_api_key: Optional API key for Claude. If not provided, will try to get from environment variable CLAUDE_API_KEY.
        """
        # Initialize HuggingFace model
        from transformers import AutoImageProcessor, AutoModelForImageClassification
        
        print("Loading HuggingFace food recognition model...")
        self.processor = AutoImageProcessor.from_pretrained("nateraw/food")
        self.model = AutoModelForImageClassification.from_pretrained("nateraw/food")
        self.model.eval()  # Set model to evaluation mode
        
        # Initialize Claude API
        print("Initializing Claude API...")
        import anthropic
        self.claude_api_key = claude_api_key or os.getenv('CLAUDE_API_KEY')
        if not self.claude_api_key:
            raise ValueError("Claude API key is required. Please set CLAUDE_API_KEY environment variable or pass it as an argument.")
            
        self.claude_client = anthropic.Anthropic(api_key=self.claude_api_key)
    
    def recognize_food(self, image: Image.Image) -> Dict[str, Any]:
        """
        Recognize food from an image using HuggingFace model.
        
        Args:
            image: PIL Image object containing the food image
            
        Returns:
            Dictionary containing food name and confidence score
        """
        try:
            print("Processing image for food recognition...")
            inputs = self.processor(images=image, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            predicted_class_id = predictions.argmax().item()
            confidence = predictions[0][predicted_class_id].item()
            food_name = self.model.config.id2label[predicted_class_id]
            
            # Map common food names to Chinese
            food_name_mapping = {
                "hamburger": "漢堡",
                "pizza": "披薩",
                "sushi": "壽司",
                "fried rice": "炒飯",
                "chicken wings": "雞翅",
                "salad": "沙拉",
                "apple": "蘋果",
                "banana": "香蕉",
                "orange": "橙子",
                "noodles": "麵條"
            }
            
            chinese_name = food_name_mapping.get(food_name.lower(), food_name)
            
            return {
                "food_name": food_name,
                "chinese_name": chinese_name,
                "confidence": confidence,
                "success": True
            }
            
        except Exception as e:
            print(f"Error in food recognition: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_nutrition(self, food_name: str) -> Dict[str, Any]:
        """
        Analyze nutrition information for a given food using Claude API.
        
        Args:
            food_name: Name of the food to analyze
            
        Returns:
            Dictionary containing nutrition information
        """
        try:
            print(f"Analyzing nutrition for {food_name}...")
            prompt = f"""
            請分析 {food_name} 的營養成分（每100g），並以JSON格式回覆：
            {{
                "calories": 數值,
                "protein": 數值,
                "fat": 數值,
                "carbs": 數值,
                "fiber": 數值,
                "sugar": 數值,
                "sodium": 數值
            }}
            """
            
            message = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract and parse the JSON response
            response_text = message.content[0].text
            try:
                nutrition_data = json.loads(response_text.strip())
                return {
                    "success": True,
                    "nutrition": nutrition_data
                }
            except json.JSONDecodeError as e:
                print(f"Error parsing Claude response: {e}")
                return {
                    "success": False,
                    "error": f"Failed to parse nutrition data: {e}",
                    "raw_response": response_text
                }
                
        except Exception as e:
            print(f"Error in nutrition analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Process an image to recognize food and analyze its nutrition.
        
        Args:
            image_data: Binary image data
            
        Returns:
            Dictionary containing recognition and analysis results
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(BytesIO(image_data))
            
            # Step 1: Recognize food
            recognition_result = self.recognize_food(image)
            if not recognition_result.get("success"):
                return recognition_result
            
            # Step 2: Analyze nutrition
            nutrition_result = self.analyze_nutrition(recognition_result["food_name"])
            if not nutrition_result.get("success"):
                return nutrition_result
            
            # Calculate health score
            nutrition = nutrition_result["nutrition"]
            health_score = self.calculate_health_score(nutrition)
            
            # Generate recommendations and warnings
            recommendations = self.generate_recommendations(nutrition)
            warnings = self.generate_warnings(nutrition)
            
            return {
                "success": True,
                "food_name": recognition_result["food_name"],
                "chinese_name": recognition_result["chinese_name"],
                "confidence": recognition_result["confidence"],
                "nutrition": nutrition,
                "analysis": {
                    "healthScore": health_score,
                    "recommendations": recommendations,
                    "warnings": warnings
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process image: {str(e)}"
            }
    
    def calculate_health_score(self, nutrition: Dict[str, float]) -> int:
        """Calculate a health score based on nutritional values"""
        score = 100
        
        # 熱量評分
        if nutrition["calories"] > 400:
            score -= 20
        elif nutrition["calories"] > 300:
            score -= 10
        
        # 脂肪評分
        if nutrition["fat"] > 20:
            score -= 15
        elif nutrition["fat"] > 15:
            score -= 8
        
        # 蛋白質評分
        if nutrition["protein"] > 15:
            score += 10
        elif nutrition["protein"] < 5:
            score -= 10
        
        # 鈉含量評分
        if "sodium" in nutrition and nutrition["sodium"] > 800:
            score -= 15
        elif "sodium" in nutrition and nutrition["sodium"] > 600:
            score -= 8
        
        return max(0, min(100, score))
    
    def generate_recommendations(self, nutrition: Dict[str, float]) -> list:
        """Generate dietary recommendations based on nutrition data"""
        recommendations = []
        
        if nutrition["protein"] < 10:
            recommendations.append("建議增加蛋白質攝取，可搭配雞蛋或豆腐")
        
        if nutrition["fat"] > 20:
            recommendations.append("脂肪含量較高，建議適量食用")
        
        if "fiber" in nutrition and nutrition["fiber"] < 3:
            recommendations.append("纖維含量不足，建議搭配蔬菜沙拉")
        
        if "sodium" in nutrition and nutrition["sodium"] > 600:
            recommendations.append("鈉含量偏高，建議多喝水並減少其他鹽分攝取")
        
        return recommendations
    
    def generate_warnings(self, nutrition: Dict[str, float]) -> list:
        """Generate dietary warnings based on nutrition data"""
        warnings = []
        
        if nutrition["calories"] > 500:
            warnings.append("高熱量食物")
        
        if nutrition["fat"] > 25:
            warnings.append("高脂肪食物")
        
        if "sodium" in nutrition and nutrition["sodium"] > 1000:
            warnings.append("高鈉食物")
        
        return warnings
