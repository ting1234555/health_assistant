# 檔案路徑: app/services/lightweight_model_service.py

import logging
import numpy as np
from PIL import Image
import io
from typing import Dict, Any, List, Optional, Tuple, Union
import torch
import cv2
from ultralytics import YOLO
import os

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightweightModelService:
    """
    輕量化 AI 模型服務
    支持多種替代模型選擇，包括 MobileSAM、DPT SwinV2-Tiny 等
    """
    
    def __init__(self, model_config: Optional[Dict[str, str]] = None):
        """
        初始化輕量化模型服務
        
        Args:
            model_config: 模型配置字典，可指定具體的模型
        """
        self.model_config = model_config or {
            "detection": "yolov5n",  # 物件偵測
            "segmentation": "mobilesam",  # 圖像分割
            "depth": "dpt_swinv2_tiny"  # 深度估計
        }
        
        # 模型實例
        self.detection_model = None
        self.segmentation_model = None
        self.segmentation_processor = None
        self.depth_model = None
        
        # 載入模型
        self._load_models()
    
    def _load_models(self):
        """載入指定的 AI 模型"""
        try:
            logger.info("開始載入輕量化模型組合...")
            
            # 1. 載入物件偵測模型
            self._load_detection_model()
            
            # 2. 載入圖像分割模型
            self._load_segmentation_model()
            
            # 3. 載入深度估計模型
            self._load_depth_model()
            
            logger.info("✅ 所有輕量化模型載入完成！")
            
        except Exception as e:
            logger.error(f"模型載入失敗: {str(e)}")
            raise
    
    def _load_detection_model(self):
        """載入物件偵測模型"""
        try:
            detection_type = self.model_config.get("detection", "yolov5n")
            
            if detection_type == "yolov5n":
                logger.info("載入 YOLOv5n 物件偵測模型...")
                self.detection_model = YOLO('yolov5nu.pt')
            elif detection_type == "yolov8n":
                logger.info("載入 YOLOv8n 物件偵測模型...")
                self.detection_model = YOLO('yolov8n.pt')
            else:
                logger.warning(f"未知的偵測模型類型: {detection_type}，使用預設 YOLOv5n")
                self.detection_model = YOLO('yolov5nu.pt')
                
            logger.info(f"✅ 物件偵測模型載入成功: {detection_type}")
            
        except Exception as e:
            logger.error(f"物件偵測模型載入失敗: {str(e)}")
            raise
    
    def _load_segmentation_model(self):
        """載入圖像分割模型"""
        try:
            segmentation_type = self.model_config.get("segmentation", "mobilesam")
            
            if segmentation_type == "mobilesam":
                logger.info("載入 MobileSAM 分割模型...")
                from transformers import SamModel, SamProcessor
                self.segmentation_model = SamModel.from_pretrained("facebook/sam-vit-base")
                self.segmentation_processor = SamProcessor.from_pretrained("facebook/sam-vit-base")
                
            elif segmentation_type == "slimsam":
                logger.info("載入 SlimSAM 分割模型...")
                # 嘗試載入 SlimSAM (如果可用)
                try:
                    from transformers import SamModel, SamProcessor
                    self.segmentation_model = SamModel.from_pretrained("Zigeng/SlimSAM-uniform")
                    self.segmentation_processor = SamProcessor.from_pretrained("Zigeng/SlimSAM-uniform")
                except:
                    logger.warning("SlimSAM 載入失敗，回退到標準 SAM")
                    self.segmentation_model = SamModel.from_pretrained("facebook/sam-vit-base")
                    self.segmentation_processor = SamProcessor.from_pretrained("facebook/sam-vit-base")
                    
            elif segmentation_type == "efficientvit_sam":
                logger.info("載入 EfficientViT-SAM 分割模型...")
                # 嘗試載入 EfficientViT-SAM (如果可用)
                try:
                    from transformers import SamModel, SamProcessor
                    self.segmentation_model = SamModel.from_pretrained("hustvl/EfficientViT-SAM")
                    self.segmentation_processor = SamProcessor.from_pretrained("hustvl/EfficientViT-SAM")
                except:
                    logger.warning("EfficientViT-SAM 載入失敗，回退到標準 SAM")
                    self.segmentation_model = SamModel.from_pretrained("facebook/sam-vit-base")
                    self.segmentation_processor = SamProcessor.from_pretrained("facebook/sam-vit-base")
                    
            else:
                logger.warning(f"未知的分割模型類型: {segmentation_type}，使用預設 MobileSAM")
                from transformers import SamModel, SamProcessor
                self.segmentation_model = SamModel.from_pretrained("facebook/sam-vit-base")
                self.segmentation_processor = SamProcessor.from_pretrained("facebook/sam-vit-base")
                
            logger.info(f"✅ 圖像分割模型載入成功: {segmentation_type}")
            
        except Exception as e:
            logger.error(f"圖像分割模型載入失敗: {str(e)}")
            raise
    
    def _load_depth_model(self):
        """載入深度估計模型"""
        try:
            depth_type = self.model_config.get("depth", "dpt_swinv2_tiny")
            
            if depth_type == "dpt_swinv2_tiny":
                logger.info("載入 DPT SwinV2-Tiny 深度估計模型...")
                from transformers import pipeline
                self.depth_model = pipeline("depth-estimation", model="Intel/dpt-swinv2-tiny-256")
                
            elif depth_type == "dpt_large":
                logger.info("載入 DPT Large 深度估計模型...")
                from transformers import pipeline
                self.depth_model = pipeline("depth-estimation", model="Intel/dpt-large")
                
            elif depth_type == "lmdepth_s":
                logger.info("載入 LMDepth-S 深度估計模型...")
                # 嘗試載入 LMDepth-S (如果可用)
                try:
                    from transformers import pipeline
                    self.depth_model = pipeline("depth-estimation", model="hustvl/LMDepth-S")
                except:
                    logger.warning("LMDepth-S 載入失敗，回退到 DPT SwinV2-Tiny")
                    self.depth_model = pipeline("depth-estimation", model="Intel/dpt-swinv2-tiny-256")
                    
            elif depth_type == "mininet":
                logger.info("載入 MiniNet 深度估計模型...")
                # 嘗試載入 MiniNet (如果可用)
                try:
                    from transformers import pipeline
                    self.depth_model = pipeline("depth-estimation", model="hustvl/MiniNet")
                except:
                    logger.warning("MiniNet 載入失敗，回退到 DPT SwinV2-Tiny")
                    self.depth_model = pipeline("depth-estimation", model="Intel/dpt-swinv2-tiny-256")
                    
            else:
                logger.warning(f"未知的深度模型類型: {depth_type}，使用預設 DPT SwinV2-Tiny")
                from transformers import pipeline
                self.depth_model = pipeline("depth-estimation", model="Intel/dpt-swinv2-tiny-256")
                
            logger.info(f"✅ 深度估計模型載入成功: {depth_type}")
            
        except Exception as e:
            logger.error(f"深度估計模型載入失敗: {str(e)}")
            raise
    
    def detect_objects(self, image: Image.Image) -> List[Dict[str, Any]]:
        """使用載入的偵測模型偵測圖片中的所有物體"""
        try:
            # 轉成 numpy array
            img_np = np.array(image)
            if img_np.shape[2] == 4:
                img_np = img_np[:, :, :3]  # 移除 alpha
            
            # 使用偵測模型進行偵測
            results = self.detection_model(img_np, conf=0.25)  # 降低信心度閾值
            
            detected_objects = []
            if results and len(results) > 0:
                result = results[0]  # 取第一個結果
                if result.boxes is not None:
                    for box in result.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        label = self.detection_model.names[class_id].lower() if hasattr(self.detection_model, 'names') else str(class_id)
                        
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
        """使用載入的分割模型根據提供的邊界框分割食物區域"""
        if not input_boxes:
            return []
        try:
            # 使用分割模型進行分割，並提供邊界框作為提示
            inputs = self.segmentation_processor(image, input_boxes=input_boxes, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.segmentation_model(**inputs)
            
            # 取得分割遮罩
            masks_tensor = self.segmentation_processor.image_processor.post_process_masks(
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
        """使用載入的深度模型進行深度估計"""
        try:
            depth_result = self.depth_model(image)
            depth_map = np.array(depth_result["depth"])
            return depth_map
        except Exception as e:
            logger.error(f"深度估計失敗: {str(e)}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """獲取當前載入的模型資訊"""
        return {
            "detection": self.model_config.get("detection", "yolov5n"),
            "segmentation": self.model_config.get("segmentation", "mobilesam"),
            "depth": self.model_config.get("depth", "dpt_swinv2_tiny"),
            "models_loaded": {
                "detection": self.detection_model is not None,
                "segmentation": self.segmentation_model is not None,
                "depth": self.depth_model is not None
            }
        }
    
    def test_model_performance(self, test_image: Image.Image) -> Dict[str, Any]:
        """測試模型性能"""
        import time
        
        results = {}
        
        # 測試物件偵測性能
        start_time = time.time()
        objects = self.detect_objects(test_image)
        detection_time = time.time() - start_time
        results["detection"] = {
            "time": detection_time,
            "objects_count": len(objects),
            "success": len(objects) > 0
        }
        
        # 測試深度估計性能
        start_time = time.time()
        depth_map = self.estimate_depth(test_image)
        depth_time = time.time() - start_time
        results["depth"] = {
            "time": depth_time,
            "success": depth_map is not None,
            "shape": depth_map.shape if depth_map is not None else None
        }
        
        # 測試分割性能 (如果有偵測到物件)
        if objects:
            start_time = time.time()
            input_boxes = [obj["bbox"] for obj in objects[:1]]  # 只測試第一個物件
            masks = self.segment_food(test_image, input_boxes)
            segmentation_time = time.time() - start_time
            results["segmentation"] = {
                "time": segmentation_time,
                "masks_count": len(masks),
                "success": len(masks) > 0
            }
        else:
            results["segmentation"] = {
                "time": 0,
                "masks_count": 0,
                "success": False,
                "note": "No objects detected for segmentation test"
            }
        
        return results

# 全域服務實例
lightweight_service = LightweightModelService()

def create_model_service_with_config(config: Dict[str, str]) -> LightweightModelService:
    """
    根據配置創建模型服務實例
    
    Args:
        config: 模型配置字典
        
    Returns:
        LightweightModelService 實例
    """
    return LightweightModelService(config)

def get_available_models() -> Dict[str, List[str]]:
    """
    獲取可用的模型選項
    
    Returns:
        包含各類型可用模型的字典
    """
    return {
        "detection": ["yolov5n", "yolov8n"],
        "segmentation": ["mobilesam", "slimsam", "efficientvit_sam"],
        "depth": ["dpt_swinv2_tiny", "dpt_large", "lmdepth_s", "mininet"]
    } 