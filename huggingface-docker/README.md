# Health Assistant AI - Docker Space

智能食物分析與營養追蹤系統，部署在 Hugging Face Docker Space。

## 🚀 系統特色

### 三層遞進式 AI 分析
1. **第一層**：YOLOv5n + SAM + DPT（重量估算）
2. **第二層**：Food101 模型（食物識別）
3. **第三層**：手動查詢（用戶備援）

### 技術架構
- **後端**：Python FastAPI + Gradio
- **AI 模型**：YOLOv5n, SAM, DPT, Food101
- **資料庫**：USDA FoodData Central API
- **部署**：Hugging Face Docker Space

### 準確度
- Food101 模型信心度：95%+
- 重量估算誤差：±15%
- 營養資料來源：USDA 官方資料庫

## 🏗️ 部署架構

### Docker 配置
- **基礎鏡像**：Python 3.11-slim
- **端口**：7860
- **健康檢查**：自動監控服務狀態

### 服務端點
- `/` - Gradio 界面
- `/health` - 健康檢查
- `/ai/analyze-food-image/` - AI 食物分析
- `/api/nutrition/lookup` - 營養查詢

## 📊 功能模組

### 🤖 AI 食物分析
- 上傳食物圖片
- 自動偵測食物物件
- 分割食物區域
- 估算重量
- 提供營養資訊

### 🔍 營養查詢
- 手動查詢食物營養資訊
- 支援 USDA 資料庫查詢
- 包含詳細營養成分

### 📊 系統狀態
- 檢查各項服務是否正常運作
- 實時監控系統健康狀態

## 🔧 本地開發

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 運行應用
```bash
python app.py
```

### Docker 構建
```bash
docker build -t health-assistant .
docker run -p 7860:7860 health-assistant
```

## 📈 性能優化

### 模型載入策略
- 首次使用時載入 AI 模型
- 節省啟動時間
- 按需載入資源

### 記憶體管理
- 使用輕量級模型
- 優化推理速度
- 減少記憶體佔用

## 🔗 相關連結

- **GitHub**：[https://github.com/ting1234555/health_assistant](https://github.com/ting1234555/health_assistant)
- **Hugging Face**：[https://huggingface.co/spaces/yuting111222/health-assistant](https://huggingface.co/spaces/yuting111222/health-assistant)

## 📝 更新日誌

### v1.0.0 (2025-08-04)
- 初始版本發布
- 支援 Docker Space 部署
- 完整的三層 AI 分析架構 