#!/usr/bin/env python3
"""
測試輕量化模型服務的各種替代方案
包括 MobileSAM、DPT SwinV2-Tiny、LMDepth-S 等
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.lightweight_model_service import (
    LightweightModelService, 
    create_model_service_with_config, 
    get_available_models
)
import logging
from PIL import Image
import numpy as np

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_default_configuration():
    """測試預設配置"""
    logger.info("🧪 測試預設配置...")
    try:
        service = LightweightModelService()
        model_info = service.get_model_info()
        logger.info(f"✅ 預設配置載入成功: {model_info}")
        return True
    except Exception as e:
        logger.error(f"❌ 預設配置測試失敗: {str(e)}")
        return False

def test_alternative_segmentation_models():
    """測試替代分割模型"""
    logger.info("🧪 測試替代分割模型...")
    
    segmentation_models = ["mobilesam", "slimsam", "efficientvit_sam"]
    
    for model_type in segmentation_models:
        logger.info(f"測試分割模型: {model_type}")
        try:
            config = {
                "detection": "yolov5n",
                "segmentation": model_type,
                "depth": "dpt_swinv2_tiny"
            }
            service = create_model_service_with_config(config)
            model_info = service.get_model_info()
            logger.info(f"✅ {model_type} 載入成功: {model_info}")
        except Exception as e:
            logger.error(f"❌ {model_type} 載入失敗: {str(e)}")

def test_alternative_depth_models():
    """測試替代深度模型"""
    logger.info("🧪 測試替代深度模型...")
    
    depth_models = ["dpt_swinv2_tiny", "dpt_large", "lmdepth_s", "mininet"]
    
    for model_type in depth_models:
        logger.info(f"測試深度模型: {model_type}")
        try:
            config = {
                "detection": "yolov5n",
                "segmentation": "mobilesam",
                "depth": model_type
            }
            service = create_model_service_with_config(config)
            model_info = service.get_model_info()
            logger.info(f"✅ {model_type} 載入成功: {model_info}")
        except Exception as e:
            logger.error(f"❌ {model_type} 載入失敗: {str(e)}")

def test_model_performance():
    """測試模型性能"""
    logger.info("🧪 測試模型性能...")
    
    try:
        # 創建測試圖片
        test_image = Image.fromarray(np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8))
        
        # 測試預設配置
        service = LightweightModelService()
        performance = service.test_model_performance(test_image)
        
        logger.info("性能測試結果:")
        for model_type, result in performance.items():
            logger.info(f"  {model_type}: {result}")
        
        return True
    except Exception as e:
        logger.error(f"❌ 性能測試失敗: {str(e)}")
        return False

def test_fallback_mechanism():
    """測試回退機制"""
    logger.info("🧪 測試回退機制...")
    
    # 測試不存在的模型，應該會回退到預設模型
    try:
        config = {
            "detection": "yolov5n",
            "segmentation": "nonexistent_model",
            "depth": "nonexistent_depth_model"
        }
        service = create_model_service_with_config(config)
        model_info = service.get_model_info()
        logger.info(f"✅ 回退機制測試成功: {model_info}")
        return True
    except Exception as e:
        logger.error(f"❌ 回退機制測試失敗: {str(e)}")
        return False

def test_available_models():
    """測試獲取可用模型列表"""
    logger.info("🧪 測試獲取可用模型列表...")
    
    try:
        available_models = get_available_models()
        logger.info("可用模型列表:")
        for model_type, models in available_models.items():
            logger.info(f"  {model_type}: {models}")
        return True
    except Exception as e:
        logger.error(f"❌ 獲取可用模型列表失敗: {str(e)}")
        return False

def test_memory_usage():
    """測試記憶體使用情況"""
    logger.info("🧪 測試記憶體使用情況...")
    
    try:
        import psutil
        import gc
        
        # 獲取初始記憶體使用
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 創建服務
        service = LightweightModelService()
        
        # 獲取載入後記憶體使用
        gc.collect()  # 強制垃圾回收
        loaded_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_increase = loaded_memory - initial_memory
        
        logger.info(f"記憶體使用情況:")
        logger.info(f"  初始記憶體: {initial_memory:.2f} MB")
        logger.info(f"  載入後記憶體: {loaded_memory:.2f} MB")
        logger.info(f"  記憶體增加: {memory_increase:.2f} MB")
        
        # 檢查是否在合理範圍內 (應該小於 4GB)
        if memory_increase < 4096:
            logger.info("✅ 記憶體使用在合理範圍內")
            return True
        else:
            logger.warning(f"⚠️ 記憶體使用較高: {memory_increase:.2f} MB")
            return False
            
    except ImportError:
        logger.warning("⚠️ psutil 未安裝，跳過記憶體測試")
        return True
    except Exception as e:
        logger.error(f"❌ 記憶體測試失敗: {str(e)}")
        return False

def main():
    """主測試函數"""
    logger.info("🚀 開始測試輕量化模型服務...")
    
    test_results = []
    
    # 1. 測試預設配置
    test_results.append(("預設配置", test_default_configuration()))
    
    # 2. 測試替代分割模型
    test_alternative_segmentation_models()
    
    # 3. 測試替代深度模型
    test_alternative_depth_models()
    
    # 4. 測試模型性能
    test_results.append(("模型性能", test_model_performance()))
    
    # 5. 測試回退機制
    test_results.append(("回退機制", test_fallback_mechanism()))
    
    # 6. 測試可用模型列表
    test_results.append(("可用模型列表", test_available_models()))
    
    # 7. 測試記憶體使用
    test_results.append(("記憶體使用", test_memory_usage()))
    
    # 總結測試結果
    logger.info("\n📊 測試結果總結:")
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        logger.info(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 總體結果: {passed}/{total} 項測試通過")
    
    if passed == total:
        logger.info("🎉 所有測試通過！輕量化模型服務可以正常使用。")
    else:
        logger.warning("⚠️ 部分測試失敗，請檢查相關配置。")
    
    logger.info("測試完成。")

if __name__ == "__main__":
    main() 