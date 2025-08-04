# 檔案路徑: app/services/weight_estimation_service_v2.py

import logging
import numpy as np
from PIL import Image
import io
from typing import Dict, Any, List, Optional, Tuple
import torch
import cv2

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

class WeightEstimationServiceV2:
    """
    重量估算服務 V2 - 整合輕量化模型服務
    支持多種替代模型選擇，包括 MobileSAM、DPT SwinV2-Tiny 等
    """
    
    def __init__(self, model_config: Optional[Dict[str, str]] = None):
        """
        初始化重量估算服務 V2
        
        Args:
            model_config: 模型配置字典，可指定具體的模型
        """
        self.model_config = model_config or {
            "detection": "yolov5n",  # 物件偵測
            "segmentation": "mobilesam",  # 圖像分割
            "depth": "dpt_swinv2_tiny"  # 深度估計
        }
        
        # 載入輕量化模型服務
        from .lightweight_model_service import LightweightModelService
        self.model_service = LightweightModelService(model_config)
        
        logger.info(f"✅ 重量估算服務 V2 初始化完成，使用配置: {self.model_config}")
    
    def detect_objects(self, image: Image.Image) -> List[Dict[str, Any]]:
        """使用輕量化模型服務偵測圖片中的所有物體"""
        return self.model_service.detect_objects(image)
    
    def segment_food(self, image: Image.Image, input_boxes: List[List[float]]) -> List[np.ndarray]:
        """使用輕量化模型服務分割食物區域"""
        return self.model_service.segment_food(image, input_boxes)
    
    def estimate_depth(self, image: Image.Image) -> Optional[np.ndarray]:
        """使用輕量化模型服務進行深度估計"""
        return self.model_service.estimate_depth(image)

    def calculate_volume_and_weight(self, 
                                  mask: np.ndarray, 
                                  food_type: str,
                                  pixel_to_cm_ratio: Optional[float] = None,
                                  depth_map: Optional[np.ndarray] = None,
                                  image_area_pixels: Optional[int] = None) -> Tuple[float, float, float]:
        """計算體積和重量 (V2 - 輕量化方案)"""
        try:
            food_pixels = np.sum(mask)

            if pixel_to_cm_ratio:
                # --- 主要路徑：有參考物，進行精準計算 ---
                area_cm2 = food_pixels * (pixel_to_cm_ratio ** 2)
                
                # 預設形狀因子
                shape_factor = 0.5 
                
                if depth_map is not None and depth_map.shape == mask.shape:
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
                
                weight = actual_volume * self.get_food_density(food_type)
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
    
    def get_model_info(self) -> Dict[str, Any]:
        """獲取當前使用的模型資訊"""
        return self.model_service.get_model_info()
    
    def test_model_performance(self, test_image: Image.Image) -> Dict[str, Any]:
        """測試模型性能"""
        return self.model_service.test_model_performance(test_image)

# 全域服務實例
weight_service_v2 = WeightEstimationServiceV2()

async def estimate_food_weight_v2(image_bytes: bytes, 
                                model_config: Optional[Dict[str, str]] = None,
                                debug: bool = False) -> Dict[str, Any]:
    """
    整合食物辨識、重量估算與營養分析的主函數 (V2 - 輕量化方案)
    使用可配置的輕量化模型組合
    """
    debug_dir = None
    try:
        if debug:
            import os
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            debug_dir = os.path.join("debug_output", timestamp)
            os.makedirs(debug_dir, exist_ok=True)
            
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        if debug:
            image.save(os.path.join(debug_dir, "00_original.jpg"))
        
        # 創建服務實例（如果提供了配置）
        if model_config:
            service = WeightEstimationServiceV2(model_config)
        else:
            service = weight_service_v2
        
        # 1. 物件偵測，取得所有物件的邊界框
        all_objects = service.detect_objects(image)
        image_area_pixels = image.width * image.height

        if not all_objects:
            note = "無法從圖片中偵測到任何物體。"
            result = {"detected_foods": [], "total_estimated_weight": 0, "total_nutrition": {}, "note": note}
            if debug: result["debug_output_path"] = debug_dir
            return result

        if debug:
            from PIL import ImageDraw
            debug_image = image.copy()
            draw = ImageDraw.Draw(debug_image)
            for obj in all_objects:
                bbox = obj.get("bbox")
                label = obj.get("label", "unknown")
                draw.rectangle(bbox, outline="red", width=3)
                draw.text((bbox[0], bbox[1]), label, fill="red")
            debug_image.save(os.path.join(debug_dir, "01_detected_objects.jpg"))
            
        # 2. 計算全域 pixel_to_cm_ratio
        pixel_to_cm_ratio = None
        reference_object_label = None
        
        # 所有偵測到的參考物候選
        all_ref_candidates = [obj for obj in all_objects if obj["label"] in ["plate", "bowl", "credit_card", "coin"]]

        logger.info(f"偵測到 {len(all_ref_candidates)} 個參考物候選: {[o['label'] for o in all_ref_candidates]}")
        for obj in all_ref_candidates:
            bbox = obj.get("bbox")
            bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            area_percentage = (bbox_area / image_area_pixels) * 100
            logger.info(f"候選參考物 '{obj['label']}' 佔畫面 {area_percentage:.2f}% (Bbox: {[int(c) for c in bbox]})")

        # 可靠的參考物（通過尺寸檢測）
        potential_refs = [
            obj for obj in all_ref_candidates 
            if (obj["bbox"][2]-obj["bbox"][0]) * (obj["bbox"][3]-obj["bbox"][1]) > image_area_pixels * 0.01
        ]

        if potential_refs:
            # 選擇最大的參考物
            best_ref = max(potential_refs, key=lambda obj: (obj["bbox"][2]-obj["bbox"][0]) * (obj["bbox"][3]-obj["bbox"][1]))
            reference_object_label = best_ref["label"]
            ref_type = best_ref.get("label")
            ref_bbox = best_ref.get("bbox")
            ref_size_cm = REFERENCE_OBJECTS.get(ref_type)

            if ref_size_cm and ref_bbox:
                px_w = ref_bbox[2] - ref_bbox[0]
                px_h = ref_bbox[3] - ref_bbox[1]
                
                if "diameter" in ref_size_cm and px_w > 0:
                    # 圓形參考物 (盤子、碗、硬幣)
                    px_diameter = px_w
                    pixel_to_cm_ratio = ref_size_cm["diameter"] / px_diameter
                    logger.info(f"成功使用圓形參考物 '{reference_object_label}' ({px_diameter:.1f} px) 計算出 pixel_to_cm_ratio: {pixel_to_cm_ratio:.4f}")
                elif "width" in ref_size_cm and "height" in ref_size_cm and px_w > 0 and px_h > 0:
                    # 矩形參考物 (信用卡)
                    pixel_to_cm_ratio = ref_size_cm["width"] / px_w
                    logger.info(f"成功使用矩形參考物 '{reference_object_label}' ({px_w:.1f}x{px_h:.1f} px) 計算出 pixel_to_cm_ratio: {pixel_to_cm_ratio:.4f}")
            
            if not pixel_to_cm_ratio:
                 reference_object_label = None
                 logger.warning(f"偵測到參考物 '{best_ref['label']}'，但計算其比例失敗。")

        # 3. 深度估計
        depth_map = service.estimate_depth(image)
        if debug and depth_map is not None:
            depth_for_save = (depth_map - np.min(depth_map)) / (np.max(depth_map) - np.min(depth_map) + 1e-6) * 255.0
            Image.fromarray(depth_for_save.astype(np.uint8)).convert("L").save(os.path.join(debug_dir, "03_depth_map.png"))

        # 4. 載入相關服務
        from .ai_service import classify_food_image
        from .nutrition_api_service import fetch_nutrition_data

        detected_foods = []
        total_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0}
        
        food_objects = [obj for obj in all_objects if obj["label"] not in ["plate", "bowl", "credit_card", "coin"]]

        for i, food_obj in enumerate(food_objects):
            try:
                # a. 分割
                input_box = [food_obj["bbox"]]
                masks = service.segment_food(image, input_boxes=input_box)
                if not masks: continue
                mask = max(masks, key=lambda m: np.sum(m))

                # 遮罩過濾器
                mask_pixels = np.sum(mask)
                if mask_pixels > image_area_pixels * 0.9:
                    logger.warning(f"過濾掉一個可疑的過大食物遮罩 (來自 YOLO 的 '{food_obj['label']}'), 其遮罩佔據了畫面的 {mask_pixels / image_area_pixels:.2%}。")
                    continue

                # b. 裁切 (辨識用)
                if mask.ndim == 3: mask = mask[0]
                if mask.ndim != 2: continue
                rows, cols = np.any(mask, axis=1), np.any(mask, axis=0)
                if not np.any(rows) or not np.any(cols): continue
                rmin, rmax = np.where(rows)[0][[0, -1]]
                cmin, cmax = np.where(cols)[0][[0, -1]]
                item_array = np.array(image); item_rgba = np.zeros((*item_array.shape[:2], 4), dtype=np.uint8)
                item_rgba[:,:,:3] = item_array; item_rgba[:,:,3] = mask * 255
                cropped_pil = Image.fromarray(item_rgba[rmin:rmax+1, cmin:cmax+1, :], 'RGBA')
                buffer = io.BytesIO(); cropped_pil.save(buffer, format="PNG"); item_image_bytes = buffer.getvalue()
                if debug:
                    cropped_pil.save(os.path.join(debug_dir, f"item_{i}_{food_obj['label']}_cropped.png"))

                # c. 辨識
                food_name = classify_food_image(item_image_bytes)
                
                # d. 計算體積和重量
                weight, confidence, error_range = service.calculate_volume_and_weight(
                    mask, 
                    food_name, 
                    pixel_to_cm_ratio=pixel_to_cm_ratio,
                    depth_map=depth_map,
                    image_area_pixels=image_area_pixels
                )
                
                # e. 查詢營養資訊
                nutrition_info = fetch_nutrition_data(food_name)
                if nutrition_info is None:
                    nutrition_info = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0}

                # f. 根據重量調整營養素
                weight_ratio = weight / 100
                adjusted_nutrition = {k: v * weight_ratio for k, v in nutrition_info.items() if isinstance(v, (int, float))}
                
                # g. 累加總營養
                for key in total_nutrition: total_nutrition[key] += adjusted_nutrition.get(key, 0)

                # h. 儲存單項食物結果
                detected_foods.append({
                    "food_name": food_name,
                    "estimated_weight": round(weight, 1),
                    "nutrition": {k: round(v, 1) for k, v in adjusted_nutrition.items()}
                })
            except Exception as item_e:
                logger.error(f"處理物件 '{food_obj['label']}' 時失敗: {str(item_e)}")
                continue

        # 5. 智慧後備機制
        if not detected_foods:
            logger.info("主要重量估算流程未偵測到有效食物，啟用後備食物辨識模型。")
            try:
                fallback_food_name = classify_food_image(image_bytes)
                
                if fallback_food_name and fallback_food_name.lower() not in ['unknown', 'other']:
                    logger.info(f"後備模型辨識出食物為: {fallback_food_name}")
                    note = f"AI 重量估算失敗，但圖片辨識模型認為食物可能是「{fallback_food_name}」。請參考並手動輸入重量。"
                    result = {
                        "detected_foods": [],
                        "total_estimated_weight": 0,
                        "total_nutrition": {},
                        "reference_object": None,
                        "note": note,
                        "fallback_food_suggestion": { "food_name": fallback_food_name },
                        "model_info": service.get_model_info()
                    }
                    if debug: result["debug_output_path"] = debug_dir
                    return result

            except Exception as fallback_e:
                logger.error(f"後備食物辨識模型失敗: {fallback_e}")

        # 6. 生成備註
        if detected_foods:
            if pixel_to_cm_ratio and reference_object_label:
                note = f"已使用 '{reference_object_label}' 作為參考物，成功分析 {len(detected_foods)} 項食物，準確度較高。"
            elif all_ref_candidates:
                too_small_ref_labels = list(set([o['label'] for o in all_ref_candidates]))
                note = f"警告：雖偵測到 {too_small_ref_labels}，但其佔比過小無法作為精準參考。結果為AI基於畫面比例估算，僅供參考。"
            else:
                note = f"未能找到可靠參考物。結果為AI基於畫面比例估算，僅供參考。"
        else:
            note = "分析失敗：AI 無法辨識出任何可信的食物項目。請嘗試手動搜尋。"

        result = {
            "detected_foods": detected_foods,
            "total_estimated_weight": round(sum(item['estimated_weight'] for item in detected_foods), 1),
            "total_nutrition": {k: round(v, 1) for k, v in total_nutrition.items()},
            "reference_object": reference_object_label,
            "note": note,
            "model_info": service.get_model_info()
        }
        
        if debug:
            from PIL import ImageDraw
            overlay_img = image.copy()
            overlay_array = np.array(overlay_img)
            all_food_boxes = [obj['bbox'] for obj in food_objects]
            if all_food_boxes:
                all_masks = service.segment_food(image, input_boxes=all_food_boxes)
                for mask in all_masks:
                    color = np.random.randint(0, 255, size=3, dtype=np.uint8)
                    if mask.ndim == 3: mask = mask[0]
                    overlay_array[mask] = (overlay_array[mask] * 0.5 + color * 0.5).astype(np.uint8)
            Image.fromarray(overlay_array).save(os.path.join(debug_dir, "02_final_segmentation.jpg"))
            result["debug_output_path"] = debug_dir
            
        return result
        
    except Exception as e:
        logger.error(f"多食物重量估算主流程失敗: {str(e)}")
        result = {
            "detected_foods": [],
            "total_estimated_weight": 0,
            "total_nutrition": {},
            "reference_object": None,
            "note": f"分析失敗: {str(e)}"
        }
        if debug and debug_dir:
            result["debug_output_path"] = debug_dir
        return result 