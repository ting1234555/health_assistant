import React, { useState, useRef, useEffect } from 'react';
import Chart from 'chart.js/auto';
import './AIFoodAnalyzer.css';
import { Camera, Upload, Zap, Search, PlusCircle, Trash2, Edit } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const defaultProfile = {
  name: '', age: '', gender: '', height: '', weight: '',
  activityLevel: 'sedentary', healthGoal: 'maintain',
  dailyCalories: 0, proteinGoal: 0, fiberGoal: 25, waterGoal: 2000
};

function AIFoodAnalyzer() {
  // 分頁狀態
  const [tab, setTab] = useState('analyzer');
  // 個人資料
  const [profile, setProfile] = useState(() => {
    const stored = localStorage.getItem('userProfile');
    return stored ? JSON.parse(stored) : { ...defaultProfile };
  });
  // 食物日記
  const [foodDiary, setFoodDiary] = useState([]);
  // 分析狀態
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  // 相機/上傳
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const [stream, setStream] = useState(null);
  // Chart
  const chartRef = useRef(null);
  // 新增一個 state 來存放預覽圖片的 URL
  const [previewImage, setPreviewImage] = useState(null);
  const [manualWeight, setManualWeight] = useState('');
  const [editingMealId, setEditingMealId] = useState(null);
  const [editingWeight, setEditingWeight] = useState('');
  // 計算顯示用的營養資訊（根據手動重量自動調整）
  function getAdjustedNutrition() {
    if (!result) return {};
    const baseWeight = result.estimatedWeight || 100;
    const targetWeight = manualWeight ? Number(manualWeight) : baseWeight;
    if (!result.nutrition) return {};
    const ratio = targetWeight / baseWeight;
    const adjusted = {};
    for (const [k, v] of Object.entries(result.nutrition)) {
      adjusted[k] = Math.round((v || 0) * ratio);
    }
    return adjusted;
  }
  const adjustedNutrition = getAdjustedNutrition();

  // --- 新增手動模式相關 state ---
  const [isManualMode, setIsManualMode] = useState(false);
  const [manualFoodName, setManualFoodName] = useState('');
  const [manualNutrition, setManualNutrition] = useState(null);
  const [isManualLoading, setIsManualLoading] = useState(false);
  const [manualError, setManualError] = useState('');

  // --- 新增 AI 輔助模式相關 state ---
  const [isAssistedMode, setIsAssistedMode] = useState(false);
  
  // --- 新增日記編輯相關 state ---
  const [editingMeal, setEditingMeal] = useState(null);
  const [editWeight, setEditWeight] = useState('');

  // 初始化日記
  useEffect(() => {
    loadFoodDiary();
    // 清理相機
    return () => { if (stream) stream.getTracks().forEach(t => t.stop()); };
  }, []);

  // 分頁切換時載入日記
  useEffect(() => {
    if (tab === 'tracking') loadFoodDiary();
  }, [tab]);

  // 分頁切換
  const switchTab = (t) => { setTab(t); setError(''); setResult(null); };

  // 個人資料儲存
  const handleProfileChange = e => {
    const { name, value } = e.target;
    setProfile(p => ({ ...p, [name]: value }));
  };
  const saveProfile = e => {
    e.preventDefault();
    // 計算每日建議
    const bmr = profile.gender === 'male'
      ? 88.362 + (13.397 * profile.weight) + (4.799 * profile.height) - (5.677 * profile.age)
      : 447.593 + (9.247 * profile.weight) + (3.098 * profile.height) - (4.330 * profile.age);
    const activityMultipliers = { sedentary: 1.2, light: 1.375, moderate: 1.55, active: 1.725, extra: 1.9 };
    let calories = bmr * (activityMultipliers[profile.activityLevel] || 1.2);
    const goalAdjustments = { lose: -300, gain: 300, muscle: 200 };
    calories += goalAdjustments[profile.healthGoal] || 0;
    const dailyCalories = Math.round(calories);
    const proteinGoal = Math.round(dailyCalories * 0.25 / 4);
    setProfile(p => {
      const newP = { ...p, dailyCalories, proteinGoal, fiberGoal: 25, waterGoal: 2000 };
      localStorage.setItem('userProfile', JSON.stringify(newP));
      return newP;
    });
    alert('個人資料已儲存！');
    setTab('analyzer');
  };

  // 日記
  function loadFoodDiary() {
    const today = new Date().toISOString().slice(0, 10);
    const stored = localStorage.getItem(`foodDiary_${today}`);
    setFoodDiary(stored ? JSON.parse(stored) : []);
  }
  function saveFoodDiary(diary) {
    const today = new Date().toISOString().slice(0, 10);
    localStorage.setItem(`foodDiary_${today}`, JSON.stringify(diary));
    setFoodDiary(diary);
  }
  // 修改 addToFoodDiary，以處理多食物日記格式
  function addToFoodDiary() {
    // AI 模式
    if (result && result.originalResponse && result.originalResponse.detected_foods) {
      const newMeals = result.originalResponse.detected_foods.map(foodItem => ({
        foodName: foodItem.food_name,
        estimatedWeight: foodItem.estimated_weight,
        nutrition: foodItem.nutrition,
        id: Date.now() + Math.random(),
        timestamp: new Date().toISOString()
      }));
      const newDiary = [...foodDiary, ...newMeals];
      saveFoodDiary(newDiary);
      alert(`${newMeals.length} 項食物已加入記錄！`);
      return;
    }
    
    // 模式 2 & 3: AI 輔助模式或完全手動模式
    if ((isAssistedMode || isManualMode) && manualNutrition && manualWeight) {
      const weight = parseFloat(manualWeight);
      if (isNaN(weight) || weight <= 0) {
        alert('請輸入有效的實際重量。');
        return;
      }
      
      const weightRatio = weight / 100;
      const finalNutrition = Object.keys(manualNutrition).reduce((acc, key) => {
        if (typeof manualNutrition[key] === 'number') {
          acc[key] = manualNutrition[key] * weightRatio;
        } else {
          acc[key] = manualNutrition[key];
        }
        return acc;
      }, {});

      const meal = {
        foodName: manualNutrition.food_name || manualFoodName,
        estimatedWeight: weight,
        nutrition: finalNutrition,
        standardNutrition: manualNutrition, // <--- 儲存100g的標準營養
        id: Date.now(),
        timestamp: new Date().toISOString()
      };
      
      const newDiary = [...foodDiary, meal];
      saveFoodDiary(newDiary);
      alert(`${meal.foodName} (${weight}g) 已加入記錄！`);

      // 重設所有模式狀態
      setIsManualMode(false);
      setIsAssistedMode(false);
      setManualFoodName('');
      setManualNutrition(null);
      setManualWeight('');
      setError('');
      setImageSrc(null);

    } else {
       alert('沒有可加入的分析結果，或手動資料不完整。');
    }
  }

  // --- DIARY EDIT/DELETE FUNCTIONS ---

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
    
    // 重新計算營養
    // 假設 meal 物件中儲存了 100g 的營養標準
    // 這需要我們在儲存時做一些調整
    const weightRatio = weight / 100;
    const standardNutrition = editingMeal.standardNutrition; 
    
    // 如果沒有標準營養，我們無法重新計算，這是一個簡化處理
    // 在真實應用中，我們會在 addToFoodDiary 時就把 100g 的標準營養存起來
    if(!standardNutrition) {
        alert("缺少標準營養數據，無法更新。");
        setEditingMeal(null);
        return;
    }

    const updatedNutrition = Object.keys(standardNutrition).reduce((acc, key) => {
      if (typeof standardNutrition[key] === 'number') {
        acc[key] = standardNutrition[key] * weightRatio;
      } else {
        acc[key] = standardNutrition[key];
      }
      return acc;
    }, {});

    const updatedDiary = foodDiary.map(m => 
      m.id === editingMeal.id 
        ? { ...m, estimatedWeight: weight, nutrition: updatedNutrition }
        : m
    );
    
    saveFoodDiary(updatedDiary);
    setEditingMeal(null);
    setEditWeight('');
  };


  const deleteMeal = (mealIdToDelete) => {
    const confirmed = window.confirm("確定要刪除這筆紀錄嗎？");
    if (confirmed) {
        const newDiary = foodDiary.filter(meal => meal.id !== mealIdToDelete);
        saveFoodDiary(newDiary);
    }
  };

  const cancelEditing = () => {
      setEditingMeal(null);
      setEditWeight('');
  };

  // 相機/圖片分析
  const startCamera = async () => {
    setError('');
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        setStream(mediaStream);
      }
    } catch (err) {
      setError('無法開啟相機，請檢查權限。');
    }
  };
  const capturePhoto = () => {
    setError('');
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(blob => {
      if (blob) {
        setPreviewImage(URL.createObjectURL(blob));
        processImage(blob);
      }
      else setError('無法擷取圖片，請再試一次');
    }, 'image/jpeg');
  };
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setPreviewImage(URL.createObjectURL(file));
      processImage(file);
      e.target.value = '';
    }
  };
  const processImage = async (imageSource) => {
    setLoading(true);
    setResult(null);
    setError('');
    const formData = new FormData();
    formData.append('file', imageSource);
    try {
      const aiResponse = await fetch(`${API_BASE_URL}/ai/analyze-food-image-with-weight/`, {
        method: 'POST', body: formData,
      });
      if (!aiResponse.ok) {
        const errorData = await aiResponse.json();
        throw new Error(errorData.detail || `AI辨識失敗 (狀態碼: ${aiResponse.status})`);
      }
      const aiData = await aiResponse.json();
      const foodName = aiData.food_name;
      if (!foodName || foodName === 'Unknown') throw new Error('AI無法辨識出食物名稱。');
      let analysis = {
        foodName,
        description: `AI 辨識結果：${foodName}`,
        healthIndex: 75,
        glycemicIndex: 50,
        benefits: [`含有 ${foodName} 的營養成分`],
        nutrition: { calories: 150, protein: 8, carbs: 20, fat: 5, fiber: 3, sugar: 2 },
        vitamins: { 'Vitamin C': 15, 'Vitamin A': 10 },
        minerals: { 'Iron': 2, 'Calcium': 50 }
      };
      setResult(analysis);
    } catch (err) {
      const errorMessage = err.message || '分析時發生未知錯誤，請稍後再試。';
      setError(errorMessage);
      setResult(null);
      setIsManualMode(true); // 發生任何其他錯誤也切換到完全手動模式
      setIsAssistedMode(false);
    } finally {
      setLoading(false);
    }
  };
  
  // --- 新增手動查詢營養的函式 (可選傳入 foodName) ---
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
      console.log('營養查詢成功:', data);
      setManualNutrition(data);
    } catch (err) {
      console.error('營養查詢錯誤:', err);
      let errorMessage = '查詢失敗，請稍後再試';
      
      if (err.message) {
        // 處理可能的模板字符串問題
        errorMessage = err.message.replace(/\$\{encodeURIComponent\(foodName\)\}/g, foodName);
      }
      
      setManualError(errorMessage);
    } finally {
      setIsManualLoading(false);
    }
  };

  // Chart.js 本週熱量趨勢
  useEffect(() => {
    if (tab !== 'tracking' || !chartRef.current) return;
    if (chartRef.current._chart) chartRef.current._chart.destroy();
    // 取得本週資料
    const days = ['日','一','二','三','四','五','六'];
    const week = [];
    const now = new Date();
    for (let i = 6; i >= 0; i--) {
      const d = new Date(now);
      d.setDate(now.getDate() - i);
      const key = d.toISOString().slice(0,10);
      const diary = JSON.parse(localStorage.getItem(`foodDiary_${key}`) || '[]');
      const total = diary.reduce((sum, m) => sum + (m.nutrition?.calories||0), 0);
      week.push({ day: days[d.getDay()], calories: total });
    }
    chartRef.current._chart = new Chart(chartRef.current.getContext('2d'), {
      type: 'line',
      data: {
        labels: week.map(d=>d.day),
        datasets: [{
          label: '熱量',
          data: week.map(d=>d.calories),
          borderColor: '#667eea',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          tension: 0.3, pointRadius: 4, fill: true
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { stepSize: 200 } } },
        responsive: true, maintainAspectRatio: false
      }
    });
  }, [tab, foodDiary]);

  // UI
  return (
    <div className="app-container">
      <div className="header">
        <h1 className="title">🍎 AI食物營養分析器</h1>
        <p className="subtitle">智能分析您的飲食營養</p>
      </div>
      
      <div className="tab-nav">
        <button className={`tab-btn${tab === 'analyzer' ? ' active' : ''}`} onClick={() => switchTab('analyzer')}>分析食物</button>
        <button className={`tab-btn${tab === 'profile' ? ' active' : ''}`} onClick={() => switchTab('profile')}>個人資料</button>
        <button className={`tab-btn${tab === 'tracking' ? ' active' : ''}`} onClick={() => switchTab('tracking')}>營養追蹤</button>
      </div>

      {tab === 'analyzer' && (
        <div id="analyzerContent">
          {/* 新增提示訊息 */}
          <div style={{textAlign:'center',color:'#185a9d',fontWeight:'bold',marginBottom:'0.5rem',fontSize:'1rem'}}>
            請將硬幣、餐具等標準物品放在食物旁邊一起拍照，AI會更準確！
          </div>
          <div className="camera-container" style={{position:'relative', width:'100%', maxWidth:300, margin:'0 auto'}}>
            {/* 預覽圖片優先顯示，否則顯示相機畫面 */}
            {previewImage ? (
              <img src={previewImage} alt="預覽圖片" style={{width:'100%', borderRadius:15, boxShadow:'0 5px 15px rgba(0,0,0,0.2)', background:'#000', objectFit:'contain', maxHeight:220}} />
            ) : (
              <video ref={videoRef} autoPlay playsInline style={{width:'100%', borderRadius:15, boxShadow:'0 5px 15px rgba(0,0,0,0.2)', background:'#000'}} />
            )}
            <canvas ref={canvasRef} style={{display:'none'}} />
          </div>

          <div className="controls">
            <button onClick={startCamera}>📷 開啟相機</button>
            <button onClick={capturePhoto}>📸 拍照分析</button>
            <button className="upload-btn" onClick={() => fileInputRef.current && fileInputRef.current.click()}>📁 上傳圖片</button>
            <input ref={fileInputRef} type="file" className="file-input" accept="image/*" onChange={handleFileUpload} style={{ display: 'none' }} />
          </div>

          {loading && (
            <div className="loading" style={{display:'flex'}}>
              <div className="spinner"></div>
              <p>AI正在分析食物中...</p>
            </div>
          )}

          {error && <div style={{color:'red',textAlign:'center',margin:'1rem 0'}}>{error}</div>}

          {result && (
            <div className="result" style={{display:'block'}}>
              <div className="food-info">
                <h3 className="food-name">{result.foodName}</h3>
                <button className="add-to-diary" onClick={addToFoodDiary}>加入飲食記錄</button>
              </div>

                  <div className="health-indices">
                    <div className="health-index">
                      <div className="index-label">健康指數</div>
                      <div className="index-meter">
                        <div className="meter-fill" style={{width:`${result.healthIndex||75}%`, background:'linear-gradient(45deg,#43cea2,#185a9d)'}}></div>
                      </div>
                      <div className="index-value">{result.healthIndex||75}/100</div>
                    </div>
                    <div className="health-index">
                      <div className="index-label">升糖指數</div>
                      <div className="index-meter">
                        <div className="meter-fill" style={{width:`${result.glycemicIndex||50}%`, background:'linear-gradient(45deg,#ff9a9e,#fad0c4)'}}></div>
                      </div>
                      <div className="index-value">{result.glycemicIndex||50}/100</div>
                    </div>
                  </div>

                  <p className="food-description">{result.description || `這是 ${result.foodName}`}</p>

                  <div className="benefits-tags">
                    {(result.benefits||[`${result.foodName} 的營養價值`]).map((b,i)=>(
                      <span key={i} className="benefit-tag">{b}</span>
                    ))}
                  </div>

                  <div className="nutrition-details">
                    <div className="nutrition-section">
                      <h4 className="nutrition-section-title">基本營養素</h4>
                      <div className="nutrition-grid">
                        {Object.entries(adjustedNutrition).map(([k,v])=>(
                          <div key={k} className="nutrition-item">
                            <div className="nutrition-label">{k}</div>
                            <div className="nutrition-value">
                              {v !== undefined ? `${v}${k === 'calories' ? ' 卡' : ' g'}` : '--'}
                              {manualWeight && result.nutrition && result.estimatedWeight &&
                                <span style={{fontSize:'0.85em',color:'#888',marginLeft:6}}>
                                  (AI:{Math.round(result.nutrition[k])}{k === 'calories' ? '卡' : 'g'})
                                </span>
                              }
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="nutrition-section">
                      <h4 className="nutrition-section-title">維生素</h4>
                      <div className="nutrition-grid">
                        {result.vitamins && Object.entries(result.vitamins).map(([k,v])=>(
                          <div key={k} className="nutrition-item">
                            <div className="nutrition-label">{k}</div>
                            <div className="nutrition-value">{v} mg</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="nutrition-section">
                      <h4 className="nutrition-section-title">礦物質</h4>
                      <div className="nutrition-grid">
                        {result.minerals && Object.entries(result.minerals).map(([k,v])=>(
                          <div key={k} className="nutrition-item">
                            <div className="nutrition-label">{k}</div>
                            <div className="nutrition-value">{v} mg</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {profile && (
                    <div className="daily-recommendation">
                      <div className="recommendation-title">💡 個人化建議</div>
                      <div className="recommendation-text">
                        這份食物約佔您每日熱量建議的 {adjustedNutrition.calories && profile.dailyCalories ? Math.round((adjustedNutrition.calories / profile.dailyCalories) * 100) : '--'}%。
                        {manualWeight && result.nutrition && result.estimatedWeight &&
                          <span style={{fontSize:'0.95em',color:'#888',marginLeft:8}}>
                            (AI:{Math.round(result.nutrition.calories)}卡)
                          </span>
                        }
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* AI 輔助模式介面 */}
              {isAssistedMode && (
                <div className="assisted-mode-card">
                  <h3 className="text-lg font-bold text-yellow-600 mb-2">AI 輔助記錄模式</h3>
                  {error && <p className="text-sm text-gray-600 mb-3">{error}</p>}
                  
                  {isManualLoading && <p>查詢營養資訊中...</p>}
                  {manualError && <p className="text-sm text-red-600 mb-3">{manualError}</p>}

                  {manualNutrition && (
                    <div>
                      <p className="text-md text-gray-800 mb-4">
                        AI 建議的食物「<strong>{manualNutrition.food_name || manualFoodName}</strong>」每 100g 的營養如下：
                      </p>
                  
                  {/* --- 新增：顯示100g營養成分 --- */}
                  <div className="nutrition-grid mb-4">
                    {Object.entries(manualNutrition)
                      .filter(([key]) => !['food_name', 'chinese_name', 'error'].includes(key))
                      .map(([key, value]) => (
                      <div key={key} className="nutrition-item">
                        <span className="nutrition-label">{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                        <span className="nutrition-value">{typeof value === 'number' ? value.toFixed(1) : value} {key === 'calories' ? 'kcal' : 'g'}</span>
                      </div>
                    ))}
                  </div>

                  <div className="manual-weight-input">
                     <label className="block text-sm font-medium text-gray-700 mb-1">請輸入這份餐點的實際重量 (g):</label>
                     <input
                            type="number"
                            value={manualWeight}
                            onChange={(e) => setManualWeight(e.target.value)}
                            placeholder="例如：250"
                            className="input-field w-full"
                          />
                  </div>
                  <button onClick={addToFoodDiary} className="btn-primary mt-4">加入日記</button>
                </div>
              )}
            </div>
          )}

              {/* 完全手動模式介面 */}
              {isManualMode && (
                <div className="manual-mode-card">
                  <h3 className="text-lg font-bold text-gray-700 mb-2">手動記錄模式</h3>
                  {manualError && <p className="text-sm text-red-600 mb-3">{manualError}</p>}
                  <p className="text-sm text-gray-500 mb-4">
                    AI 無法自動辨識圖片，或辨識結果不準確？沒問題，您可以在這裡手動查詢並記錄您的餐點。
                  </p>
                  
                  <div className="manual-lookup-form">
                    <input
                      type="text"
                      value={manualFoodName}
                      onChange={(e) => setManualFoodName(e.target.value)}
                      placeholder="輸入食物名稱，例如：雞胸肉"
                      className="input-field"
                    />
                    <button onClick={handleManualLookup} disabled={isManualLoading} className="btn-secondary ml-2">
                      {isManualLoading ? '查詢中...' : <><Search className="mr-1" />查詢營養</>}
                    </button>
                  </div>

                  {manualNutrition && (
                    <div className="manual-nutrition-details">
                      <h4>營養成分</h4>
                      <div className="nutrition-grid">
                        {Object.entries(manualNutrition).map(([k,v])=>(
                          <div key={k} className="nutrition-item">
                            <div className="nutrition-label">{k}</div>
                            <div className="nutrition-value">{v} {k === 'calories' ? '卡' : 'g'}</div>
                          </div>
                        ))}
                      </div>
                      <div style={{marginTop:'0.5rem'}}>
                        <label style={{fontSize:'0.95em',color:'#185a9d'}}>如有實際秤重，請輸入：
                          <input
                            type="number"
                            min="1"
                            step="1"
                            value={manualWeight}
                            onChange={e => setManualWeight(e.target.value)}
                            style={{marginLeft:8,padding:'2px 6px',borderRadius:4,border:'1px solid #ccc',width:80}}
                            placeholder="實際重量(g)"
                          />
                          <span style={{marginLeft:4}}>g</span>
                        </label>
                      </div>
                      <button onClick={addToFoodDiary} className="btn-primary mt-3">加入飲食記錄</button>
                      <button onClick={() => setIsManualMode(false)} className="btn-secondary mt-2 ml-2">返回分析模式</button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {tab === 'profile' && (
        <form className="profile-form" onSubmit={saveProfile}>
          <div className="input-group">
            <label htmlFor="userName">姓名</label>
            <input type="text" id="userName" name="name" value={profile.name} onChange={handleProfileChange} placeholder="請輸入您的姓名" />
          </div>
          
          <div className="input-row">
            <div className="input-group">
              <label htmlFor="userAge">年齡</label>
              <input type="number" id="userAge" name="age" value={profile.age} onChange={handleProfileChange} placeholder="歲" min="1" max="120" />
            </div>
            <div className="input-group">
              <label htmlFor="userGender">性別</label>
              <select id="userGender" name="gender" value={profile.gender} onChange={handleProfileChange}>
                <option value="">請選擇</option>
                <option value="male">男性</option>
                <option value="female">女性</option>
              </select>
            </div>
          </div>
          
          <div className="input-row">
            <div className="input-group">
              <label htmlFor="userHeight">身高 (cm)</label>
              <input type="number" id="userHeight" name="height" value={profile.height} onChange={handleProfileChange} placeholder="公分" min="100" max="250" />
            </div>
            <div className="input-group">
              <label htmlFor="userWeight">體重 (kg)</label>
              <input type="number" id="userWeight" name="weight" value={profile.weight} onChange={handleProfileChange} placeholder="公斤" min="30" max="200" />
            </div>
          </div>
          
          <div className="input-group">
            <label htmlFor="activityLevel">活動量</label>
            <select id="activityLevel" name="activityLevel" value={profile.activityLevel} onChange={handleProfileChange}>
              <option value="sedentary">久坐少動 (辦公室工作)</option>
              <option value="light">輕度活動 (每週運動1-3次)</option>
              <option value="moderate">中度活動 (每週運動3-5次)</option>
              <option value="active">高度活動 (每週運動6-7次)</option>
              <option value="extra">超高活動 (體力勞動+運動)</option>
            </select>
          </div>
          
          <div className="input-group">
            <label htmlFor="healthGoal">健康目標</label>
            <select id="healthGoal" name="healthGoal" value={profile.healthGoal} onChange={handleProfileChange}>
              <option value="lose">減重</option>
              <option value="maintain">維持體重</option>
              <option value="gain">增重</option>
              <option value="muscle">增肌</option>
              <option value="health">保持健康</option>
            </select>
          </div>
          
          <button className="save-profile-btn" type="submit">💾 儲存資料</button>
          
          {profile && (
            <div className="profile-summary" style={{marginTop: '1.5rem', background: '#f5f7fa', borderRadius: '10px', padding: '1rem'}}>
              <h4>您的每日建議：</h4>
              <ul>
                <li>熱量：{profile.dailyCalories} 卡</li>
                <li>蛋白質：{profile.proteinGoal} g</li>
                <li>纖維：{profile.fiberGoal} g</li>
                <li>水分：{profile.waterGoal} ml</li>
              </ul>
            </div>
          )}
        </form>
      )}

      {tab === 'tracking' && (
        <div className="tracking-tab">
          <div className="overview-cards">
            <div className="overview-card">
              <div className="overview-label">今日攝取熱量</div>
              <div className="overview-value">{Math.round(foodDiary.reduce((t,m)=>t+(m.nutrition?.calories||0),0))} <span>卡</span></div>
            </div>
            <div className="overview-card">
              <div className="overview-label">蛋白質</div>
              <div className="overview-value">{Math.round(foodDiary.reduce((t,m)=>t+(m.nutrition?.protein||0),0))} <span>g</span></div>
            </div>
            <div className="overview-card">
              <div className="overview-label">纖維</div>
              <div className="overview-value">{Math.round(foodDiary.reduce((t,m)=>t+(m.nutrition?.fiber||0),0))} <span>g</span></div>
            </div>
          </div>
          
          <div className="progress-section">
            {[{label:'熱量',current:foodDiary.reduce((t,m)=>t+(m.nutrition?.calories||0),0),goal:profile.dailyCalories,unit:'卡',color:'#43cea2'},
              {label:'蛋白質',current:foodDiary.reduce((t,m)=>t+(m.nutrition?.protein||0),0),goal:profile.proteinGoal,unit:'g',color:'#185a9d'},
              {label:'纖維',current:foodDiary.reduce((t,m)=>t+(m.nutrition?.fiber||0),0),goal:profile.fiberGoal,unit:'g',color:'#ff9a9e'}].map(({label,current,goal,unit,color})=>{
              const percent = goal ? Math.min(100, (current/goal)*100) : 0;
              return (
                <div className="progress-row" key={label}>
                  <div className="progress-label">{label}</div>
                  <div className="progress-bar-bg">
                    <div className="progress-bar-fill" style={{width:`${percent}%`,background:color}}></div>
                  </div>
                  <div className="progress-value">{Math.round(current)} / {goal} {unit}</div>
                </div>
              );
            })}
          </div>
          
          <div className="food-diary-section">
            <div className="food-diary-title">今日食物記錄</div>
            {foodDiary.length === 0 ? (
              <div className="no-diary">今天尚未記錄任何食物 🍽️</div>
            ) : (
              <div className="food-diary-list">
                {foodDiary.map(meal => (
                  <div className="food-diary-item" key={meal.id}>
                    {editingMeal && editingMeal.id === meal.id ? (
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                          <span className="food-diary-name">{meal.foodName}</span>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <input
                                  type="number"
                                  value={editWeight}
                                  onChange={(e) => setEditWeight(e.target.value)}
                                  style={{ width: '70px', padding: '4px', border: '1px solid #ccc', borderRadius: '4px' }}
                              />
                              <span>g</span>
                              <button onClick={handleUpdateMeal} style={{ padding: '4px 8px', background: '#43cea2', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>保存</button>
                              <button onClick={cancelEditing} style={{ padding: '4px 8px', background: '#aaa', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>取消</button>
                          </div>
                      </div>
                    ) : (
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                          <div style={{ flex: 1 }}>
                              <div className="food-diary-name">{meal.foodName}</div>
                              <div style={{ fontSize: '0.8em', color: '#888' }}>{new Date(meal.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                          </div>
                          <div style={{ flex: 1, textAlign: 'center' }}>
                              <span>{Math.round(meal.estimatedWeight || 0)}g</span>
                              <span style={{ margin: '0 10px' }}>/</span>
                              <span className="food-diary-calories">{Math.round(meal.nutrition?.calories || 0)} 卡</span>
                          </div>
                          <div style={{ display: 'flex', gap: '15px' }}>
                              <button onClick={() => handleEditMeal(meal)} style={{ background: 'none', border: 'none', color: '#185a9d', cursor: 'pointer', fontSize: '0.9em' }}>修改</button>
                              <button onClick={() => deleteMeal(meal.id)} style={{ background: 'none', border: 'none', color: '#ff6b6b', cursor: 'pointer', fontSize: '0.9em' }}>刪除</button>
                          </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div className="week-chart-section">
            <div className="week-chart-title">本週熱量趨勢</div>
            <div className="week-chart-wrapper">
              <canvas ref={chartRef} width={320} height={180} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AIFoodAnalyzer;
