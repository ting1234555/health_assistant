from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
from PIL import Image
import io
import random

app = FastAPI()

# 允許跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模擬食物列表
FOOD_ITEMS = [
    "牛肉麵",
    "滷肉飯",
    "炒飯",
    "水餃",
    "炸雞",
    "三明治",
    "沙拉",
    "義大利麵",
    "披薩",
    "漢堡"
]

@app.post("/api/ai/analyze-food")
async def analyze_food(file: UploadFile = File(...)):
    # 讀取圖片（僅作為示範，不進行實際分析）
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    # 隨機選擇一個食物和信心度
    food = random.choice(FOOD_ITEMS)
    confidence = random.uniform(85.0, 99.9)
    
    # 模擬營養資訊
    nutrition = {
        "calories": random.randint(200, 800),
        "protein": random.randint(10, 30),
        "carbs": random.randint(20, 60),
        "fat": random.randint(5, 25)
    }
    
    # 返回結果
    return {
        "success": True,
        "analysis_time": datetime.now().isoformat(),
        "top_prediction": {
            "label": food,
            "confidence": confidence,
            "nutrition": nutrition,
            "description": f"這是一道美味的{food}，營養豐富且美味可口。"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
