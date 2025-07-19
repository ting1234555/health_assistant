# backend/app/services/nutrition_api_service.py
import os
import requests
from dotenv import load_dotenv
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

# 從環境變數中獲取 API 金鑰
USDA_API_KEY = os.getenv("USDA_API_KEY")
USDA_API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# 我們關心的主要營養素及其在 USDA API 中的名稱或編號
# 我們可以透過 nutrient.nutrientNumber 或 nutrient.name 來匹配
NUTRIENT_MAP = {
    'calories': 'Energy',
    'protein': 'Protein',
    'fat': 'Total lipid (fat)',
    'carbs': 'Carbohydrate, by difference',
    'fiber': 'Fiber, total dietary',
    'sugar': 'Total sugars',
    'sodium': 'Sodium, Na'
}

def fetch_nutrition_data(food_name: str):
    """
    從 USDA FoodData Central API 獲取食物的營養資訊。

    :param food_name: 要查詢的食物名稱 (例如 "Donuts")。
    :return: 包含營養資訊的字典，如果找不到則返回 None。
    """
    if not USDA_API_KEY:
        logger.error("USDA_API_KEY 未設定，無法查詢營養資訊。請在環境變數中設定 USDA_API_KEY")
        return None

    params = {
        'query': food_name,
        'api_key': USDA_API_KEY,
        'dataType': 'Branded',  # 優先搜尋品牌食品，結果通常更符合預期
        'pageSize': 1  # 我們只需要最相關的一筆結果
    }

    try:
        logger.info(f"正在向 USDA API 查詢食物：{food_name}")
        response = requests.get(USDA_API_URL, params=params)
        response.raise_for_status()  # 如果請求失敗 (例如 4xx 或 5xx)，則會拋出異常

        data = response.json()

        # 檢查是否有找到食物
        if data.get('foods') and len(data['foods']) > 0:
            food_data = data['foods'][0]  # 取第一個最相關的結果
            logger.info(f"從 API 成功獲取到食物 '{food_data.get('description')}' 的資料")
            
            nutrition_info = {
                "food_name": food_data.get('description', food_name).capitalize(),
                "chinese_name": None,  # USDA API 不提供中文名
            }

            # 遍歷我們需要的營養素
            extracted_nutrients = {key: 0.0 for key in NUTRIENT_MAP.keys()} # 初始化
            
            for nutrient in food_data.get('foodNutrients', []):
                for key, name in NUTRIENT_MAP.items():
                    if nutrient.get('nutrientName').strip().lower() == name.strip().lower():
                        # 將值存入我們的格式
                        extracted_nutrients[key] = float(nutrient.get('value', 0.0))
                        break # 找到後就跳出內層迴圈

            nutrition_info.update(extracted_nutrients)
            
            # 由於 USDA 不直接提供健康建議，我們先回傳原始數據
            # 後續可以在 main.py 中根據這些數據生成我們自己的建議
            return nutrition_info

        else:
            logger.warning(f"在 USDA API 中找不到食物：{food_name}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"請求 USDA API 時發生錯誤: {e}")
        return None
    except Exception as e:
        logger.error(f"處理 API 回應時發生未知錯誤: {e}")
        return None

if __name__ == '__main__':
    # 測試此模組的功能
    test_food = "donuts"
    nutrition = fetch_nutrition_data(test_food)
    if nutrition:
        import json
        print(f"成功獲取 '{test_food}' 的營養資訊:")
        print(json.dumps(nutrition, indent=2))
    else:
        print(f"無法獲取 '{test_food}' 的營養資訊。") 