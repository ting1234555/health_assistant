#!/usr/bin/env python3
"""
AI 模型測試腳本
診斷 YOLOv5n、SAM、DPT 模型的載入和運行狀況
"""

import logging
import sys
import os
from PIL import Image
import numpy as np

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_yolo_model():
    """測試 YOLOv5n 模型"""
    try:
        logger.info("=== 測試 YOLOv5n 模型 ===")
        
        # 測試模型載入
        from ultralytics import YOLO
        logger.info("正在載入 YOLOv5n 模型...")
        model = YOLO('yolov5nu.pt')
        logger.info("✅ YOLOv5n 模型載入成功")
        
        # 測試類別名稱
        class_names = model.names if hasattr(model, 'names') else None
        logger.info(f"模型類別數量: {len(class_names) if class_names else 'Unknown'}")
        
        # 創建測試圖片
        test_image = Image.fromarray(np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8))
        logger.info("創建測試圖片成功")
        
        # 測試推理
        logger.info("正在進行物件偵測...")
        results = model(test_image, conf=0.25)
        
        if results and len(results) > 0:
            result = results[0]
            if result.boxes is not None:
                detected_count = len(result.boxes)
                logger.info(f"✅ 偵測到 {detected_count} 個物件")
                
                for i, box in enumerate(result.boxes):
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    label = class_names[class_id] if class_names else str(class_id)
                    logger.info(f"  物件 {i+1}: {label} (信心度: {conf:.2f})")
            else:
                logger.warning("⚠️ 沒有偵測到任何物件")
        else:
            logger.warning("⚠️ 推理結果為空")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ YOLOv5n 測試失敗: {str(e)}")
        return False

def test_sam_model():
    """測試 SAM 模型"""
    try:
        logger.info("=== 測試 SAM 模型 ===")
        
        # 測試模型載入
        from transformers import SamModel, SamProcessor
        logger.info("正在載入 SAM 模型...")
        model = SamModel.from_pretrained("facebook/sam-vit-base")
        processor = SamProcessor.from_pretrained("facebook/sam-vit-base")
        logger.info("✅ SAM 模型載入成功")
        
        # 創建測試圖片和邊界框
        test_image = Image.fromarray(np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8))
        test_boxes = [[[100, 100, 200, 200]]]  # 修正邊界框格式：需要雙層列表
        
        # 測試推理
        logger.info("正在進行圖像分割...")
        inputs = processor(test_image, input_boxes=test_boxes, return_tensors="pt")
        
        import torch
        with torch.no_grad():
            outputs = model(**inputs)
        
        logger.info("✅ SAM 推理成功")
        return True
        
    except Exception as e:
        logger.error(f"❌ SAM 測試失敗: {str(e)}")
        return False

def test_dpt_model():
    """測試 DPT 模型"""
    try:
        logger.info("=== 測試 DPT 模型 ===")
        
        # 測試模型載入
        from transformers import pipeline
        logger.info("正在載入 DPT 模型...")
        model = pipeline("depth-estimation", model="Intel/dpt-large")
        logger.info("✅ DPT 模型載入成功")
        
        # 創建測試圖片
        test_image = Image.fromarray(np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8))
        
        # 測試推理
        logger.info("正在進行深度估計...")
        result = model(test_image)
        
        if "depth" in result:
            depth_map = np.array(result["depth"])
            logger.info(f"✅ 深度估計成功，深度圖尺寸: {depth_map.shape}")
        else:
            logger.warning("⚠️ 深度估計結果格式異常")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ DPT 測試失敗: {str(e)}")
        return False

def test_weight_estimation_service():
    """測試重量估算服務"""
    try:
        logger.info("=== 測試重量估算服務 ===")
        
        # 導入服務
        from app.services.weight_estimation_service import WeightEstimationService
        
        # 創建服務實例
        logger.info("正在初始化重量估算服務...")
        service = WeightEstimationService()
        logger.info("✅ 重量估算服務初始化成功")
        
        # 創建測試圖片
        test_image = Image.fromarray(np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8))
        
        # 測試物件偵測
        logger.info("正在測試物件偵測...")
        objects = service.detect_objects(test_image)
        logger.info(f"✅ 物件偵測完成，偵測到 {len(objects)} 個物件")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 重量估算服務測試失敗: {str(e)}")
        return False

def main():
    """主測試函數"""
    logger.info("開始 AI 模型診斷測試...")
    
    results = {
        "yolo": test_yolo_model(),
        "sam": test_sam_model(),
        "dpt": test_dpt_model(),
        "weight_service": test_weight_estimation_service()
    }
    
    # 總結結果
    logger.info("=== 測試結果總結 ===")
    success_count = sum(results.values())
    total_count = len(results)
    
    for test_name, success in results.items():
        status = "✅ 通過" if success else "❌ 失敗"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"總體結果: {success_count}/{total_count} 個測試通過")
    
    if success_count == total_count:
        logger.info("🎉 所有測試都通過了！AI 模型運行正常。")
        return 0
    else:
        logger.error("⚠️ 部分測試失敗，請檢查相關模型。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 