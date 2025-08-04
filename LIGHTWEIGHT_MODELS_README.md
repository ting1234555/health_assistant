# 輕量化 AI 模型服務

## 概述

本項目提供了一個可配置的輕量化 AI 模型服務，支持多種替代模型選擇，以解決 TinySAM 和 MiDaS_small 無法下載的問題。該服務提供了靈活的模型配置選項，可以根據不同的需求（速度、準確度、記憶體使用）選擇最適合的模型組合。

## 主要特性

### 🚀 多模型支持
- **物件偵測**: YOLOv5n, YOLOv8n
- **圖像分割**: MobileSAM, SlimSAM, EfficientViT-SAM
- **深度估計**: DPT SwinV2-Tiny, DPT Large, LMDepth-S, MiniNet

### ⚡ 智能回退機制
- 當指定模型無法載入時，自動回退到可用的替代模型
- 確保服務的穩定性和可用性

### 🎯 預設配置方案
- **平衡配置**: 速度與準確度的最佳平衡
- **速度優化**: 極致輕量化，適合資源受限環境
- **準確度優化**: 更高準確度，但需要更多資源

### 📊 性能監控
- 模型載入時間測試
- 推理速度測試
- 記憶體使用監控
- 模型比較功能

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 運行測試

```bash
# 測試輕量化模型服務
python test_lightweight_models.py

# 測試原始模型服務
python test_models.py
```

### 3. 啟動服務

```bash
uvicorn app.main:app --reload
```

## API 端點

### V2 API (推薦使用)

#### 1. 食物分析 (可配置模型)
```
POST /ai/v2/analyze-food
```

**參數:**
- `image`: 圖片文件
- `model_config` (可選): JSON 字符串格式的模型配置
- `debug` (可選): 是否啟用調試模式

**示例:**
```bash
curl -X POST "http://localhost:8000/ai/v2/analyze-food" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@food.jpg" \
  -F "model_config={\"detection\": \"yolov5n\", \"segmentation\": \"mobilesam\", \"depth\": \"dpt_swinv2_tiny\"}" \
  -F "debug=false"
```

#### 2. 獲取可用模型
```
GET /ai/v2/available-models
```

**返回:**
```json
{
  "available_models": {
    "detection": ["yolov5n", "yolov8n"],
    "segmentation": ["mobilesam", "slimsam", "efficientvit_sam"],
    "depth": ["dpt_swinv2_tiny", "dpt_large", "lmdepth_s", "mininet"]
  },
  "descriptions": {
    "detection": {
      "yolov5n": "YOLOv5 Nano - 輕量級物件偵測模型，速度快，適合即時應用"
    }
  },
  "recommended_configs": {
    "balanced": {
      "detection": "yolov5n",
      "segmentation": "mobilesam",
      "depth": "dpt_swinv2_tiny",
      "description": "平衡配置 - 速度與準確度的最佳平衡"
    }
  }
}
```

#### 3. 測試模型配置
```
POST /ai/v2/test-model-config
```

**參數:**
- `model_config`: JSON 字符串格式的模型配置

#### 4. 獲取當前模型資訊
```
GET /ai/v2/model-info
```

#### 5. 比較模型性能
```
POST /ai/v2/compare-models
```

**參數:**
- `image`: 圖片文件
- `configs`: JSON 數組格式的模型配置列表

## 模型配置示例

### 平衡配置 (推薦)
```json
{
  "detection": "yolov5n",
  "segmentation": "mobilesam",
  "depth": "dpt_swinv2_tiny"
}
```

### 速度優化配置
```json
{
  "detection": "yolov5n",
  "segmentation": "slimsam",
  "depth": "mininet"
}
```

### 準確度優化配置
```json
{
  "detection": "yolov8n",
  "segmentation": "efficientvit_sam",
  "depth": "dpt_large"
}
```

## 模型詳細說明

### 物件偵測模型

#### YOLOv5n
- **大小**: ~3.9MB
- **速度**: 非常快
- **準確度**: 中等
- **適用場景**: 即時應用，資源受限環境

#### YOLOv8n
- **大小**: ~6.2MB
- **速度**: 快
- **準確度**: 高
- **適用場景**: 需要更高準確度的應用

### 圖像分割模型

#### MobileSAM
- **大小**: ~60MB
- **速度**: 中等
- **準確度**: 高
- **特點**: 最接近原始 SAM 的輕量模型

#### SlimSAM
- **大小**: ~2MB
- **速度**: 非常快
- **準確度**: 中等
- **特點**: 僅 1.4% 原始參數，極致輕量化

#### EfficientViT-SAM
- **大小**: ~15MB
- **速度**: 快
- **準確度**: 高
- **特點**: 推理速度提升近 50 倍

### 深度估計模型

#### DPT SwinV2-Tiny
- **大小**: ~25MB
- **速度**: 中等
- **準確度**: 高
- **特點**: 支援 256×256 推理

#### DPT Large
- **大小**: ~150MB
- **速度**: 慢
- **準確度**: 非常高
- **特點**: 標準版本，準確度最高

#### LMDepth-S
- **大小**: ~8MB
- **速度**: 快
- **準確度**: 高
- **特點**: 使用 Mamba 架構，低 FLOPs

#### MiniNet
- **大小**: ~1MB
- **速度**: 非常快
- **準確度**: 中等
- **特點**: 僅 0.217M 參數，CPU 上可達 37 FPS

## 使用建議

### 根據環境選擇配置

#### 開發環境 (16GB RAM)
```json
{
  "detection": "yolov5n",
  "segmentation": "mobilesam",
  "depth": "dpt_swinv2_tiny"
}
```

#### 生產環境 (8GB RAM)
```json
{
  "detection": "yolov5n",
  "segmentation": "slimsam",
  "depth": "mininet"
}
```

#### 高精度需求
```json
{
  "detection": "yolov8n",
  "segmentation": "efficientvit_sam",
  "depth": "dpt_large"
}
```

### 性能優化建議

1. **首次載入**: 模型首次載入需要時間，建議在服務啟動時預載入
2. **記憶體管理**: 定期監控記憶體使用，必要時重啟服務
3. **快取機制**: 考慮實現模型結果快取以提高響應速度
4. **並發處理**: 根據服務器性能調整並發請求數量

## 故障排除

### 常見問題

#### 1. 模型載入失敗
**症狀**: 出現 "模型載入失敗" 錯誤
**解決方案**: 
- 檢查網絡連接
- 確認 Hugging Face 模型可用性
- 使用回退模型配置

#### 2. 記憶體不足
**症狀**: 出現 OOM (Out of Memory) 錯誤
**解決方案**:
- 使用更輕量的模型配置
- 增加系統記憶體
- 降低圖片解析度

#### 3. 推理速度慢
**症狀**: 響應時間過長
**解決方案**:
- 使用速度優化配置
- 檢查 GPU 可用性
- 優化圖片大小

### 調試模式

啟用調試模式可以獲得詳細的處理信息：

```bash
curl -X POST "http://localhost:8000/ai/v2/analyze-food" \
  -F "image=@food.jpg" \
  -F "debug=true"
```

調試模式會生成以下文件：
- `00_original.jpg`: 原始圖片
- `01_detected_objects.jpg`: 物件偵測結果
- `02_final_segmentation.jpg`: 最終分割結果
- `03_depth_map.png`: 深度圖

## 版本歷史

### V2.0 (當前版本)
- 新增可配置模型選擇
- 支持多種替代模型
- 智能回退機制
- 性能監控功能
- 模型比較功能

### V1.0
- 基礎重量估算功能
- 固定模型配置
- 基本 API 端點

## 貢獻指南

1. Fork 本項目
2. 創建功能分支
3. 提交更改
4. 發起 Pull Request

## 授權

本項目採用 MIT 授權條款。

## 聯繫方式

如有問題或建議，請提交 Issue 或聯繫開發團隊。 