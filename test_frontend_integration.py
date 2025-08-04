#!/usr/bin/env python3
"""
測試前端和後端的整合
"""

import requests
import json
from PIL import Image, ImageDraw
import io

def test_complete_flow():
    """測試完整的食物分析流程"""
    print("=== 測試完整食物分析流程 ===")
    
    # 1. 測試營養查詢 API
    print("\n1. 測試營養查詢 API...")
    try:
        response = requests.get("http://localhost:8000/api/nutrition/lookup?food_name=sushi")
        if response.status_code == 200:
            nutrition_data = response.json()
            print(f"✅ 營養查詢成功: {nutrition_data['food_name']}")
            print(f"   熱量: {nutrition_data['calories']} 卡")
            print(f"   蛋白質: {nutrition_data['protein']} g")
        else:
            print(f"❌ 營養查詢失敗: {response.status_code}")
            print(f"   錯誤: {response.text}")
    except Exception as e:
        print(f"❌ 營養查詢異常: {e}")
    
    # 2. 測試 AI 食物分析 API
    print("\n2. 測試 AI 食物分析 API...")
    try:
        # 創建測試圖片
        img = Image.new('RGB', (640, 640), color='white')
        draw = ImageDraw.Draw(img)
        draw.ellipse([100, 100, 300, 300], fill='lightgray', outline='gray', width=3)
        draw.ellipse([150, 150, 250, 250], fill='brown', outline='darkred', width=2)
        
        # 轉換為 bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # 發送請求
        files = {'file': ('test_image.jpg', img_bytes, 'image/jpeg')}
        response = requests.post("http://localhost:8000/ai/analyze-food-image-with-weight/", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI 分析成功")
            print(f"   備註: {result.get('note', '無')}")
            
            if result.get('detected_foods'):
                print(f"   偵測到 {len(result['detected_foods'])} 個食物")
                for food in result['detected_foods']:
                    print(f"     - {food['food_name']}: {food['estimated_weight']}g")
            elif result.get('fallback_food_suggestion'):
                print(f"   建議食物: {result['fallback_food_suggestion']['food_name']}")
            else:
                print("   沒有偵測到食物，進入手動模式")
        else:
            print(f"❌ AI 分析失敗: {response.status_code}")
            print(f"   錯誤: {response.text}")
    except Exception as e:
        print(f"❌ AI 分析異常: {e}")
    
    # 3. 測試 API 文檔
    print("\n3. 測試 API 文檔...")
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ API 文檔可訪問")
        else:
            print(f"❌ API 文檔不可訪問: {response.status_code}")
    except Exception as e:
        print(f"❌ API 文檔異常: {e}")
    
    print("\n=== 測試完成 ===")

if __name__ == "__main__":
    test_complete_flow() 