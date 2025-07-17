# 檔案路徑: backend/app/services/weight_estimation_service.py

import logging
import numpy as np
from PIL import Image
import io
from typing import Dict, Any, List, Optional, Tuple
import torch

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
    "default": {"diameter": 24.0}     # 預設參考物
}

class WeightEstimationService:
    def __init__(self):
        """初始化重量估算服務"""
        self.sam_model = None
        self.dpt_model = None
        self.detection_model = None
        self._load_models()
    
    def _load_models(self):
        """載入所需的 AI 模型"""
        try:
            # 載入 SAM 分割模型
            from transformers import SamModel, SamProcessor
            logger.info("正在載入 SAM 分割模型...")
            self.sam_model = SamModel.from_pretrained("facebook/sam-vit-base")
            self.sam_processor = SamProcessor.from_pretrained("facebook/sam-vit-base")
            
            # 載入 DPT 深度估計模型
            from transformers import pipeline
            logger.info("正在載入 DPT 深度估計模型...")
            self.dpt_model = pipeline("depth-estimation", model="Intel/dpt-large")
            
            # 載入物件偵測模型（用於偵測參考物）
            logger.info("正在載入物件偵測模型...")
            self.detection_model = pipeline("object-detection", model="ultralytics/yolov5")
            
            logger.info("所有模型載入完成！")
            
        except Exception as e:
            logger.error(f"模型載入失敗: {str(e)}")
            raise
    
    def detect_reference_objects(self, image: Image.Image) -> Optional[Dict[str, Any]]:
        """偵測圖片中的參考物（餐盤、餐具等）"""
        try:
            # 使用 YOLOv5 偵測物件
            results = self.detection_model(image)
            
            reference_objects = []
            for result in results:
                label = result["label"].lower()
                confidence = result["score"]
                
                # 檢查是否為參考物
                if any(ref in label for ref in ["plate", "bowl", "spoon", "fork", "knife"]):
                    reference_objects.append({
                        "type": label,
                        "confidence": confidence,
                        "bbox": result["box"]
                    })
            
            if reference_objects:
                # 選擇信心度最高的參考物
                best_ref = max(reference_objects, key=lambda x: x["confidence"])
                return best_ref
            
            return None
            
        except Exception as e:
            logger.warning(f"參考物偵測失敗: {str(e)}")
            return None
    
    def segment_food(self, image: Image.Image) -> np.ndarray:
        """使用 SAM 分割食物區域"""
        try:
            # 使用 SAM 進行分割
            inputs = self.sam_processor(image, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.sam_model(**inputs)
            
            # 取得分割遮罩
            masks = self.sam_processor.image_processor.post_process_masks(
                outputs.pred_masks.sigmoid(), 
                inputs["original_sizes"], 
                inputs["reshaped_input_sizes"]
            )[0]
            
            # 選擇最大的遮罩作為食物區域
            mask = masks[0].numpy()  # 簡化處理，選擇第一個遮罩
            
            return mask
            
        except Exception as e:
            logger.error(f"食物分割失敗: {str(e)}")
            # 回傳一個簡單的遮罩（整個圖片）
            return np.ones((image.height, image.width), dtype=bool)
    
    def estimate_depth(self, image: Image.Image) -> np.ndarray:
        """使用 DPT 進行深度估計"""
        try:
            # 使用 DPT 進行深度估計
            depth_result = self.dpt_model(image)
            depth_map = depth_result["depth"]
            
            return np.array(depth_map)
            
        except Exception as e:
            logger.error(f"深度估計失敗: {str(e)}")
            # 回傳一個預設的深度圖
            return np.ones((image.height, image.width))
    
    def calculate_volume_and_weight(self, 
                                  mask: np.ndarray, 
                                  depth_map: np.ndarray, 
                                  food_type: str,
                                  reference_object: Optional[Dict[str, Any]] = None) -> Tuple[float, float, float]:
        """計算體積和重量"""
        try:
            # 計算食物區域的像素數量
            food_pixels = np.sum(mask)
            
            # 計算食物區域的平均深度
            food_depth = np.mean(depth_map[mask])
            
            # 估算體積（相對體積）
            relative_volume = food_pixels * food_depth
            
            # 如果有參考物，進行尺寸校正
            if reference_object:
                ref_type = reference_object["type"]
                if ref_type in REFERENCE_OBJECTS:
                    ref_size = REFERENCE_OBJECTS[ref_type]
                    # 根據參考物尺寸校正體積
                    if "diameter" in ref_size:
                        # 圓形參考物（如餐盤）
                        pixel_to_cm_ratio = ref_size["diameter"] / np.sqrt(food_pixels / np.pi)
                    else:
                        # 線性參考物（如餐具）
                        pixel_to_cm_ratio = ref_size["length"] / np.sqrt(food_pixels)
                    
                    # 校正體積
                    actual_volume = relative_volume * (pixel_to_cm_ratio ** 3)
                    confidence = 0.85  # 有參考物時信心度較高
                    error_range = 0.15  # ±15% 誤差
                else:
                    actual_volume = relative_volume * 0.1  # 預設校正係數
                    confidence = 0.6
                    error_range = 0.3
            else:
                # 無參考物，使用預設值
                actual_volume = relative_volume * 0.1  # 預設校正係數
                confidence = 0.5  # 無參考物時信心度較低
                error_range = 0.4  # ±40% 誤差
            
            # 根據食物類型取得密度
            density = FOOD_DENSITY_TABLE.get(food_type.lower(), FOOD_DENSITY_TABLE["default"])
            
            # 計算重量 (g)
            weight = actual_volume * density
            
            return weight, confidence, error_range
            
        except Exception as e:
            logger.error(f"體積重量計算失敗: {str(e)}")
            return 150.0, 0.3, 0.5  # 預設值
    
    def get_food_density(self, food_name: str) -> float:
        """根據食物名稱取得密度"""
        food_name_lower = food_name.lower()
        
        # 簡單的關鍵字匹配
        if any(keyword in food_name_lower for keyword in ["rice", "飯"]):
            return FOOD_DENSITY_TABLE["rice"]
        elif any(keyword in food_name_lower for keyword in ["noodle", "麵"]):
            return FOOD_DENSITY_TABLE["noodles"]
        elif any(keyword in food_name_lower for keyword in ["meat", "肉"]):
            return FOOD_DENSITY_TABLE["meat"]
        elif any(keyword in food_name_lower for keyword in ["vegetable", "菜"]):
            return FOOD_DENSITY_TABLE["vegetables"]
        else:
            return FOOD_DENSITY_TABLE["default"]

# 全域服務實例
weight_service = WeightEstimationService()

async def estimate_food_weight(image_bytes: bytes) -> Dict[str, Any]:
    """
    整合食物辨識、重量估算與營養分析的主函數
    """
    try:
        # 將 bytes 轉換為 PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # 1. 食物辨識（使用現有的 AI 服務）
        from .ai_service import classify_food_image
        food_name = classify_food_image(image_bytes)
        
        # 2. 偵測參考物
        reference_object = weight_service.detect_reference_objects(image)
        
        # 3. 食物分割
        food_mask = weight_service.segment_food(image)
        
        # 4. 深度估計
        depth_map = weight_service.estimate_depth(image)
        
        # 5. 計算體積和重量
        weight, confidence, error_range = weight_service.calculate_volume_and_weight(
            food_mask, depth_map, food_name, reference_object
        )
        
        # 6. 查詢營養資訊
        from .nutrition_api_service import fetch_nutrition_data
        nutrition_info = fetch_nutrition_data(food_name)
        
        if nutrition_info is None:
            nutrition_info = {
                "calories": 150,
                "protein": 5,
                "carbs": 25,
                "fat": 3,
                "fiber": 2
            }
        
        # 7. 根據重量調整營養素
        weight_ratio = weight / 100  # 假設營養資訊是每100g的數據
        adjusted_nutrition = {
            key: value * weight_ratio 
            for key, value in nutrition_info.items()
        }
        
        # 8. 計算誤差範圍
        error_min = weight * (1 - error_range)
        error_max = weight * (1 + error_range)
        
        # 9. 生成備註
        if reference_object:
            note = f"檢測到參考物：{reference_object['type']}，準確度較高"
        else:
            note = "未檢測到參考物，重量為估算值，僅供參考"
        
        return {
            "food_type": food_name,
            "estimated_weight": round(weight, 1),
            "weight_confidence": round(confidence, 2),
            "weight_error_range": [round(error_min, 1), round(error_max, 1)],
            "nutrition": adjusted_nutrition,
            "reference_object": reference_object["type"] if reference_object else None,
            "note": note
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