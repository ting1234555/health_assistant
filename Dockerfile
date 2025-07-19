FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=7860
ENV TRANSFORMERS_CACHE=/tmp/hf_cache
ENV HF_HOME=/tmp/hf_home
ENV TORCH_HOME=/tmp/torch_home
ENV HF_DATASETS_CACHE=/tmp/hf_datasets
ENV XDG_CACHE_HOME=/tmp/xdg_cache
ENV DATASET_CACHE_DIR=/tmp/dataset_cache

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"] 