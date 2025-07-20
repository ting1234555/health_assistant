# 檔案路徑: backend/app/services/ai_service.py

from transformers.pipelines import pipeline
from PIL import Image
import io
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局變量
image_classifier = None

def load_model():
    """載入模型的函數"""
    global image_classifier
    
    try:
        logger.info("正在載入食物辨識模型...")
        # 載入模型 - 移除不支持的參數
        image_classifier = pipeline(
            "image-classification", 
            model="juliensimon/autotrain-food101-1471154053",
            device=-1,  # 使用CPU
            cache_dir="/tmp/huggingface"
        )
        logger.info("模型載入成功！")
        return True
    except Exception as e:
        logger.error(f"模型載入失敗: {str(e)}")
        image_classifier = None
        return False

def classify_food_image(image_bytes: bytes) -> str:
    """
    接收圖片的二進位制數據，進行分類並返回可能性最高的食物名稱。
    """
    global image_classifier
    
    # 如果模型未載入，嘗試重新載入
    if image_classifier is None:
        logger.warning("模型未載入，嘗試重新載入...")
        if not load_model():
            return "Error: Model not loaded"
    
    if image_classifier is None:
        return "Error: Model could not be loaded"

    try:
        # 驗證圖片數據
        if not image_bytes:
            return "Error: Empty image data"
        
        # 從記憶體中的 bytes 打開圖片
        image = Image.open(io.BytesIO(image_bytes))
        
        # 確保圖片是RGB格式
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        logger.info(f"處理圖片，尺寸: {image.size}")
        
        # 使用模型管線進行分類
        pipeline_output = image_classifier(image)
        
        logger.info(f"模型輸出: {pipeline_output}")
        
        # 處理輸出結果
        if not pipeline_output:
            return "Unknown"
        
        # pipeline_output 通常是一個列表
        if isinstance(pipeline_output, list) and len(pipeline_output) > 0:
            result = pipeline_output[0]
            if isinstance(result, dict) and 'label' in result:
                label = result['label']
                confidence = result.get('score', 0)
                
                logger.info(f"辨識結果: {label}, 信心度: {confidence:.2f}")
                
            # 標籤可能包含底線，我們將其替換為空格，並讓首字母大寫
                formatted_label = str(label).replace('_', ' ').title()
                return formatted_label
            
        return "Unknown"
        
    except Exception as e:
        logger.error(f"圖片分類過程中發生錯誤: {str(e)}")
        return f"Error: {str(e)}"

# 在模塊載入時嘗試載入模型
logger.info("初始化 AI 服務...")
load_model()

__all__ = ["classify_food_image"]