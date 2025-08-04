import React, { useState, useRef, useEffect } from 'react';
import './AIFoodAnalyzer.css';
import { Camera, Upload, Zap, Search, PlusCircle, Trash2, Edit, BrainCircuit, PenSquare } from 'lucide-react';

const AIFoodAnalyzer = () => {
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [imageSrc, setImageSrc] = useState(null);
  const fileInputRef = useRef(null);
  const [foodDiary, setFoodDiary] = useState([]);
  
  const [manualWeight, setManualWeight] = useState('');
  
  // --- 模式狀態管理 ---
  const [mode, setMode] = useState('initial'); // 'initial', 'ai', 'manual', 'assisted'
  
  const [manualFoodName, setManualFoodName] = useState('');
  const [manualNutrition, setManualNutrition] = useState(null);
  const [isManualLoading, setIsManualLoading] = useState(false);
  const [manualError, setManualError] = useState('');

  // --- 日記編輯相關 state ---
  const [editingMeal, setEditingMeal] = useState(null);
  const [editWeight, setEditWeight] = useState('');

  const resetAllModes = () => {
    setResult(null);
    setError('');
    setIsLoading(false);
    setImageSrc(null);
    setMode('initial'); // 回到初始選擇畫面
    setManualFoodName('');
    setManualNutrition(null);
    setManualError('');
    setManualWeight('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  useEffect(() => {
    const diary = JSON.parse(localStorage.getItem('foodDiary')) || [];
    setFoodDiary(diary);
  }, []);

  const saveFoodDiary = (diary) => {
    localStorage.setItem('foodDiary', JSON.stringify(diary));
    setFoodDiary(diary);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImageSrc(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const processImage = async () => {
    if (!imageSrc) return;
    setIsLoading(true);
    setError('');
    setResult(null);

    try {
      const blob = await (await fetch(imageSrc)).blob();
      const formData = new FormData();
      formData.append('file', blob, 'food_image.jpg');

      const aiResponse = await fetch('http://localhost:8000/api/ai/analyze-food-image-with-weight/', {
        method: 'POST',
        body: formData,
      });
      if (!aiResponse.ok) {
        throw new Error(`伺服器錯誤: ${aiResponse.status}`);
      }
      const aiData = await aiResponse.json();
      
      if (aiData.detected_foods && aiData.detected_foods.length > 0) {
        setResult({ originalResponse: aiData });
        setMode('ai');
      } else if (aiData.fallback_food_suggestion) {
        setError(aiData.note);
        setMode('assisted');
        setManualFoodName(aiData.fallback_food_suggestion.food_name);
        handleManualLookup(aiData.fallback_food_suggestion.food_name);
      } else {
        setError(aiData.note || 'AI無法辨識出任何食物項目，請嘗試手動輸入。');
        setMode('manual');
      }
    } catch (err) {
      const errorMessage = err.message || '分析時發生未知錯誤，請稍後再試。';
      setError(errorMessage);
      setMode('manual');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleManualLookup = async (foodNameToLookup) => {
    const foodName = foodNameToLookup || manualFoodName;
    if (!foodName) {
      setManualError('請輸入食物名稱。');
      return;
    }
    setIsManualLoading(true);
    setManualError('');
    setManualNutrition(null);
    try {
      const response = await fetch(`http://localhost:8000/api/nutrition/lookup?food_name=${encodeURIComponent(foodName)}`);
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || '查詢失敗');
      }
      const data = await response.json();
      setManualNutrition(data);
    } catch (err) {
      setManualError(err.message);
    } finally {
      setIsManualLoading(false);
    }
  };
  
  function addToFoodDiary() {
    if (mode === 'ai' && result && result.originalResponse) {
      const newMeals = result.originalResponse.detected_foods.map(foodItem => ({
        foodName: foodItem.food_name,
        estimatedWeight: foodItem.estimated_weight,
        nutrition: foodItem.nutrition,
        id: Date.now() + Math.random(),
        timestamp: new Date().toISOString()
      }));
      saveFoodDiary([...foodDiary, ...newMeals]);
      alert(`${newMeals.length} 項食物已加入記錄！`);
    } else if ((mode === 'assisted' || mode === 'manual') && manualNutrition && manualWeight) {
      const weight = parseFloat(manualWeight);
      if (isNaN(weight) || weight <= 0) {
        alert('請輸入有效的實際重量。');
        return;
      }
      const weightRatio = weight / 100;
      const finalNutrition = Object.keys(manualNutrition).reduce((acc, key) => {
        if (typeof manualNutrition[key] === 'number') acc[key] = manualNutrition[key] * weightRatio;
        else acc[key] = manualNutrition[key];
        return acc;
      }, {});
      const meal = {
        foodName: manualNutrition.food_name || manualFoodName,
        estimatedWeight: weight,
        nutrition: finalNutrition,
        standardNutrition: manualNutrition,
        id: Date.now(),
        timestamp: new Date().toISOString()
      };
      saveFoodDiary([...foodDiary, meal]);
      alert(`${meal.foodName} (${weight}g) 已加入記錄！`);
    } else {
       alert('沒有可加入的分析結果，或手動資料不完整。');
       return;
    }
    resetAllModes();
  }

  const handleEditMeal = (meal) => {
    setEditingMeal(meal);
    setEditWeight(meal.estimatedWeight.toString());
  };

  const handleUpdateMeal = () => {
    if (!editingMeal || !editWeight) return;
    const weight = parseFloat(editWeight);
    if (isNaN(weight) || weight <= 0) {
      alert('請輸入有效的重量。');
      return;
    }
    const standardNutrition = editingMeal.standardNutrition; 
    if(!standardNutrition) {
        alert("缺少標準營養數據，無法更新。");
        setEditingMeal(null);
        return;
    }
    const weightRatio = weight / 100;
    const updatedNutrition = Object.keys(standardNutrition).reduce((acc, key) => {
      if (typeof standardNutrition[key] === 'number') acc[key] = standardNutrition[key] * weightRatio;
      else acc[key] = standardNutrition[key];
      return acc;
    }, {});
    const updatedDiary = foodDiary.map(m => 
      m.id === editingMeal.id ? { ...m, estimatedWeight: weight, nutrition: updatedNutrition } : m
    );
    saveFoodDiary(updatedDiary);
    setEditingMeal(null);
    setEditWeight('');
  };

  const deleteMeal = (mealIdToDelete) => {
    saveFoodDiary(foodDiary.filter(meal => meal.id !== mealIdToDelete));
  };

  const renderNutritionGrid = (nutritionData) => {
    if (!nutritionData) return null;
    return (
      <div className="nutrition-grid mb-4">
        {Object.entries(nutritionData)
          .filter(([key]) => !['food_name', 'chinese_name', 'error'].includes(key))
          .map(([key, value]) => (
          <div key={key} className="nutrition-item">
            <span className="nutrition-label">{key.charAt(0).toUpperCase() + key.slice(1)}</span>
            <span className="nutrition-value">{typeof value === 'number' ? value.toFixed(1) : value} {key === 'calories' ? 'kcal' : 'g'}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="container mx-auto p-4">
      <div className="main-panel bg-white p-6 rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold text-center mb-2">AI食物營養分析器</h1>
        <p className="text-center text-gray-500 mb-6">智能分析您的飲食營養</p>

        <div className="content-area">
          {mode === 'initial' && (
            <div className="initial-choice-container grid grid-cols-1 md:grid-cols-2 gap-6 text-center">
              <div className="choice-card" onClick={() => setMode('ai')}>
                <BrainCircuit size={48} className="mx-auto text-indigo-500 mb-4" />
                <h3 className="text-xl font-semibold mb-2">AI 自動分析</h3>
                <p className="text-gray-500">上傳食物圖片，讓 AI 自動為您分析重量與營養。</p>
              </div>
              <div className="choice-card" onClick={() => setMode('manual')}>
                <PenSquare size={48} className="mx-auto text-green-500 mb-4" />
                <h3 className="text-xl font-semibold mb-2">直接手動記錄</h3>
                <p className="text-gray-500">已經知道吃了什麼？直接搜尋食物並記錄下來。</p>
              </div>
            </div>
          )}

          {mode === 'ai' && (
            <div className="ai-flow-container">
              {!result && (
                <div>
                  <p className="text-center text-sm text-blue-600 bg-blue-50 p-3 rounded-lg mb-4">
                    請將硬幣、餐具等標準物品放在食物旁邊一起拍照，AI會更準確！
                  </p>
                  <div className="image-preview mb-4 h-64 flex items-center justify-center bg-gray-100 rounded-lg">
                    {isLoading ? <div className="loading-spinner"></div> : 
                     imageSrc ? <img src={imageSrc} alt="Food" className="max-h-full max-w-full rounded-lg" /> : <span className="text-gray-400">圖片預覽區</span>}
                  </div>
                  <div className="button-group grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                    <button onClick={() => alert('相機功能開發中！')} className="btn-secondary" disabled={isLoading}><Camera className="mr-2" />開啟相機</button>
                    <button onClick={processImage} className="btn-primary" disabled={isLoading || !imageSrc}>{isLoading ? '分析中...' : <><Zap className="mr-2" />開始分析</>}</button>
                    <input type="file" accept="image/*" ref={fileInputRef} onChange={handleFileSelect} className="hidden" />
                    <button onClick={() => fileInputRef.current.click()} className="btn-secondary" disabled={isLoading}><Upload className="mr-2" />上傳圖片</button>
                  </div>
                   <div className="text-center">
                    <button onClick={resetAllModes} className="btn-link" disabled={isLoading}>返回</button>
                  </div>
                </div>
              )}
              {result && (
                <div className="result-card">
                  <h3 className="text-lg font-bold text-gray-800 mb-2">AI 分析結果</h3>
                  <p className="text-sm text-gray-500 mb-4">{result.originalResponse.note}</p>
                  {renderNutritionGrid(result.originalResponse.total_nutrition)}
                   <button onClick={addToFoodDiary} className="btn-primary">加入飲食記錄</button>
                   <button onClick={resetAllModes} className="btn-secondary mt-2 ml-2">完成並返回</button>
                </div>
              )}
            </div>
          )}
          
          {mode === 'assisted' && (
            <div className="assisted-mode-card">
              <h3 className="text-lg font-bold text-yellow-600 mb-2">AI 輔助記錄模式</h3>
              {error && <p className="text-sm text-gray-600 mb-3">{error}</p>}
              {isManualLoading && <p>查詢營養資訊中...</p>}
              {manualError && <p className="text-sm text-red-600 mb-3">{manualError}</p>}
              {manualNutrition && (
                <div>
                  <p className="text-md text-gray-800 mb-4">AI 建議的食物「<strong>{manualNutrition.food_name || manualFoodName}</strong>」每 100g 的營養如下：</p>
                  {renderNutritionGrid(manualNutrition)}
                  <div className="manual-weight-input">
                     <label className="block text-sm font-medium text-gray-700 mb-1">請輸入這份餐點的實際重量 (g):</label>
                     <input type="number" value={manualWeight} onChange={(e) => setManualWeight(e.target.value)} placeholder="例如：250" className="input-field w-full" />
                  </div>
                  <button onClick={addToFoodDiary} className="btn-primary mt-4">加入日記</button>
                  <button onClick={resetAllModes} className="btn-secondary mt-2 ml-2">取消</button>
                </div>
              )}
            </div>
          )}

          {mode === 'manual' && (
            <div className="manual-mode-card">
              <h3 className="text-lg font-bold text-gray-700 mb-2">手動記錄模式</h3>
              {error && <p className="text-sm text-red-500 mb-3">{error}</p>}
              <p className="text-sm text-gray-500 mb-4">在這裡手動查詢並記錄您的餐點。</p>
              <div className="manual-lookup-form">
                <input type="text" value={manualFoodName} onChange={(e) => setManualFoodName(e.target.value)} placeholder="輸入食物名稱" className="input-field" />
                <button onClick={() => handleManualLookup()} disabled={isManualLoading} className="btn-secondary ml-2">{isManualLoading ? '查詢中...' : <><Search className="mr-1" />查詢營養</>}</button>
              </div>
              {manualError && <p className="text-sm text-red-600 my-3">{manualError}</p>}
              {manualNutrition && (
                 <div>
                  <p className="text-md text-gray-800 my-4">「<strong>{manualNutrition.food_name || manualFoodName}</strong>」每 100g 的營養如下：</p>
                  {renderNutritionGrid(manualNutrition)}
                  <div className="manual-weight-input">
                     <label className="block text-sm font-medium text-gray-700 mb-1">請輸入實際重量 (g):</label>
                     <input type="number" value={manualWeight} onChange={(e) => setManualWeight(e.target.value)} placeholder="例如：150" className="input-field w-full" />
                  </div>
                  <button onClick={addToFoodDiary} className="btn-primary mt-4">加入日記</button>
                </div>
              )}
              <div className="text-center mt-4">
                <button onClick={resetAllModes} className="btn-link">返回</button>
              </div>
            </div>
          )}
        </div>
      </div>
      
      <div className="diary-section mt-8">
        <h2 className="text-xl font-bold mb-4">今日飲食日記</h2>
        {foodDiary.length === 0 ? (
          <p>今天還沒有飲食記錄。</p>
        ) : (
          <ul className="diary-list">
            {foodDiary.map(meal => (
              <li key={meal.id} className="diary-item">
                {editingMeal && editingMeal.id === meal.id ? (
                  <div className="diary-edit-view">
                    <span>{meal.foodName}</span>
                    <input type="number" value={editWeight} onChange={(e) => setEditWeight(e.target.value)} className="edit-weight-input"/>
                    <span>g</span>
                    <button onClick={handleUpdateMeal} className="btn-edit-save">儲存</button>
                    <button onClick={() => setEditingMeal(null)} className="btn-edit-cancel">取消</button>
                  </div>
                ) : (
                  <div className="diary-display-view">
                    <div className="diary-item-header">
                      <span>{meal.foodName} ({meal.estimatedWeight}g)</span>
                      <div>
                        <button onClick={() => handleEditMeal(meal)} className="btn-icon" disabled={!meal.standardNutrition} title={!meal.standardNutrition ? "AI分析項目無法編輯" : "編輯"}><Edit size={16} /></button>
                        <button onClick={() => deleteMeal(meal.id)} className="btn-icon"><Trash2 size={16} /></button>
                      </div>
                    </div>
                    {renderNutritionGrid(meal.nutrition)}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default AIFoodAnalyzer; 