# 檔案路徑: app/routers/ai_router_v2.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, Optional
import io
from PIL import Image
import numpy as np

from ..services.weight_estimation_service_v2 import estimate_food_weight_v2, WeightEstimationServiceV2
from ..services.lightweight_model_service import get_available_models, create_model_service_with_config

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/v2", tags=["AI Analysis V2"])

@router.post("/analyze-food")
async def analyze_food_v2(
    image: UploadFile = File(...),
    model_config: Optional[str] = Form(default=None),  # JSON 字符串格式的模型配置
    debug: bool = Form(default=False)
) -> Dict[str, Any]:
    """
    使用可配置的輕量化模型進行食物分析 V2
    
    Args:
        image: 上傳的圖片文件
        model_config: 可選的模型配置 JSON 字符串，例如：
            '{"detection": "yolov5n", "segmentation": "mobilesam", "depth": "dpt_swinv2_tiny"}'
        debug: 是否啟用調試模式
    
    Returns:
        包含食物分析結果的字典
    """
    try:
        # 驗證圖片格式
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="只支持圖片文件")
        
        # 讀取圖片
        image_bytes = await image.read()
        
        # 解析模型配置
        parsed_config = None
        if model_config:
            try:
                import json
                parsed_config = json.loads(model_config)
                logger.info(f"使用自定義模型配置: {parsed_config}")
            except json.JSONDecodeError:
                logger.warning(f"模型配置 JSON 解析失敗: {model_config}，使用預設配置")
        
        # 進行食物分析
        result = await estimate_food_weight_v2(
            image_bytes=image_bytes,
            model_config=parsed_config,
            debug=debug
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"食物分析失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失敗: {str(e)}")

@router.get("/available-models")
async def get_models() -> Dict[str, Any]:
    """
    獲取可用的模型選項
    
    Returns:
        包含各類型可用模型的字典
    """
    try:
        available_models = get_available_models()
        
        # 添加模型描述
        model_descriptions = {
            "detection": {
                "yolov5n": "YOLOv5 Nano - 輕量級物件偵測模型，速度快，適合即時應用",
                "yolov8n": "YOLOv8 Nano - 最新版本的輕量級物件偵測模型，準確度更高"
            },
            "segmentation": {
                "mobilesam": "MobileSAM - 輕量級圖像分割模型，基於 SAM 架構",
                "slimsam": "SlimSAM - 極致輕量化分割模型，僅 1.4% 原始參數",
                "efficientvit_sam": "EfficientViT-SAM - 高效能分割模型，推理速度提升 50 倍"
            },
            "depth": {
                "dpt_swinv2_tiny": "DPT SwinV2-Tiny - 輕量級深度估計模型，支援 256×256 推理",
                "dpt_large": "DPT Large - 標準深度估計模型，準確度較高",
                "lmdepth_s": "LMDepth-S - 最新輕量化深度模型，使用 Mamba 架構",
                "mininet": "MiniNet - 極致輕量深度模型，僅 0.217M 參數"
            }
        }
        
        result = {
            "available_models": available_models,
            "descriptions": model_descriptions,
            "recommended_configs": {
                "balanced": {
                    "detection": "yolov5n",
                    "segmentation": "mobilesam", 
                    "depth": "dpt_swinv2_tiny",
                    "description": "平衡配置 - 速度與準確度的最佳平衡"
                },
                "speed_optimized": {
                    "detection": "yolov5n",
                    "segmentation": "slimsam",
                    "depth": "mininet",
                    "description": "速度優化 - 極致輕量化，適合資源受限環境"
                },
                "accuracy_optimized": {
                    "detection": "yolov8n",
                    "segmentation": "efficientvit_sam",
                    "depth": "dpt_large",
                    "description": "準確度優化 - 更高準確度，但需要更多資源"
                }
            }
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"獲取可用模型失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取模型列表失敗: {str(e)}")

@router.post("/test-model-config")
async def test_model_config(
    model_config: str = Form(...)  # JSON 字符串格式的模型配置
) -> Dict[str, Any]:
    """
    測試指定的模型配置
    
    Args:
        model_config: 模型配置 JSON 字符串
    
    Returns:
        測試結果
    """
    try:
        import json
        parsed_config = json.loads(model_config)
        
        # 創建測試圖片
        test_image = Image.fromarray(np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8))
        
        # 創建服務並測試
        service = WeightEstimationServiceV2(parsed_config)
        model_info = service.get_model_info()
        performance = service.test_model_performance(test_image)
        
        result = {
            "model_config": parsed_config,
            "model_info": model_info,
            "performance_test": performance,
            "status": "success"
        }
        
        return JSONResponse(content=result)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="模型配置 JSON 格式錯誤")
    except Exception as e:
        logger.error(f"模型配置測試失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"測試失敗: {str(e)}")

@router.get("/model-info")
async def get_current_model_info() -> Dict[str, Any]:
    """
    獲取當前使用的模型資訊
    
    Returns:
        當前模型資訊
    """
    try:
        service = WeightEstimationServiceV2()
        model_info = service.get_model_info()
        
        result = {
            "current_config": model_info,
            "timestamp": "2024-01-01T00:00:00Z"  # 可以添加實際時間戳
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"獲取模型資訊失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取模型資訊失敗: {str(e)}")

@router.post("/compare-models")
async def compare_models(
    image: UploadFile = File(...),
    configs: str = Form(...)  # JSON 數組格式的模型配置列表
) -> Dict[str, Any]:
    """
    比較不同模型配置的性能
    
    Args:
        image: 上傳的圖片文件
        configs: 模型配置列表的 JSON 字符串，例如：
            '[{"detection": "yolov5n", "segmentation": "mobilesam", "depth": "dpt_swinv2_tiny"}, 
              {"detection": "yolov8n", "segmentation": "slimsam", "depth": "mininet"}]'
    
    Returns:
        比較結果
    """
    try:
        import json
        import time
        
        # 驗證圖片格式
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="只支持圖片文件")
        
        # 讀取圖片
        image_bytes = await image.read()
        image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # 解析配置列表
        parsed_configs = json.loads(configs)
        if not isinstance(parsed_configs, list):
            raise HTTPException(status_code=400, detail="配置必須是數組格式")
        
        comparison_results = []
        
        for i, config in enumerate(parsed_configs):
            try:
                start_time = time.time()
                
                # 創建服務
                service = WeightEstimationServiceV2(config)
                
                # 測試性能
                performance = service.test_model_performance(image_pil)
                
                # 進行食物分析
                result = await estimate_food_weight_v2(
                    image_bytes=image_bytes,
                    model_config=config,
                    debug=False
                )
                
                end_time = time.time()
                total_time = end_time - start_time
                
                comparison_results.append({
                    "config_index": i,
                    "config": config,
                    "performance": performance,
                    "analysis_result": {
                        "detected_foods_count": len(result.get("detected_foods", [])),
                        "total_weight": result.get("total_estimated_weight", 0),
                        "has_reference_object": result.get("reference_object") is not None
                    },
                    "total_time": total_time,
                    "status": "success"
                })
                
            except Exception as e:
                comparison_results.append({
                    "config_index": i,
                    "config": config,
                    "error": str(e),
                    "status": "failed"
                })
        
        return JSONResponse(content={
            "comparison_results": comparison_results,
            "summary": {
                "total_configs": len(parsed_configs),
                "successful_configs": len([r for r in comparison_results if r["status"] == "success"]),
                "failed_configs": len([r for r in comparison_results if r["status"] == "failed"])
            }
        })
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="配置 JSON 格式錯誤")
    except Exception as e:
        logger.error(f"模型比較失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"比較失敗: {str(e)}") 