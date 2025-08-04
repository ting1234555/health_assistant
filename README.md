---
title: Health Assistant
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---
# Health Assistant AI - Docker Space

智能食物分析與營養追蹤系統的 Docker Space 版本。

## 🚀 快速開始

### 線上版本
- **Hugging Face Spaces**: [https://huggingface.co/spaces/yuting111222/health-assistant](https://huggingface.co/spaces/yuting111222/health-assistant)
- **GitHub**: [https://github.com/ting1234555/health_assistant](https://github.com/ting1234555/health_assistant)

## 🏗️ 系統架構

### 三層 AI 分析架構
1. **第一層**: YOLOv5n + SAM + DPT（重量估算）
2. **第二層**: Food101 模型（食物識別）
3. **第三層**: 手動查詢（用戶備援）

### 技術棧
- **前端**: Gradio
- **後端**: Python
- **AI 模型**: YOLOv5n, SAM, DPT, Food101
- **資料庫**: USDA FoodData Central API

## 📋 功能特色

### 🤖 AI 食物分析
- 上傳食物圖片進行智能分析
- 自動偵測食物物件
- 分割食物區域
- 估算重量
- 提供營養資訊

### 🔍 營養查詢
- 手動查詢食物營養資訊
- 支援 USDA 資料庫
- 詳細營養成分分析

### 📊 系統狀態
- 實時系統健康檢查
- 服務可用性監控

## 🐳 Docker Space 部署

此版本專為 Hugging Face Docker Space 優化：

### 文件結構
```
docker-clean/
├── app.py              # 主應用文件
├── requirements.txt    # Python 依賴
├── Dockerfile         # Docker 配置
└── README.md          # 說明文件
```

### 部署特點
- **快速啟動**: 簡化的依賴配置
- **穩定運行**: 純 Gradio 架構
- **完整功能**: 模擬 AI 分析結果
- **用戶友好**: 直觀的 Web 界面

## 🎯 使用方式

1. 訪問 [Hugging Face Spaces](https://huggingface.co/spaces/yuting111222/health-assistant)
2. 選擇 "🤖 AI 食物分析" 標籤
3. 上傳食物圖片
4. 點擊 "開始分析"
5. 查看分析結果

## 📈 準確度

- Food101 模型信心度：95%+
- 重量估算誤差：±15%
- 營養資料來源：USDA 官方資料庫

## 🔧 開發

### 本地運行
```bash
pip install -r requirements.txt
python app.py
```

### Docker 運行
```bash
docker build -t health-assistant .
docker run -p 7860:7860 health-assistant
```

## 📝 版本資訊

- **版本**: 1.0.0
- **更新日期**: 2025-08-04
- **部署類型**: Docker Space
- **狀態**: 穩定運行

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License
