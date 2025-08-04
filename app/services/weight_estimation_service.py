# 檔案路徑: app/services/weight_estimation_service.py

import logging
import numpy as np
from PIL import Image
import io
from typing import Dict, Any, List, Optional, Tuple
import torch
import cv2
from ultralytics import YOLO  # 使用 ultralytics 載入 YOLOv4

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

class WeightEstimationService:
    def __init__(self):
        """初始化重量估算服務"""
        self.sam_model = None
        self.sam_processor = None
        self.dpt_model = None
        self.detection_model = None
        self.class_names = None
        self._load_models()
    
    def _load_models(self):
        """載入所需的 AI 模型"""
        try:
            # 載入 SAM 分割模型 (使用標準版本作為備選)
            from transformers import SamModel, SamProcessor
            logger.info("正在載入 SAM 分割模型...")
            self.sam_model = SamModel.from_pretrained("facebook/sam-vit-base")
            self.sam_processor = SamProcessor.from_pretrained("facebook/sam-vit-base")
            
            # 載入 DPT 深度估計模型 (使用標準版本作為備選)
            from transformers import pipeline
            logger.info("正在載入 DPT 深度估計模型...")
            self.dpt_model = pipeline("depth-estimation", model="Intel/dpt-large")

            # 載入 YOLOv5n 物件偵測模型 (輕量化版本)
            logger.info("正在載入 YOLOv5n 物件偵測模型...")
            self.detection_model = YOLO('yolov5nu.pt')
            # 取得類別名稱
            self.class_names = self.detection_model.names if hasattr(self.detection_model, 'names') else None
            logger.info("所有輕量化模型載入完成！")
            
        except Exception as e:
            logger.error(f"模型載入失敗: {str(e)}")
            raise
    
    def detect_objects(self, image: Image.Image) -> List[Dict[str, Any]]:
        """使用 YOLOv5n 偵測圖片中的所有物體"""
        try:
            # 轉成 numpy array
            img_np = np.array(image)
            if img_np.shape[2] == 4:
                img_np = img_np[:, :, :3]  # 移除 alpha
            
            # 使用 YOLOv5n 進行偵測
            results = self.detection_model(img_np, conf=0.25)  # 降低信心度閾值
            
            detected_objects = []
            if results and len(results) > 0:
                result = results[0]  # 取第一個結果
                if result.boxes is not None:
                    for box in result.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        label = self.class_names[class_id].lower() if self.class_names else str(class_id)
                        
                        # 過濾掉餐具等小物件
                        if label not in ["spoon", "fork", "knife", "scissors", "toothbrush"]:
                            detected_objects.append({
                                "label": label,
                                "bbox": [float(x1), float(y1), float(x2), float(y2)],
                                "confidence": conf
                            })
            return detected_objects
        except Exception as e:
            logger.warning(f"物件偵測失敗: {str(e)}")
            return []
    
    def segment_food(self, image: Image.Image, input_boxes: List[List[float]]) -> List[np.ndarray]:
        """使用 SAM 根據提供的邊界框分割食物區域"""
        if not input_boxes:
            return []
        try:
            # 使用 SAM 進行分割，並提供邊界框作為提示
            inputs = self.sam_processor(image, input_boxes=input_boxes, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.sam_model(**inputs)
            
            # 取得分割遮罩
            masks_tensor = self.sam_processor.image_processor.post_process_masks(
                outputs.pred_masks.sigmoid(), 
                inputs["original_sizes"], 
                inputs["reshaped_input_sizes"]
            )[0]
            
            # 將 Tensor 轉換為 list of numpy arrays，並使用 0.5 的閾值進行二值化
            masks = [(m.squeeze().cpu().numpy() > 0.5) for m in masks_tensor]
            return masks
            
        except Exception as e:
            logger.error(f"食物分割失敗: {str(e)}")
            return []
    
    def estimate_depth(self, image: Image.Image) -> Optional[np.ndarray]:
        """使用 DPT 進行深度估計"""
        try:
            depth_result = self.dpt_model(image)
            depth_map = np.array(depth_result["depth"])
            return depth_map
        except Exception as e:
            logger.error(f"深度估計失敗: {str(e)}")
            return None

    def calculate_volume_and_weight(self, 
                                  mask: np.ndarray, 
                                  food_type: str,
                                  pixel_to_cm_ratio: Optional[float] = None,
                                  depth_map: Optional[np.ndarray] = None,
                                  image_area_pixels: Optional[int] = None) -> Tuple[float, float, float]:
        """計算體積和重量 (V6 - 全輕量化方案)"""
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
                    # 這是一個啟發式規則，假設圖片主要內容是食物
                    screen_ratio = food_pixels / image_area_pixels
                    # 預估重量 = 基礎重量 * (佔比 / 標準佔比)
                    # 假設標準食物佔畫面 25% 時約 350g
                    base_weight = 350 
                    base_ratio = 0.25
                    weight = base_weight * (screen_ratio / base_ratio)
                    confidence = 0.4
                    error_range = 0.6
                else:
                    # 如果連圖片面積都沒有，回傳一個固定的預設值
                    weight = 150.0
                    confidence = 0.2
                    error_range = 0.8
                
                logger.info(f"後備估算結果：重量 {weight:.2f}g, 信心度 {confidence}, 誤差範圍 {error_range}")

            # 對單一物件的重量做一個合理性檢查
            if weight > 1500:
                logger.warning(f"單一物件預估重量 {weight:.2f}g 過高，可能不準確。")
                weight = 1500 # 設定一個上限

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

# 全域服務實例
weight_service = WeightEstimationService()

async def estimate_food_weight(image_bytes: bytes, debug: bool = False) -> Dict[str, Any]:
    """
    整合食物辨識、重量估算與營養分析的主函數 (V6 - 輕量化方案)
    使用 YOLOv5n + SAM + DPT 組合
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
        
        # 1. 物件偵測 (YOLO)，取得所有物件的邊界框
        all_objects = weight_service.detect_objects(image)
        image_area_pixels = image.width * image.height # 先計算總像素

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
        
        # 所有偵測到的參考物候選 (擴充參考物類型)
        all_ref_candidates = [obj for obj in all_objects if obj["label"] in ["plate", "bowl", "credit_card", "coin"]]

        # --- 新增偵錯日誌 ---
        logger.info(f"偵測到 {len(all_ref_candidates)} 個參考物候選: {[o['label'] for o in all_ref_candidates]}")
        for obj in all_ref_candidates:
            bbox = obj.get("bbox")
            bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            area_percentage = (bbox_area / image_area_pixels) * 100
            logger.info(f"候選參考物 '{obj['label']}' 佔畫面 {area_percentage:.2f}% (Bbox: {[int(c) for c in bbox]})")
        # --- 結束偵錯日誌 ---

        # 可靠的參考物（通過尺寸檢測）
        potential_refs = [
            obj for obj in all_ref_candidates 
            if (obj["bbox"][2]-obj["bbox"][0]) * (obj["bbox"][3]-obj["bbox"][1]) > image_area_pixels * 0.01 # 佔比 > 1%，提高寬容度
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
                    # 使用寬度作為主要參考，因為信用卡的寬度更標準
                    pixel_to_cm_ratio = ref_size_cm["width"] / px_w
                    logger.info(f"成功使用矩形參考物 '{reference_object_label}' ({px_w:.1f}x{px_h:.1f} px) 計算出 pixel_to_cm_ratio: {pixel_to_cm_ratio:.4f}")
            
            if not pixel_to_cm_ratio:
                 reference_object_label = None # 計算失敗，重設標籤
                 logger.warning(f"偵測到參考物 '{best_ref['label']}'，但計算其比例失敗。")

        # 重新加入深度估計
        depth_map = weight_service.estimate_depth(image)
        if debug and depth_map is not None:
            depth_for_save = (depth_map - np.min(depth_map)) / (np.max(depth_map) - np.min(depth_map) + 1e-6) * 255.0
            Image.fromarray(depth_for_save.astype(np.uint8)).convert("L").save(os.path.join(debug_dir, "03_depth_map.png"))

        # 載入相關服務
        from .ai_service import classify_food_image
        from .nutrition_api_service import fetch_nutrition_data

        detected_foods = []
        total_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0}
        
        food_objects_raw = [obj for obj in all_objects if obj["label"] not in ["plate", "bowl", "credit_card", "coin"]]
        
        # 過濾器已移至迴圈內部，此處不再需要
        food_objects = food_objects_raw


        for i, food_obj in enumerate(food_objects):
            try:
                # a. 分割
                input_box = [[food_obj["bbox"]]]  # 修正邊界框格式：需要雙層列表
                masks = weight_service.segment_food(image, input_boxes=input_box)
                if not masks: continue
                mask = max(masks, key=lambda m: np.sum(m))

                # --- 新增遮罩過濾器 (更精準的防呆機制) ---
                mask_pixels = np.sum(mask)
                if mask_pixels > image_area_pixels * 0.95:  # 放寬到 95%
                    logger.warning(f"過濾掉一個可疑的過大食物遮罩 (來自 YOLO 的 '{food_obj['label']}'), 其遮罩佔據了畫面的 {mask_pixels / image_area_pixels:.2%}。")
                    continue
                # --- 結束遮罩過濾器 ---

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
                weight, confidence, error_range = weight_service.calculate_volume_and_weight(
                    mask, 
                    food_name, 
                    pixel_to_cm_ratio=pixel_to_cm_ratio, # 傳入全域比例
                    depth_map=depth_map, # 傳入深度圖
                    image_area_pixels=image_area_pixels # 傳入總像素供後備方案使用
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

        # --- 新增智慧後備機制 (Tier 2) ---
        if not detected_foods:
            logger.info("主要重量估算流程未偵測到有效食物，啟用後備食物辨識模型 (Tier 2)。")
            try:
                # 使用另一個 AI 服務來辨識整張圖片
                fallback_food_name = classify_food_image(image_bytes)
                
                if fallback_food_name and fallback_food_name.lower() not in ['unknown', 'other']:
                    logger.info(f"後備模型辨識出食物為: {fallback_food_name}")
                    # 回傳一個特殊結構，讓前端知道要進入「輔助模式」
                    note = f"AI 重量估算失敗，但圖片辨識模型認為食物可能是「{fallback_food_name}」。請參考並手動輸入重量。"
                    result = {
                        "detected_foods": [],
                        "total_estimated_weight": 0,
                        "total_nutrition": {},
                        "reference_object": None,
                        "note": note,
                        "fallback_food_suggestion": { "food_name": fallback_food_name }
                    }
                    if debug: result["debug_output_path"] = debug_dir
                    return result

            except Exception as fallback_e:
                logger.error(f"後備食物辨識模型失敗: {fallback_e}")
                # 如果後備模型也失敗，就繼續執行到最後，回傳完全空的結果，觸發前端的「完全手動模式」

        # 5. 生成備註 (Tier 1 成功時)
        if detected_foods:
            if pixel_to_cm_ratio and reference_object_label:
                note = f"已使用 '{reference_object_label}' 作為參考物，成功分析 {len(detected_foods)} 項食物，準確度較高。"
            elif all_ref_candidates:
                too_small_ref_labels = list(set([o['label'] for o in all_ref_candidates]))
                note = f"警告：雖偵測到 {too_small_ref_labels}，但其佔比過小無法作為精準參考。結果為AI基於畫面比例估算，僅供參考。"
            else:
                note = f"未能找到可靠參考物。結果為AI基於畫面比例估算，僅供參考。"
        else:
            # Tier 3: 所有 AI 流程都失敗
            note = "分析失敗：AI 無法辨識出任何可信的食物項目。請嘗試手動搜尋。"

        result = {
            "detected_foods": detected_foods,
            "total_estimated_weight": round(sum(item['estimated_weight'] for item in detected_foods), 1),
            "total_nutrition": {k: round(v, 1) for k, v in total_nutrition.items()},
            "reference_object": reference_object_label,
            "note": note
        }
        if debug:
            from PIL import ImageDraw
            overlay_img = image.copy()
            overlay_array = np.array(overlay_img)
            all_food_boxes = [[obj['bbox']] for obj in food_objects]  # 修正邊界框格式
            if all_food_boxes:
                all_masks = weight_service.segment_food(image, input_boxes=all_food_boxes)
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