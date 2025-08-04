import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ai_router, meal_router, nutrition_router
from app.database import engine, Base
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建資料庫表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Health Assistant API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(ai_router.router)
app.include_router(meal_router.router)
app.include_router(nutrition_router.router, prefix="/api/nutrition", tags=["nutrition"])

@app.get("/")
async def root():
    return {"message": "Health Assistant API is running"}

@app.on_event("startup")
async def startup_event():
    """應用程序啟動時的事件"""
    logger.info("Health Assistant API 正在啟動...")
    logger.info("AI 模型將在首次使用時載入，以節省啟動時間")

@app.on_event("shutdown")
async def shutdown_event():
    """應用程序關閉時的事件"""
    logger.info("Health Assistant API 正在關閉...")

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "routers": ["ai_router", "meal_router", "nutrition_router"],
        "endpoints": [
            "/ai/analyze-food-image/",
            "/ai/analyze-food-image-with-weight/",
            "/ai/health",
            "/api/nutrition/lookup"
        ]
    }

# Gradio 界面
def create_gradio_interface():
    """創建 Gradio 界面"""
    
    def analyze_food_image(image):
        """分析食物圖片"""
        if image is None:
            return "請上傳圖片"
        
        # 這裡可以調用 AI 分析功能
        return "食物分析結果將在這裡顯示"
    
    def lookup_nutrition(food_name):
        """查詢營養資訊"""
        if not food_name:
            return "請輸入食物名稱"
        
        # 這裡可以調用營養查詢功能
        return f"查詢 {food_name} 的營養資訊"
    
    # 創建界面
    with gr.Blocks(title="Health Assistant AI") as demo:
        gr.Markdown("# 🏥 Health Assistant AI")
        gr.Markdown("## 智能食物分析與營養追蹤系統")
        
        with gr.Tab("AI 食物分析"):
            gr.Markdown("### 上傳食物圖片進行 AI 分析")
            image_input = gr.Image(label="上傳食物圖片")
            analyze_btn = gr.Button("開始分析", variant="primary")
            result_output = gr.Textbox(label="分析結果", lines=5)
            
            analyze_btn.click(
                fn=analyze_food_image,
                inputs=image_input,
                outputs=result_output
            )
        
        with gr.Tab("營養查詢"):
            gr.Markdown("### 手動查詢食物營養資訊")
            food_input = gr.Textbox(label="食物名稱", placeholder="例如：apple, chicken breast")
            lookup_btn = gr.Button("查詢營養", variant="primary")
            nutrition_output = gr.Textbox(label="營養資訊", lines=10)
            
            lookup_btn.click(
                fn=lookup_nutrition,
                inputs=food_input,
                outputs=nutrition_output
            )
        
        with gr.Tab("系統狀態"):
            gr.Markdown("### 系統健康狀態")
            status_output = gr.JSON(label="API 狀態")
            
            def get_status():
                return {
                    "status": "healthy",
                    "services": {
                        "ai_analysis": "available",
                        "nutrition_api": "available",
                        "weight_estimation": "available"
                    }
                }
            
            status_btn = gr.Button("檢查狀態")
            status_btn.click(fn=get_status, outputs=status_output)
    
    return demo

# 創建 Gradio 應用
demo = create_gradio_interface()

# 將 Gradio 應用掛載到 FastAPI
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860) 