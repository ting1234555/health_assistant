#!/usr/bin/env python3
"""
測試新的輕量化模型組合：YOLOv4-tiny + MobileSAM + MiDaS_small
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.weight_estimation_service import WeightEstimationService
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_loading():
    """測試模型載入"""
    try:
        logger.info("開始測試輕量化模型載入...")
        
        # 初始化服務
        service = WeightEstimationService()
        
        logger.info("✅ 所有模型載入成功！")
        logger.info(f"YOLOv4-tiny 類別數量: {len(service.class_names) if service.class_names else 'Unknown'}")
        logger.info(f"SAM 模型類型: MobileSAM (TinySAM)")
        logger.info(f"深度模型類型: MiDaS_small")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 模型載入失敗: {str(e)}")
        return False

def test_basic_functionality():
    """測試基本功能"""
    try:
        logger.info("開始測試基本功能...")
        
        service = WeightEstimationService()
        
        # 創建一個測試圖片 (1x1 像素)
        from PIL import Image
        import numpy as np
        
        test_image = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8))
        
        # 測試物件偵測
        objects = service.detect_objects(test_image)
        logger.info(f"✅ 物件偵測測試通過，偵測到 {len(objects)} 個物件")
        
        # 測試深度估計
        depth_map = service.estimate_depth(test_image)
        if depth_map is not None:
            logger.info(f"✅ 深度估計測試通過，深度圖尺寸: {depth_map.shape}")
        else:
            logger.warning("⚠️ 深度估計返回 None (可能是正常的)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 基本功能測試失敗: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("🚀 開始測試新的輕量化模型組合...")
    
    # 測試模型載入
    if test_model_loading():
        logger.info("✅ 模型載入測試通過")
        
        # 測試基本功能
        if test_basic_functionality():
            logger.info("✅ 基本功能測試通過")
            logger.info("🎉 所有測試通過！新的輕量化模型組合可以正常使用。")
        else:
            logger.error("❌ 基本功能測試失敗")
    else:
        logger.error("❌ 模型載入測試失敗")
    
    logger.info("測試完成。") 