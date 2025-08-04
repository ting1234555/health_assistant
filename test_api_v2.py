#!/usr/bin/env python3
"""
測試 V2 API 端點
"""

import requests
import json
import time
from PIL import Image
import numpy as np
import io

# API 基礎 URL
BASE_URL = "http://localhost:8000"

def create_test_image():
    """創建測試圖片"""
    # 創建一個簡單的測試圖片
    img_array = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    # 保存到 bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def test_available_models():
    """測試獲取可用模型端點"""
    print("🧪 測試獲取可用模型...")
    
    try:
        response = requests.get(f"{BASE_URL}/ai/v2/available-models")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 獲取可用模型成功")
            print(f"可用偵測模型: {data['available_models']['detection']}")
            print(f"可用分割模型: {data['available_models']['segmentation']}")
            print(f"可用深度模型: {data['available_models']['depth']}")
            return True
        else:
            print(f"❌ 獲取可用模型失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

def test_model_info():
    """測試獲取模型資訊端點"""
    print("\n🧪 測試獲取模型資訊...")
    
    try:
        response = requests.get(f"{BASE_URL}/ai/v2/model-info")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 獲取模型資訊成功")
            print(f"當前配置: {data['current_config']}")
            return True
        else:
            print(f"❌ 獲取模型資訊失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

def test_analyze_food_default():
    """測試預設配置的食物分析"""
    print("\n🧪 測試預設配置的食物分析...")
    
    try:
        # 創建測試圖片
        img_bytes = create_test_image()
        
        # 發送請求
        files = {'image': ('test.jpg', img_bytes, 'image/jpeg')}
        data = {'debug': 'false'}
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/ai/v2/analyze-food", files=files, data=data)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 預設配置食物分析成功")
            print(f"處理時間: {end_time - start_time:.2f} 秒")
            print(f"偵測到食物數量: {len(result.get('detected_foods', []))}")
            print(f"總重量: {result.get('total_estimated_weight', 0)}g")
            print(f"模型資訊: {result.get('model_info', {})}")
            return True
        else:
            print(f"❌ 食物分析失敗: {response.status_code}")
            print(f"錯誤信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

def test_analyze_food_custom_config():
    """測試自定義配置的食物分析"""
    print("\n🧪 測試自定義配置的食物分析...")
    
    try:
        # 創建測試圖片
        img_bytes = create_test_image()
        
        # 自定義配置
        custom_config = {
            "detection": "yolov5n",
            "segmentation": "mobilesam",
            "depth": "dpt_swinv2_tiny"
        }
        
        # 發送請求
        files = {'image': ('test.jpg', img_bytes, 'image/jpeg')}
        data = {
            'model_config': json.dumps(custom_config),
            'debug': 'false'
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/ai/v2/analyze-food", files=files, data=data)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 自定義配置食物分析成功")
            print(f"處理時間: {end_time - start_time:.2f} 秒")
            print(f"偵測到食物數量: {len(result.get('detected_foods', []))}")
            print(f"總重量: {result.get('total_estimated_weight', 0)}g")
            print(f"模型資訊: {result.get('model_info', {})}")
            return True
        else:
            print(f"❌ 食物分析失敗: {response.status_code}")
            print(f"錯誤信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

def test_model_config():
    """測試模型配置端點"""
    print("\n🧪 測試模型配置...")
    
    try:
        # 測試配置
        test_config = {
            "detection": "yolov5n",
            "segmentation": "mobilesam",
            "depth": "dpt_swinv2_tiny"
        }
        
        data = {'model_config': json.dumps(test_config)}
        response = requests.post(f"{BASE_URL}/ai/v2/test-model-config", data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 模型配置測試成功")
            print(f"配置: {result['model_config']}")
            print(f"模型資訊: {result['model_info']}")
            return True
        else:
            print(f"❌ 模型配置測試失敗: {response.status_code}")
            print(f"錯誤信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

def test_compare_models():
    """測試模型比較端點"""
    print("\n🧪 測試模型比較...")
    
    try:
        # 創建測試圖片
        img_bytes = create_test_image()
        
        # 測試配置列表
        configs = [
            {
                "detection": "yolov5n",
                "segmentation": "mobilesam",
                "depth": "dpt_swinv2_tiny"
            },
            {
                "detection": "yolov5n",
                "segmentation": "mobilesam",
                "depth": "dpt_large"
            }
        ]
        
        # 發送請求
        files = {'image': ('test.jpg', img_bytes, 'image/jpeg')}
        data = {'configs': json.dumps(configs)}
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/ai/v2/compare-models", files=files, data=data)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 模型比較成功")
            print(f"比較時間: {end_time - start_time:.2f} 秒")
            print(f"成功配置數: {result['summary']['successful_configs']}")
            print(f"失敗配置數: {result['summary']['failed_configs']}")
            
            for i, comp_result in enumerate(result['comparison_results']):
                if comp_result['status'] == 'success':
                    print(f"  配置 {i}: 成功 (時間: {comp_result['total_time']:.2f}s)")
                else:
                    print(f"  配置 {i}: 失敗 ({comp_result.get('error', 'Unknown error')})")
            
            return True
        else:
            print(f"❌ 模型比較失敗: {response.status_code}")
            print(f"錯誤信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

def main():
    """主測試函數"""
    print("🚀 開始測試 V2 API 端點...")
    
    # 等待服務啟動
    print("等待服務啟動...")
    time.sleep(5)
    
    test_results = []
    
    # 1. 測試獲取可用模型
    test_results.append(("獲取可用模型", test_available_models()))
    
    # 2. 測試獲取模型資訊
    test_results.append(("獲取模型資訊", test_model_info()))
    
    # 3. 測試預設配置食物分析
    test_results.append(("預設配置食物分析", test_analyze_food_default()))
    
    # 4. 測試自定義配置食物分析
    test_results.append(("自定義配置食物分析", test_analyze_food_custom_config()))
    
    # 5. 測試模型配置
    test_results.append(("模型配置測試", test_model_config()))
    
    # 6. 測試模型比較
    test_results.append(("模型比較", test_compare_models()))
    
    # 總結測試結果
    print("\n📊 測試結果總結:")
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 總體結果: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 所有 API 測試通過！V2 API 可以正常使用。")
    else:
        print("⚠️ 部分 API 測試失敗，請檢查服務狀態。")
    
    print("測試完成。")

if __name__ == "__main__":
    main() 