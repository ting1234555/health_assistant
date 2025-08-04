#!/usr/bin/env python3
"""
使用真實食物圖片測試 AI 模型
"""

import logging
import sys
import os
from PIL import Image
import numpy as np
import requests
from io import BytesIO

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_food_image():
    """創建一個模擬食物圖片"""
    # 創建一個 640x640 的圖片
    img = Image.new('RGB', (640, 640), color='white')
    
    # 添加一些簡單的幾何形狀來模擬食物
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # 模擬盤子（圓形）
    draw.ellipse([100, 100, 300, 300], fill='lightgray', outline='gray', width=3)
    
    # 模擬食物（橢圓形）
    draw.ellipse([150, 150, 250, 250], fill='brown', outline='darkred', width=2)
    
    # 模擬餐具
    draw.rectangle([400, 200, 450, 400], fill='silver', outline='gray', width=2)
    
    return img

def test_with_food_image():
    """使用食物圖片測試 AI 模型"""
    try:
        logger.info("=== 使用食物圖片測試 AI 模型 ===")
        
        # 創建測試圖片
        test_image = create_test_food_image()
        logger.info("創建測試食物圖片成功")
        
        # 測試 YOLOv5n
        from ultralytics import YOLO
        logger.info("正在載入 YOLOv5n 模型...")
        model = YOLO('yolov5nu.pt')
        
        # 進行物件偵測
        logger.info("正在進行物件偵測...")
        results = model(test_image, conf=0.25)
        
        detected_objects = []
        if results and len(results) > 0:
            result = results[0]
            if result.boxes is not None:
                class_names = model.names
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    label = class_names[class_id].lower() if class_names else str(class_id)
                    
                    detected_objects.append({
                        "label": label,
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "confidence": conf
                    })
        
        logger.info(f"偵測到 {len(detected_objects)} 個物件:")
        for obj in detected_objects:
            logger.info(f"  - {obj['label']} (信心度: {obj['confidence']:.2f})")
        
        # 測試重量估算服務
        from app.services.weight_estimation_service import WeightEstimationService
        logger.info("正在測試重量估算服務...")
        service = WeightEstimationService()
        
        # 轉換圖片為 bytes
        img_bytes = BytesIO()
        test_image.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        # 測試完整的重量估算流程
        from app.services.weight_estimation_service import estimate_food_weight
        import asyncio
        
        logger.info("正在進行完整的食物分析...")
        result = asyncio.run(estimate_food_weight(img_bytes, debug=True))
        
        logger.info("分析結果:")
        logger.info(f"  偵測到的食物數量: {len(result.get('detected_foods', []))}")
        logger.info(f"  總估算重量: {result.get('total_estimated_weight', 0):.1f}g")
        logger.info(f"  備註: {result.get('note', '無')}")
        
        if result.get('detected_foods'):
            for i, food in enumerate(result['detected_foods']):
                logger.info(f"  食物 {i+1}: {food.get('food_name', 'Unknown')} - {food.get('estimated_weight', 0):.1f}g")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    logger.info("開始使用真實食物圖片測試...")
    
    success = test_with_food_image()
    
    if success:
        logger.info("🎉 測試完成！")
        return 0
    else:
        logger.error("⚠️ 測試失敗！")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 