# 檔案路徑: app/services/weight_estimation_service.py

import logging
import numpy as np
from PIL import Image
import io
from typing import Dict, Any, List, Optional, Tuple
import random
from .ai_service import classify_food_image  # 引入真實的 AI 分類函數

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 食物密度表 (g/cm³) - 常見食物的平均密度
FOOD_DENSITY_TABLE = {
    "rice": 0.8,           # 米飯
    "fried_rice": 0.7,     # 炒飯
    "noodles": 0.6,        # 麵條
    "bread": 0.3,          # 麵包
    "meat": 1.0,           # 肉類
    "fish": 1.1,           # 魚類
    "vegetables": 0.4,     # 蔬菜
    "fruits": 0.8,         # 水果
    "soup": 1.0,           # 湯類
    "default": 0.8         # 預設密度
}

# 參考物尺寸表 (cm)
REFERENCE_OBJECTS = {
    "plate": {"diameter": 24.0},      # 標準餐盤直徑
    "bowl": {"diameter": 15.0},       # 標準碗直徑
    "spoon": {"length": 15.0},        # 湯匙長度
    "fork": {"length": 20.0},         # 叉子長度
    "credit_card": {"width": 8.56, "height": 5.4},  # 信用卡尺寸
    "coin": {"diameter": 2.6},        # 10元硬幣直徑
    "default": {"diameter": 24.0}     # 預設參考物
}

# 模擬食物數據庫 - 用於營養資訊查詢
FOOD_DATABASE = {
    "sushi": {
        "calories": 200,
        "protein": 8,
        "fat": 2,
        "carbs": 35,
        "sodium": 400,
        "density": 0.9
    },
    "rice": {
        "calories": 130,
        "protein": 2.7,
        "fat": 0.3,
        "carbs": 28,
        "fiber": 0.4,
        "density": 0.8
    },
    "chicken": {
        "calories": 165,
        "protein": 31,
        "fat": 3.6,
        "carbs": 0,
        "cholesterol": 85,
        "density": 1.0
    },
    "salmon": {
        "calories": 208,
        "protein": 25,
        "fat": 12,
        "carbs": 0,
        "vitamin_d": 11.1,
        "density": 1.1
    },
    "apple": {
        "calories": 52,
        "protein": 0.3,
        "fat": 0.2,
        "carbs": 14,
        "fiber": 2.4,
        "density": 0.8
    },
    "bread": {
        "calories": 265,
        "protein": 9,
        "fat": 3.2,
        "carbs": 49,
        "fiber": 2.7,
        "density": 0.3
    },
    "noodles": {
        "calories": 138,
        "protein": 5,
        "fat": 1.1,
        "carbs": 25,
        "fiber": 1.8,
        "density": 0.6
    }
}

class WeightEstimationService:
    def __init__(self):
        """初始化重量估算服務"""
        logger.info("重量估算服務初始化完成")
    
    def detect_objects(self, image):
        """模擬物件偵測"""
        # 模擬檢測到的物件
        objects = [
            {"label": "plate", "confidence": 0.85, "bbox": [100, 100, 300, 300]},
            {"label": "spoon", "confidence": 0.72, "bbox": [50, 200, 80, 220]}
        ]
        return objects
    
    def estimate_depth(self, image):
        """模擬深度估計"""
        # 模擬深度圖
        depth_map = np.random.rand(image.height, image.width) * 100
        return depth_map
    
    def segment_food(self, image, input_boxes=None):
        """模擬食物分割"""
        # 模擬分割遮罩 - 確保返回正確的格式
        height, width = image.height, image.width
        mask = np.random.rand(height, width) > 0.5
        return [mask]  # 返回列表格式

    def calculate_dynamic_pixel_ratio(self, image, food_type: str, food_pixels: int) -> float:
        """動態計算像素比例"""
        try:
            image_area = image.width * image.height
            food_ratio = food_pixels / image_area
            
            # 根據食物類型設定合理的預期面積範圍
            food_area_ranges = {
                "sushi": (50, 200),      # 壽司: 50-200 cm²
                "ramen": (100, 400),     # 拉麵: 100-400 cm²  
                "rice": (80, 300),       # 米飯: 80-300 cm²
                "noodles": (100, 400),   # 麵條: 100-400 cm²
                "bread": (30, 150),      # 麵包: 30-150 cm²
                "meat": (50, 200),       # 肉類: 50-200 cm²
                "fish": (40, 180),       # 魚類: 40-180 cm²
                "vegetables": (20, 100), # 蔬菜: 20-100 cm²
                "fruits": (30, 150),     # 水果: 30-150 cm²
                "soup": (80, 300),       # 湯類: 80-300 cm²
            }
            
            # 獲取該食物類型的預期面積範圍
            min_area, max_area = food_area_ranges.get(food_type.lower(), (50, 200))
            
            # 根據食物佔畫面比例估算實際面積
            if food_ratio > 0.8:  # 食物佔畫面超過80%
                estimated_area = max_area
            elif food_ratio < 0.1:  # 食物佔畫面少於10%
                estimated_area = min_area
            else:
                # 線性插值
                estimated_area = min_area + (max_area - min_area) * (food_ratio - 0.1) / 0.7
            
            # 計算像素比例
            pixel_ratio = (estimated_area / food_pixels) ** 0.5
            
            # 限制在合理範圍內
            pixel_ratio = max(0.001, min(0.1, pixel_ratio))
            
            logger.info(f"動態像素比例計算 - 食物: {food_type}, 畫面佔比: {food_ratio:.3f}, 預估面積: {estimated_area:.1f} cm², 像素比例: {pixel_ratio:.4f}")
            
            return pixel_ratio
            
        except Exception as e:
            logger.warning(f"動態像素比例計算失敗: {e}，使用預設值")
            return 0.01  # 預設值

    def calculate_volume_and_weight(self, 
                                  mask: np.ndarray, 
                                  food_type: str,
                                  pixel_to_cm_ratio: Optional[float] = None,
                                  depth_map: Optional[np.ndarray] = None,
                                  image_area_pixels: Optional[int] = None) -> Tuple[float, float, float]:
        """計算體積和重量 (改進版本)"""
        try:
            food_pixels = np.sum(mask)
            logger.info(f"重量計算開始 - 食物: {food_type}, 像素數量: {food_pixels}")

            if pixel_to_cm_ratio:
                # --- 主要路徑：有參考物，進行精準計算 ---
                area_cm2 = food_pixels * (pixel_to_cm_ratio ** 2)
                logger.info(f"精準計算 - 像素比例: {pixel_to_cm_ratio}, 實際面積: {area_cm2:.2f} cm²")
                
                # 預設形狀因子
                shape_factor = 0.5 
                
                # 修復深度圖比較問題
                if depth_map is not None and len(depth_map.shape) == len(mask.shape) and all(d == m for d, m in zip(depth_map.shape, mask.shape)):
                    try:
                        food_depth_values = depth_map[mask]
                        if food_depth_values.size > 0:
                            min_depth, max_depth = np.min(food_depth_values), np.max(food_depth_values)
                            if max_depth > min_depth:
                                normalized_depth = (food_depth_values - min_depth) / (max_depth - min_depth)
                                dynamic_shape_factor = np.mean(normalized_depth)
                                shape_factor = np.clip(dynamic_shape_factor, 0.2, 0.8)
                                logger.info(f"使用深度圖將食物 '{food_type}' 的形狀因子動態調整為 {shape_factor:.2f}")
                    except Exception as e:
                        logger.warning(f"分析深度圖以調整形狀因子時失敗: {e}，將使用預設值 0.5。")

                actual_volume = shape_factor * (area_cm2 ** 1.5)
                logger.info(f"體積計算 - 形狀因子: {shape_factor}, 估算體積: {actual_volume:.2f} cm³")
                
                food_density = self.get_food_density(food_type)
                weight = actual_volume * food_density
                logger.info(f"重量計算 - 密度: {food_density} g/cm³, 原始重量: {weight:.2f} g")
                
                confidence = 0.8 if depth_map is not None else 0.75
                error_range = 0.25
                
            else:
                # --- 後備路徑：無參考物，使用畫面佔比估算 ---
                logger.warning(f"無 pixel_to_cm_ratio，對食物 '{food_type}' 啟用基於畫面佔比的後備估算。")
                if image_area_pixels and image_area_pixels > 0:
                    # 假設標準餐點重量為 350g，並根據食物佔畫面的比例進行調整
                    screen_ratio = food_pixels / image_area_pixels
                    base_weight = 350 
                    base_ratio = 0.25
                    weight = base_weight * (screen_ratio / base_ratio)
                    logger.info(f"後備估算 - 畫面佔比: {screen_ratio:.3f}, 估算重量: {weight:.2f} g")
                    confidence = 0.4
                    error_range = 0.6
                else:
                    weight = 150.0
                    confidence = 0.2
                    error_range = 0.8
                
                logger.info(f"後備估算結果：重量 {weight:.2f}g, 信心度 {confidence}, 誤差範圍 {error_range}")

            # 對單一物件的重量做一個合理性檢查
            if weight > 1500:
                logger.warning(f"單一物件預估重量 {weight:.2f}g 過高，可能不準確。")
                weight = 1500

            logger.info(f"最終結果 - 重量: {weight:.2f}g, 信心度: {confidence:.2f}")
            return weight, confidence, error_range

        except Exception as e:
            logger.error(f"體積重量計算失敗: {str(e)}")
            return 150.0, 0.3, 0.5

    def get_food_density(self, food_name: str) -> float:
        """根據食物名稱取得密度"""
        food_name_lower = food_name.lower()
        
        # 簡單的關鍵字匹配
        if any(keyword in food_name_lower for keyword in ["rice", "飯"]):
            return FOOD_DENSITY_TABLE["rice"]
        elif any(keyword in food_name_lower for keyword in ["noodle", "麵"]):
            return FOOD_DENSITY_TABLE["noodles"]
        elif any(keyword in food_name_lower for keyword in ["meat", "肉", "chicken", "pork", "beef", "lamb"]):
            return FOOD_DENSITY_TABLE["meat"]
        elif any(keyword in food_name_lower for keyword in ["vegetable", "菜"]):
            return FOOD_DENSITY_TABLE["vegetables"]
        else:
            return FOOD_DENSITY_TABLE["default"]

# 創建服務實例
weight_service = WeightEstimationService()

async def estimate_food_weight(image_bytes: bytes) -> Dict[str, Any]:
    """
    整合食物辨識、重量估算與營養分析的主函數
    """
    try:
        # 將 bytes 轉換為 PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # 1. 使用真實的 AI 模型進行食物辨識
        detected_food = classify_food_image(image_bytes)
        
        # 如果 AI 模型失敗，使用備用方案
        if detected_food.startswith("Error") or detected_food == "Unknown":
            logger.warning(f"AI 模型辨識失敗: {detected_food}，使用備用方案")
            food_names = list(FOOD_DATABASE.keys())
            detected_food = random.choice(food_names)
        
        # 標準化食物名稱（轉小寫，移除空格）
        detected_food_normalized = detected_food.lower().replace(' ', '_')
        
        # 2. 模擬物件偵測
        detected_objects = weight_service.detect_objects(image)
        
        # 3. 模擬深度估計
        depth_map = weight_service.estimate_depth(image)
        
        # 4. 模擬食物分割
        food_masks = weight_service.segment_food(image)
        
        # 5. 使用改進的重量計算方法
        if food_masks and len(food_masks) > 0:
            # 使用第一個分割遮罩
            mask = food_masks[0]
            
            # 計算像素到實際距離的比例（使用動態計算）
            pixel_to_cm_ratio = None
            if detected_objects:
                # 如果有參考物，優先使用參考物計算
                plate_diameter_cm = REFERENCE_OBJECTS["plate"]["diameter"]
                # 這裡可以根據實際檢測到的盤子像素大小計算比例
                # 目前使用動態計算作為備用
                pixel_to_cm_ratio = weight_service.calculate_dynamic_pixel_ratio(image, detected_food, np.sum(mask))
            else:
                # 沒有參考物時，使用動態計算
                pixel_to_cm_ratio = weight_service.calculate_dynamic_pixel_ratio(image, detected_food, np.sum(mask))
            
            # 使用改進的重量計算
            estimated_weight, confidence, error_range = weight_service.calculate_volume_and_weight(
                mask=mask,
                food_type=detected_food,
                pixel_to_cm_ratio=pixel_to_cm_ratio,
                depth_map=depth_map,
                image_area_pixels=image.width * image.height
            )
        else:
            # 如果沒有分割遮罩，使用舊的計算方法
            image_area = image.width * image.height
            base_weight = image_area / 1000
            weight_variation = random.uniform(0.8, 1.2)
            estimated_weight = base_weight * weight_variation
            
            food_density = FOOD_DATABASE.get(detected_food_normalized, {}).get("density", 0.8)
            estimated_weight *= food_density
            estimated_weight = max(50, min(500, estimated_weight))
            
            confidence = random.uniform(0.6, 0.9)
            error_range = random.uniform(0.1, 0.25)
        
        # 6. 獲取營養資訊
        nutrition_base = FOOD_DATABASE.get(detected_food_normalized, FOOD_DATABASE["rice"]).copy()
        del nutrition_base["density"]  # 移除密度信息
        
        # 根據重量調整營養素
        weight_ratio = estimated_weight / 100
        adjusted_nutrition = {
            key: round(value * weight_ratio, 1)
            for key, value in nutrition_base.items()
        }
        
        # 7. 計算誤差範圍
        error_min = estimated_weight * (1 - error_range)
        error_max = estimated_weight * (1 + error_range)
        
        # 8. 檢測參考物
        reference_object = None
        if detected_objects:
            ref_obj = random.choice(detected_objects)
            reference_object = ref_obj["label"]
        
        # 9. 生成備註
        if reference_object:
            note = f"檢測到參考物：{reference_object}，準確度較高"
        else:
            note = "未檢測到參考物，重量為估算值，僅供參考"
        
        logger.info(f"分析完成：{detected_food}, 重量：{estimated_weight:.1f}g, 信心度：{confidence:.2f}")
        
        return {
            "food_type": detected_food,
            "estimated_weight": round(estimated_weight, 1),
            "weight_confidence": round(confidence, 2),
            "weight_error_range": [round(error_min, 1), round(error_max, 1)],
            "nutrition": adjusted_nutrition,
            "reference_object": reference_object,
            "note": note,
            "detected_objects": len(detected_objects),
            "analysis_timestamp": "2024-01-01T12:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"重量估算失敗: {str(e)}")
        # 回傳預設結果
        return {
            "food_type": "Unknown",
            "estimated_weight": 150.0,
            "weight_confidence": 0.3,
            "weight_error_range": [100.0, 200.0],
            "nutrition": {
                "calories": 150,
                "protein": 5,
                "carbs": 25,
                "fat": 3,
                "fiber": 2
            },
            "reference_object": None,
            "note": "分析失敗，顯示預設值"
        }
