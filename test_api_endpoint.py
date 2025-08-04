#!/usr/bin/env python3
"""
測試 API 端點
"""

import requests
import json
from PIL import Image, ImageDraw
import io

def create_test_image():
    """創建一個測試圖片"""
    # 創建一個 640x640 的圖片
    img = Image.new('RGB', (640, 640), color='white')
    
    # 添加一些簡單的幾何形狀來模擬食物
    draw = ImageDraw.Draw(img)
    
    # 模擬盤子（圓形）
    draw.ellipse([100, 100, 300, 300], fill='lightgray', outline='gray', width=3)
    
    # 模擬食物（橢圓形）
    draw.ellipse([150, 150, 250, 250], fill='brown', outline='darkred', width=2)
    
    # 模擬餐具
    draw.rectangle([400, 200, 450, 400], fill='silver', outline='gray', width=2)
    
    return img

def test_api_endpoint():
    """測試 API 端點"""
    try:
        print("=== 測試 API 端點 ===")
        
        # 創建測試圖片
        test_image = create_test_image()
        
        # 轉換為 bytes
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # 準備請求
        url = "http://localhost:8000/ai/analyze-food-image-with-weight/"
        files = {'file': ('test_image.jpg', img_bytes, 'image/jpeg')}
        
        print(f"正在發送請求到: {url}")
        
        # 發送請求
        response = requests.post(url, files=files)
        
        print(f"響應狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API 請求成功！")
            print("響應內容:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 檢查結果
            if result.get('detected_foods'):
                print(f"🎉 成功偵測到 {len(result['detected_foods'])} 個食物項目！")
                for i, food in enumerate(result['detected_foods']):
                    print(f"  食物 {i+1}: {food.get('food_name', 'Unknown')} - {food.get('estimated_weight', 0):.1f}g")
            elif result.get('fallback_food_suggestion'):
                print(f"🔄 進入輔助模式，建議食物: {result['fallback_food_suggestion']['food_name']}")
            else:
                print("⚠️ 沒有偵測到食物，進入手動模式")
                
        else:
            print(f"❌ API 請求失敗: {response.status_code}")
            print(f"錯誤內容: {response.text}")
            
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_endpoint() 