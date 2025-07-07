from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import base64
from transformers.pipelines import pipeline  # 修正匯入
import requests
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Health Assistant AI - Food Recognition API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境請設定具體的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化Hugging Face模型
try:
    # 使用nateraw/food專門的食物分類模型
    food_classifier = pipeline(
        "image-classification",
        model="nateraw/food",
        device=-1  # 使用CPU，如果有GPU可以設為0
    )
    print("nateraw/food 食物辨識模型載入成功")
except Exception as e:
    print(f"模型載入失敗: {e}")
    food_classifier = None

# 食物營養資料庫（擴展版，涵蓋nateraw/food模型常見的食物類型）
NUTRITION_DATABASE = {
    # 水果類
    "apple": {"name": "蘋果", "calories_per_100g": 52, "protein": 0.3, "carbs": 14, "fat": 0.2, "fiber": 2.4, "sugar": 10.4, "vitamin_c": 4.6},
    "banana": {"name": "香蕉", "calories_per_100g": 89, "protein": 1.1, "carbs": 23, "fat": 0.3, "fiber": 2.6, "sugar": 12.2, "potassium": 358},
    "orange": {"name": "橘子", "calories_per_100g": 47, "protein": 0.9, "carbs": 12, "fat": 0.1, "fiber": 2.4, "sugar": 9.4, "vitamin_c": 53.2},
    "strawberry": {"name": "草莓", "calories_per_100g": 32, "protein": 0.7, "carbs": 7.7, "fat": 0.3, "fiber": 2, "sugar": 4.9, "vitamin_c": 58.8},
    "grape": {"name": "葡萄", "calories_per_100g": 62, "protein": 0.6, "carbs": 16.8, "fat": 0.2, "fiber": 0.9, "sugar": 16.1},
    
    # 主食類
    "bread": {"name": "麵包", "calories_per_100g": 265, "protein": 9, "carbs": 49, "fat": 3.2, "fiber": 2.7, "sodium": 491},
    "rice": {"name": "米飯", "calories_per_100g": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "fiber": 0.4},
    "pasta": {"name": "義大利麵", "calories_per_100g": 131, "protein": 5, "carbs": 25, "fat": 1.1, "fiber": 1.8},
    "noodles": {"name": "麵條", "calories_per_100g": 138, "protein": 4.5, "carbs": 25, "fat": 2.2, "fiber": 1.2},
    "pizza": {"name": "披薩", "calories_per_100g": 266, "protein": 11, "carbs": 33, "fat": 10, "sodium": 598},
    
    # 肉類
    "chicken": {"name": "雞肉", "calories_per_100g": 165, "protein": 31, "carbs": 0, "fat": 3.6, "iron": 0.9},
    "beef": {"name": "牛肉", "calories_per_100g": 250, "protein": 26, "carbs": 0, "fat": 15, "iron": 2.6, "zinc": 4.8},
    "pork": {"name": "豬肉", "calories_per_100g": 242, "protein": 27, "carbs": 0, "fat": 14, "thiamine": 0.7},
    "fish": {"name": "魚肉", "calories_per_100g": 206, "protein": 22, "carbs": 0, "fat": 12, "omega_3": "豐富"},
    
    # 蔬菜類
    "broccoli": {"name": "花椰菜", "calories_per_100g": 34, "protein": 2.8, "carbs": 7, "fat": 0.4, "fiber": 2.6, "vitamin_c": 89.2},
    "carrot": {"name": "胡蘿蔔", "calories_per_100g": 41, "protein": 0.9, "carbs": 10, "fat": 0.2, "fiber": 2.8, "vitamin_a": 835},
    "tomato": {"name": "番茄", "calories_per_100g": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2, "fiber": 1.2, "vitamin_c": 13.7},
    "lettuce": {"name": "萵苣", "calories_per_100g": 15, "protein": 1.4, "carbs": 2.9, "fat": 0.2, "fiber": 1.3, "folate": 38},
    
    # 飲品類
    "coffee": {"name": "咖啡", "calories_per_100g": 2, "protein": 0.3, "carbs": 0, "fat": 0, "caffeine": 95},
    "tea": {"name": "茶", "calories_per_100g": 1, "protein": 0, "carbs": 0.3, "fat": 0, "antioxidants": "豐富"},
    "milk": {"name": "牛奶", "calories_per_100g": 42, "protein": 3.4, "carbs": 5, "fat": 1, "calcium": 113},
    "juice": {"name": "果汁", "calories_per_100g": 45, "protein": 0.7, "carbs": 11, "fat": 0.2, "vitamin_c": "因果汁種類而異"},
    
    # 甜點類
    "cake": {"name": "蛋糕", "calories_per_100g": 257, "protein": 4, "carbs": 46, "fat": 6, "sugar": 35},
    "cookie": {"name": "餅乾", "calories_per_100g": 502, "protein": 5.9, "carbs": 64, "fat": 25, "sugar": 39},
    "ice_cream": {"name": "冰淇淋", "calories_per_100g": 207, "protein": 3.5, "carbs": 24, "fat": 11, "sugar": 21},
    "chocolate": {"name": "巧克力", "calories_per_100g": 546, "protein": 4.9, "carbs": 61, "fat": 31, "sugar": 48},
    
    # 其他常見食物
    "egg": {"name": "雞蛋", "calories_per_100g": 155, "protein": 13, "carbs": 1.1, "fat": 11, "choline": 294},
    "cheese": {"name": "起司", "calories_per_100g": 113, "protein": 7, "carbs": 1, "fat": 9, "calcium": 200},
    "yogurt": {"name": "優格", "calories_per_100g": 59, "protein": 10, "carbs": 3.6, "fat": 0.4, "probiotics": "豐富"},
    "nuts": {"name": "堅果", "calories_per_100g": 607, "protein": 15, "carbs": 7, "fat": 54, "vitamin_e": 26},
    "salad": {"name": "沙拉", "calories_per_100g": 20, "protein": 1.5, "carbs": 4, "fat": 0.2, "fiber": 2, "vitamins": "多種維生素"}
}

# 回應模型
class FoodAnalysisResponse(BaseModel):
    success: bool
    food_name: str
    confidence: float
    nutrition_info: Dict[str, Any]
    ai_suggestions: list
    message: str

class HealthResponse(BaseModel):
    status: str
    message: str

def get_nutrition_info(food_name: str) -> Dict[str, Any]:
    """根據食物名稱獲取營養資訊"""
    # 將食物名稱轉為小寫並清理
    food_key = food_name.lower().strip()
    
    # 移除常見的修飾詞和格式化字符
    food_key = food_key.replace("_", " ").replace("-", " ")
    
    # 直接匹配
    if food_key in NUTRITION_DATABASE:
        return NUTRITION_DATABASE[food_key]
    
    # 模糊匹配 - 檢查是否包含關鍵字
    for key, value in NUTRITION_DATABASE.items():
        if key in food_key or food_key in key:
            return value
        # 也檢查中文名稱
        if value["name"] in food_name:
            return value
    
    # 更智能的匹配 - 處理複合詞
    food_words = food_key.split()
    for word in food_words:
        for key, value in NUTRITION_DATABASE.items():
            if word == key or word in key:
                return value
    
    # 特殊情況處理
    special_mappings = {
        "french fries": "potato",
        "hamburger": "beef",
        "sandwich": "bread", 
        "soda": "juice",
        "water": {"name": "水", "calories_per_100g": 0, "protein": 0, "carbs": 0, "fat": 0},
        "soup": {"name": "湯", "calories_per_100g": 50, "protein": 2, "carbs": 8, "fat": 1, "sodium": 400}
    }
    
    for special_key, mapping in special_mappings.items():
        if special_key in food_key:
            if isinstance(mapping, str):
                return NUTRITION_DATABASE.get(mapping, {"name": food_name, "message": "營養資料不完整"})
            else:
                return mapping
    
    # 如果沒有找到，返回預設值
    return {
        "name": food_name,
        "calories_per_100g": "未知",
        "protein": "未知",
        "carbs": "未知", 
        "fat": "未知",
        "message": f"抱歉，暫時沒有「{food_name}」的詳細營養資料，建議查詢專業營養資料庫"
    }

def generate_ai_suggestions(food_name: str, nutrition_info: Dict) -> list:
    """根據食物和營養資訊生成AI建議"""
    suggestions = []
    food_name_lower = food_name.lower()
    
    # 檢查是否有完整的營養資訊
    if isinstance(nutrition_info.get("calories_per_100g"), (int, float)):
        calories = nutrition_info["calories_per_100g"]
        
        # 熱量相關建議
        if calories > 400:
            suggestions.append("⚠️ 這是高熱量食物，建議控制份量，搭配運動")
        elif calories > 200:
            suggestions.append("🍽️ 中等熱量食物，適量食用，建議搭配蔬菜")
        elif calories < 50:
            suggestions.append("✅ 低熱量食物，適合減重期間食用")
        
        # 營養素相關建議
        protein = nutrition_info.get("protein", 0)
        if isinstance(protein, (int, float)) and protein > 20:
            suggestions.append("💪 高蛋白食物，有助於肌肉發展和修復")
        
        fiber = nutrition_info.get("fiber", 0)
        if isinstance(fiber, (int, float)) and fiber > 3:
            suggestions.append("🌿 富含纖維，有助於消化健康和增加飽足感")
        
        sugar = nutrition_info.get("sugar", 0)
        if isinstance(sugar, (int, float)) and sugar > 20:
            suggestions.append("🍯 含糖量較高，建議適量食用，避免血糖快速上升")
        
        # 特殊營養素
        if nutrition_info.get("vitamin_c", 0) > 30:
            suggestions.append("🍊 富含維生素C，有助於增強免疫力和抗氧化")
        
        if nutrition_info.get("calcium", 0) > 100:
            suggestions.append("🦴 富含鈣質，有助於骨骼和牙齒健康")
        
        if nutrition_info.get("omega_3"):
            suggestions.append("🐟 含有Omega-3脂肪酸，對心血管健康有益")
    
    # 根據食物類型給出特定建議
    if any(fruit in food_name_lower for fruit in ["apple", "banana", "orange", "strawberry", "grape"]):
        suggestions.append("🍎 建議在餐前或運動前食用，提供天然糖分和維生素")
    
    elif any(meat in food_name_lower for meat in ["chicken", "beef", "pork", "fish"]):
        suggestions.append("🥩 建議搭配蔬菜食用，選擇健康的烹調方式（烤、蒸、煮）")
    
    elif any(sweet in food_name_lower for sweet in ["cake", "cookie", "ice_cream", "chocolate"]):
        suggestions.append("🍰 甜點建議偶爾享用，可在運動後適量食用")
        suggestions.append("💡 可以考慮與朋友分享，減少單次攝取量")
    
    elif any(drink in food_name_lower for drink in ["coffee", "tea"]):
        suggestions.append("☕ 建議控制咖啡因攝取量，避免影響睡眠")
    
    elif "salad" in food_name_lower:
        suggestions.append("🥗 很棒的選擇！可以添加堅果或橄欖油增加健康脂肪")
    
    # 通用健康建議
    if not suggestions:
        suggestions.extend([
            "🍽️ 建議均衡飲食，搭配多樣化的食物",
            "💧 記得多喝水，保持身體水分充足",
            "🏃‍♂️ 搭配適量運動，維持健康生活型態"
        ])
    else:
        # 添加一些通用的健康提醒
        suggestions.append("💧 記得多喝水，幫助營養吸收")
        if len(suggestions) < 4:
            suggestions.append("⚖️ 注意食物份量，適量攝取是健康飲食的關鍵")
    
    return suggestions[:5]  # 限制建議數量，避免過多

@app.get("/", response_model=HealthResponse)
async def root():
    """API根路径"""
    return HealthResponse(
        status="success",
        message="Health Assistant AI - Food Recognition API is running!"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康檢查端點"""
    model_status = "正常" if food_classifier else "模型載入失敗"
    return HealthResponse(
        status="success",
        message=f"API運行正常，模型狀態: {model_status}"
    )

@app.post("/analyze-food", response_model=FoodAnalysisResponse)
async def analyze_food(file: UploadFile = File(...)):
    """分析上傳的食物圖片"""
    try:
        # 檢查模型是否載入成功
        if not food_classifier:
            raise HTTPException(status_code=500, detail="AI模型尚未載入，請稍後再試")
        # 檢查文件類型
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="請上傳圖片文件")
        # 讀取圖片
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        # 確保圖片是RGB格式
        if image.mode != "RGB":
            image = image.convert("RGB")
        # 使用AI模型進行食物辨識
        results = food_classifier(image)
        if not isinstance(results, list) or not results:
            raise HTTPException(status_code=500, detail="AI模型辨識失敗")
        top_result = results[0]
        food_name = str(top_result.get("label", "Unknown"))
        confidence = float(top_result.get("score", 0.0))
        # 獲取營養資訊
        nutrition_info = get_nutrition_info(food_name)
        # 生成AI建議
        ai_suggestions = generate_ai_suggestions(food_name, nutrition_info)
        return FoodAnalysisResponse(
            success=True,
            food_name=food_name,
            confidence=round(confidence * 100, 2),
            nutrition_info=nutrition_info,
            ai_suggestions=ai_suggestions,
            message="食物分析完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失敗: {str(e)}")

@app.post("/analyze-food-base64", response_model=FoodAnalysisResponse)
async def analyze_food_base64(image_data: dict):
    """分析base64編碼的食物圖片"""
    try:
        # 檢查模型是否載入成功
        if not food_classifier:
            raise HTTPException(status_code=500, detail="AI模型尚未載入，請稍後再試")
        # 解碼base64圖片
        base64_string = image_data.get("image", "")
        if not base64_string:
            raise HTTPException(status_code=400, detail="缺少圖片資料")
        # 移除base64前綴（如果有的話）
        if "," in base64_string:
            base64_string = base64_string.split(",", 1)[1]
        # 解碼圖片
        image_bytes = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_bytes))
        # 確保圖片是RGB格式
        if image.mode != "RGB":
            image = image.convert("RGB")
        # 使用AI模型進行食物辨識
        results = food_classifier(image)
        if not isinstance(results, list) or not results:
            raise HTTPException(status_code=500, detail="AI模型辨識失敗")
        top_result = results[0]
        food_name = str(top_result.get("label", "Unknown"))
        confidence = float(top_result.get("score", 0.0))
        # 獲取營養資訊
        nutrition_info = get_nutrition_info(food_name)
        # 生成AI建議
        ai_suggestions = generate_ai_suggestions(food_name, nutrition_info)
        return FoodAnalysisResponse(
            success=True,
            food_name=food_name,
            confidence=round(confidence * 100, 2),
            nutrition_info=nutrition_info,
            ai_suggestions=ai_suggestions,
            message="食物分析完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失敗: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
