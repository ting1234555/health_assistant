---
title: Health Assistant
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---
# Health Assistant AI

一個整合飲食追蹤、運動記錄和AI圖像辨識的健康生活助手應用。

## 主要功能

* 🍽️ 飲食記錄（支援AI圖像辨識）
* 💧 飲水追蹤
* 🏃‍♂️ 運動記錄
* 📊 營養分析儀表板
* 🤖 AI驅動的個人化建議

## 技術堆疊

### 前端

* React
* TailwindCSS
* Chart.js

### 後端

* Python FastAPI
* SQLAlchemy
* PostgreSQL
* TensorFlow/PyTorch
* Pydantic
* HuggingFace Transformers
* Anthropic Claude API

## 快速開始

### 本地開發

1. 克隆專案

```bash
git clone https://github.com/ting1234555/health_assistant.git
cd health_assistant
```

2. 設置 Python 虛擬環境並安裝依賴：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

pip install -e .  # 以開發模式安裝
```

3. 安裝前端依賴：

```bash
cd frontend
npm install
```

### 啟動服務

#### 後端開發

```bash
# 啟動後端開發服務器
python start_server.py
```

#### 前端開發

```bash
cd frontend
npm run dev
```

## 線上版本

### Hugging Face Spaces

🌐 **線上體驗**: [Health Assistant AI on Hugging Face](https://huggingface.co/spaces/yuting111222/health-assistant)

### GitHub Pages

🌐 **專案頁面**: [GitHub Repository](https://github.com/ting1234555/health_assistant)

## AI 模型架構

### 三層遞進式分析

1. **第一層**: YOLOv5n + SAM + DPT（重量估算）
2. **第二層**: Food101 模型 + USDA API（食物識別）
3. **第三層**: 手動查詢（用戶備援）

### 模型特色

- ✅ **輕量化設計**: 適合 16GB RAM 環境
- ✅ **高準確度**: Food101 模型信心度 95%+
- ✅ **智能降級**: 自動從重量估算降級到識別
- ✅ **營養計算**: 精確的重量 × 營養密度計算

## 開發說明

### 後端開發

# 啟動後端開發服務器
uvicorn backend.main:app --reload

### 前端開發

cd frontend
npm run dev

## 測試

### 運行測試

運行所有測試：

pytest

運行特定測試文件：

pytest tests/test_api/test_main.py      # 運行 API 測試
pytest tests/test_services/             # 運行服務層測試
pytest -k "test_function_name"          # 運行特定測試函數

### 測試覆蓋率報告

生成測試覆蓋率報告：

pytest --cov=backend --cov-report=html

這將在 `htmlcov` 目錄下生成 HTML 格式的覆蓋率報告。

### 代碼風格檢查

使用 black 和 isort 進行代碼格式化：

black .
isort .

### 類型檢查

運行 mypy 進行靜態類型檢查：

mypy .

## 持續整合 (CI)

項目使用 GitHub Actions 進行持續整合。每次推送代碼或創建 Pull Request 時，會自動運行以下檢查：

* 在 Python 3.9, 3.10, 3.11 上運行測試
* 生成測試覆蓋率報告
* 上傳覆蓋率到 Codecov

### 本地運行 CI 檢查

在提交代碼前，可以本地運行 CI 檢查：

# 運行測試和覆蓋率
pytest --cov=backend

# 檢查代碼風格
black --check .
isort --check-only .

# 運行類型檢查
mypy .

## 測試覆蓋率要求

* 所有新代碼應該有對應的測試
* 目標是達到至少 80% 的代碼覆蓋率
* 關鍵業務邏輯應該有完整的測試覆蓋
* 測試應該包含成功和失敗案例
* 使用 `# pragma: no cover` 時需提供正當理由

## 貢獻指南

1. Fork 項目
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 許可證

MIT License - 詳見 LICENSE 文件
