FROM python:3.11-slim

WORKDIR /code

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製需求文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案檔案
COPY . .

# 設定環境變數
ENV PYTHONPATH=/code

# 暴露端口
EXPOSE 7860

# 啟動指令
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]