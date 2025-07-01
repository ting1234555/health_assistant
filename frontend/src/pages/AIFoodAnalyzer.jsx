import React, { useState, useEffect, useRef } from 'react';
import { XMarkIcon, InboxArrowDownIcon, CalendarIcon, ClockIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import Chart from 'chart.js/auto';
import './AIFoodAnalyzer.css';

export default function AIFoodAnalyzer() {
  // 應用狀態管理
  const [userProfile, setUserProfile] = useState(null);
  const [dailyMeals, setDailyMeals] = useState([]);
  const [activeTab, setActiveTab] = useState('profile');
  const [selectedImage, setSelectedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentFoodAnalysis, setCurrentFoodAnalysis] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  // 後端 API 基礎 URL
  const API_BASE_URL = 'http://localhost:8000/api';
  
  // 狀態追蹤錯誤信息
  const [error, setError] = useState(null);

  // 初始化 - 載入儲存的資料
  useEffect(() => {
    loadStoredData();
  }, []);

  // 當 tab 切換時檢查頁面狀態
  useEffect(() => {
    checkPageAccess(activeTab);
  }, [activeTab, userProfile]);

  // 初始化營養圖表
  useEffect(() => {
    if (activeTab === 'tracking' && userProfile && chartRef.current) {
      initNutritionChart();
    }
  }, [activeTab, userProfile]);

  // 載入儲存的資料
  const loadStoredData = () => {
    try {
      const storedProfile = localStorage.getItem('userProfile');
      const storedMeals = localStorage.getItem('dailyMeals');
      
      if (storedProfile) {
        setUserProfile(JSON.parse(storedProfile));
      }
      
      if (storedMeals) {
        setDailyMeals(JSON.parse(storedMeals));
      }
    } catch (error) {
      console.error('Error loading stored data:', error);
    }
  };

  // 檢查頁面訪問權限
  const checkPageAccess = (tabId) => {
    if (tabId === 'analyze') {
      if (userProfile) {
        initCamera();
      }
    } else if (tabId === 'tracking' && userProfile) {
      updateTrackingStats();
    }
  };

  // 初始化相機
  const initCamera = async () => {
    try {
      if (videoRef.current && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoRef.current.srcObject = stream;
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
    }
  };

  // 拍照功能
  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const context = canvasRef.current.getContext('2d');
      canvasRef.current.width = videoRef.current.videoWidth;
      canvasRef.current.height = videoRef.current.videoHeight;
      context.drawImage(videoRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);
      
      const imageData = canvasRef.current.toDataURL('image/png');
      setSelectedImage(imageData);
      analyzeImage(imageData);
    }
  };

  // 處理檔案上傳
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result);
        analyzeImage(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  // 分析圖片
  const analyzeImage = async (imageData) => {
    setIsAnalyzing(true);
    setError(null);
    
    try {
      // 將 base64 圖片數據轉換為 Blob
      const base64Response = await fetch(imageData);
      const blob = await base64Response.blob();
      
      // 創建 FormData 並添加圖片
      const formData = new FormData();
      formData.append('file', blob, 'food-image.jpg');
      
      // 發送到後端 API
      const response = await fetch(`${API_BASE_URL}/recognize-food`, {
        method: 'POST',
        body: formData,
        // 注意：不要手動設置 Content-Type，讓瀏覽器自動設置並添加 boundary
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || '分析圖片時發生錯誤');
      }
      
      const data = await response.json();
      
      setCurrentFoodAnalysis({
        name: data.food_name,
        nutrition: data.nutrition || {},
        timestamp: new Date().toISOString()
      });
      
      // 如果後端返回了營養分析，也更新追蹤數據
      if (data.nutrition) {
        addMealToTracker(data.food_name, data.nutrition);
      }
      
    } catch (err) {
      console.error('分析圖片時出錯:', err);
      setError(err.message || '分析失敗，請重試！');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 儲存個人資料
  const saveProfile = () => {
    const name = document.getElementById('userName').value;
    const age = parseInt(document.getElementById('userAge').value);
    const gender = document.getElementById('userGender').value;
    const height = parseInt(document.getElementById('userHeight').value);
    const weight = parseInt(document.getElementById('userWeight').value);
    const activityLevel = document.getElementById('activityLevel').value;
    const healthGoal = document.getElementById('healthGoal').value;
    
    // 驗證必填欄位
    if (!name || !age || !gender || !height || !weight || !activityLevel || !healthGoal) {
      alert('請填寫所有欄位！');
      return;
    }
    
    const profile = {
      name,
      age,
      gender,
      height,
      weight,
      activityLevel,
      healthGoal
    };
    
    // 計算基礎代謝率 (BMR) 和每日熱量需求
    profile.bmr = calculateBMR(profile);
    profile.dailyCalories = calculateDailyCalories(profile);
    profile.bmi = (profile.weight / Math.pow(profile.height / 100, 2)).toFixed(1);
    
    setUserProfile(profile);
    
    // 儲存到 localStorage
    localStorage.setItem('userProfile', JSON.stringify(profile));
    localStorage.setItem('dailyMeals', JSON.stringify([])); // 重置每日記錄
    setDailyMeals([]);
    
    alert('個人資料已儲存成功！✅');
    
    // 切換到分析頁面
    setActiveTab('analyze');
  };

  // 計算基礎代謝率 (BMR)
  const calculateBMR = (profile) => {
    let bmr;
    if (profile.gender === 'male') {
      bmr = 88.362 + (13.397 * profile.weight) + (4.799 * profile.height) - (5.677 * profile.age);
    } else {
      bmr = 447.593 + (9.247 * profile.weight) + (3.098 * profile.height) - (4.330 * profile.age);
    }
    return Math.round(bmr);
  };

  // 計算每日熱量需求
  const calculateDailyCalories = (profile) => {
    const activityMultipliers = {
      sedentary: 1.2,
      light: 1.375,
      moderate: 1.55,
      active: 1.725,
      extra: 1.9
    };
    
    let calories = profile.bmr * activityMultipliers[profile.activityLevel];
    
    // 根據健康目標調整
    if (profile.healthGoal === 'lose') {
      calories -= 300; // 減重
    } else if (profile.healthGoal === 'gain') {
      calories += 300; // 增重
    }
    
    return Math.round(calories);
  };

  // 顯示營養資訊
  const displayNutrition = (foodName, nutrition) => {
    return (
      <div className="result">
        <div className="food-info">
          <div className="food-name">{foodName} (每100g)</div>
          <button className="add-to-diary" onClick={addToDiary}>+ 加入記錄</button>
        </div>
        <div className="nutrition-grid">
          <div className="nutrition-item">
            <div className="nutrition-label">熱量</div>
            <div className="nutrition-value">{nutrition.calories} 卡</div>
          </div>
          <div className="nutrition-item">
            <div className="nutrition-label">蛋白質</div>
            <div className="nutrition-value">{nutrition.protein} g</div>
          </div>
          <div className="nutrition-item">
            <div className="nutrition-label">碳水化合物</div>
            <div className="nutrition-value">{nutrition.carbs} g</div>
          </div>
          <div className="nutrition-item">
            <div className="nutrition-label">脂肪</div>
            <div className="nutrition-value">{nutrition.fat} g</div>
          </div>
          <div className="nutrition-item">
            <div className="nutrition-label">纖維</div>
            <div className="nutrition-value">{nutrition.fiber} g</div>
          </div>
          <div className="nutrition-item">
            <div className="nutrition-label">糖分</div>
            <div className="nutrition-value">{nutrition.sugar} g</div>
          </div>
        </div>
        <div className="daily-recommendation">
          <div className="recommendation-title">💡 個人化建議</div>
          <div className="recommendation-text">
            {getPersonalizedRecommendation(nutrition)}
          </div>
        </div>
      </div>
    );
  };

  // 獲取個人化建議
  const getPersonalizedRecommendation = (nutrition) => {
    if (!userProfile) return '';
    
    const dailyCaloriesNeeded = userProfile.dailyCalories;
    const caloriePercentage = ((nutrition.calories / dailyCaloriesNeeded) * 100).toFixed(1);
    
    let recommendationText = `這份食物提供您每日所需熱量的 ${caloriePercentage}%。`;
    
    if (userProfile.healthGoal === 'lose' && nutrition.calories > 200) {
      recommendationText += ' 由於您的目標是減重，建議控制份量或搭配蔬菜一起食用。';
    } else if (userProfile.healthGoal === 'muscle' && nutrition.protein < 10) {
      recommendationText += ' 建議搭配高蛋白食物，有助於肌肉成長。';
    } else if (nutrition.fiber > 3) {
      recommendationText += ' 富含纖維，對消化健康很有幫助！';
    }
    
    return recommendationText;
  };

  // 加入飲食記錄
  const addToDiary = () => {
    if (currentFoodAnalysis) {
      const newMeals = [...dailyMeals, {
        ...currentFoodAnalysis,
        id: Date.now()
      }];
      
      setDailyMeals(newMeals);
      localStorage.setItem('dailyMeals', JSON.stringify(newMeals));
      alert('已加入今日飲食記錄！✅');
      
      // 更新統計
      updateTrackingStats();
    }
  };

  // 更新追蹤統計
  const updateTrackingStats = () => {
    // 計算今日總熱量
    const todayCalories = dailyMeals.reduce((total, meal) => {
      return total + meal.nutrition.calories;
    }, 0);
    
    // 模擬週平均
    const weeklyAvg = Math.round(todayCalories * (0.8 + Math.random() * 0.4));
    
    // 更新 DOM
    const todayCaloriesElement = document.getElementById('todayCalories');
    const weeklyAvgElement = document.getElementById('weeklyAvg');
    
    if (todayCaloriesElement) todayCaloriesElement.textContent = todayCalories;
    if (weeklyAvgElement) weeklyAvgElement.textContent = weeklyAvg;
    
    // 更新餐點列表
    updateMealsList();
  };

  // 更新餐點列表
  const updateMealsList = () => {
    const mealsListElement = document.getElementById('mealsList');
    
    if (mealsListElement) {
      if (dailyMeals.length === 0) {
        mealsListElement.innerHTML = `
          <div class="meal-item">
            <div class="meal-info">
              <h4>尚無飲食記錄</h4>
              <span>開始分析食物來建立您的飲食記錄吧！</span>
            </div>
          </div>
        `;
      } else {
        mealsListElement.innerHTML = dailyMeals.map(meal => `
          <div class="meal-item">
            <div class="meal-info">
              <h4>${meal.name}</h4>
              <span>${new Date(meal.timestamp).toLocaleTimeString()}</span>
            </div>
            <div class="meal-calories">${meal.nutrition.calories} 卡</div>
          </div>
        `).join('');
      }
    }
  };

  // 初始化營養圖表
  const initNutritionChart = () => {
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }
    
    const ctx = chartRef.current.getContext('2d');
    
    // 模擬一週的數據
    const days = ['週一', '週二', '週三', '週四', '週五', '週六', '週日'];
    const caloriesData = Array(7).fill(0).map(() => Math.floor(Math.random() * 1000 + 1000));
    const proteinData = Array(7).fill(0).map(() => Math.floor(Math.random() * 30 + 50));
    const carbsData = Array(7).fill(0).map(() => Math.floor(Math.random() * 50 + 150));
    
    // 今天的數據
    const today = new Date().getDay() || 7; // 0 是週日，轉換為 7
    caloriesData[today - 1] = dailyMeals.reduce((total, meal) => total + meal.nutrition.calories, 0) || 
                             Math.floor(Math.random() * 1000 + 1000);
    
    chartInstance.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels: days,
        datasets: [
          {
            label: '熱量 (卡)',
            data: caloriesData,
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            tension: 0.3
          },
          {
            label: '蛋白質 (g)',
            data: proteinData,
            borderColor: 'rgb(54, 162, 235)',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            tension: 0.3
          },
          {
            label: '碳水 (g)',
            data: carbsData,
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          tooltip: {
            mode: 'index',
            intersect: false,
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  };

  // 獲取 BMI 狀態
  const getBMIStatus = (bmi) => {
    if (bmi < 18.5) return '體重過輕';
    if (bmi < 24) return '正常範圍';
    if (bmi < 27) return '體重過重';
    if (bmi < 30) return '輕度肥胖';
    if (bmi < 35) return '中度肥胖';
    return '重度肥胖';
  };

  // 更新歡迎訊息
  const updateWelcomeMessage = () => {
    if (!userProfile) return '';
    
    const bmiStatus = getBMIStatus(userProfile.bmi);
    return (
      <div className="welcome-message">
        <h3>👋 你好，{userProfile.name}！</h3>
        <p>BMI: {userProfile.bmi} ({bmiStatus}) | 每日建議熱量: {userProfile.dailyCalories} 卡</p>
      </div>
    );
  };

  return (
    <div className="app-container">
      <div className="header">
        <h1 className="title">🍎 AI營養分析器</h1>
        <p className="subtitle">個人化健康管理助手</p>
      </div>
      
      <nav className="tab-nav">
        <button 
          className={`tab-btn ${activeTab === 'profile' ? 'active' : ''}`} 
          onClick={() => setActiveTab('profile')}
        >
          👤 個人資料
        </button>
        <button 
          className={`tab-btn ${activeTab === 'analyze' ? 'active' : ''}`} 
          onClick={() => setActiveTab('analyze')}
        >
          📸 食物分析
        </button>
        <button 
          className={`tab-btn ${activeTab === 'tracking' ? 'active' : ''}`} 
          onClick={() => setActiveTab('tracking')}
        >
          📊 追蹤記錄
        </button>
      </nav>
      
      {/* 個人資料頁面 */}
      <div className={`tab-content ${activeTab === 'profile' ? 'active' : ''}`} id="profile">
        <div className="profile-form">
          <div className="input-group">
            <label htmlFor="userName">姓名</label>
            <input type="text" id="userName" placeholder="請輸入您的姓名" defaultValue={userProfile?.name || ''} />
          </div>
          
          <div className="input-row">
            <div className="input-group">
              <label htmlFor="userAge">年齡</label>
              <input type="number" id="userAge" placeholder="歲" min="1" max="120" defaultValue={userProfile?.age || ''} />
            </div>
            <div className="input-group">
              <label htmlFor="userGender">性別</label>
              <select id="userGender" defaultValue={userProfile?.gender || ''}>
                <option value="">請選擇</option>
                <option value="male">男性</option>
                <option value="female">女性</option>
              </select>
            </div>
          </div>
          
          <div className="input-row">
            <div className="input-group">
              <label htmlFor="userHeight">身高 (cm)</label>
              <input type="number" id="userHeight" placeholder="公分" min="100" max="250" defaultValue={userProfile?.height || ''} />
            </div>
            <div className="input-group">
              <label htmlFor="userWeight">體重 (kg)</label>
              <input type="number" id="userWeight" placeholder="公斤" min="30" max="200" defaultValue={userProfile?.weight || ''} />
            </div>
          </div>
          
          <div className="input-group">
            <label htmlFor="activityLevel">活動量</label>
            <select id="activityLevel" defaultValue={userProfile?.activityLevel || ''}>
              <option value="">請選擇活動量</option>
              <option value="sedentary">久坐少動 (辦公室工作)</option>
              <option value="light">輕度活動 (每週運動1-3次)</option>
              <option value="moderate">中度活動 (每週運動3-5次)</option>
              <option value="active">高度活動 (每週運動6-7次)</option>
              <option value="extra">超高活動 (體力勞動+運動)</option>
            </select>
          </div>
          
          <div className="input-group">
            <label htmlFor="healthGoal">健康目標</label>
            <select id="healthGoal" defaultValue={userProfile?.healthGoal || ''}>
              <option value="">請選擇目標</option>
              <option value="lose">減重</option>
              <option value="maintain">維持體重</option>
              <option value="gain">增重</option>
              <option value="muscle">增肌</option>
              <option value="health">保持健康</option>
            </select>
          </div>
          
          <button className="save-profile-btn" onClick={saveProfile}>💾 儲存個人資料</button>
        </div>
      </div>
      
      {/* 食物分析頁面 */}
      <div className={`tab-content ${activeTab === 'analyze' ? 'active' : ''}`} id="analyze">
        {!userProfile ? (
          <div className="no-profile">
            <p>請先完成個人資料設定，以獲得個人化營養建議 👆</p>
          </div>
        ) : (
          <div>
            <div className="camera-container">
              <video ref={videoRef} id="video" autoPlay playsInline></video>
              <canvas ref={canvasRef} id="canvas"></canvas>
            </div>
            
            <div className="controls">
              <button id="captureBtn" onClick={captureImage}>📸 拍照</button>
              <input 
                type="file" 
                id="fileInput" 
                className="file-input" 
                accept="image/*" 
                onChange={handleFileUpload}
              />
              <button 
                id="uploadBtn" 
                className="upload-btn" 
                onClick={() => document.getElementById('fileInput').click()}
              >
                📁 上傳
              </button>
            </div>
            
            {isAnalyzing && (
              <div className="loading" style={{ display: 'block' }}>
                <div className="spinner"></div>
                <p>AI正在分析食物...</p>
              </div>
            )}
            
            {error && !isAnalyzing && (
              <div className="error-message" style={{ 
                backgroundColor: '#ffebee',
                color: '#c62828',
                padding: '15px',
                borderRadius: '8px',
                margin: '20px 0',
                borderLeft: '4px solid #ef5350',
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
              }}>
                <span style={{ fontSize: '20px' }}>⚠️</span>
                <div>
                  <strong>錯誤：</strong>
                  <p style={{ margin: '5px 0 0 0' }}>{error}</p>
                </div>
              </div>
            )}
            
            {currentFoodAnalysis && !isAnalyzing && (
              displayNutrition(currentFoodAnalysis.name, currentFoodAnalysis.nutrition)
            )}
          </div>
        )}
      </div>
      
      {/* 追蹤記錄頁面 */}
      <div className={`tab-content ${activeTab === 'tracking' ? 'active' : ''}`} id="tracking">
        {!userProfile ? (
          <div className="no-profile">
            <p>請先完成個人資料設定，開始追蹤您的營養攝取 👆</p>
          </div>
        ) : (
          <div>
            {updateWelcomeMessage()}
            
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-number" id="todayCalories">
                  {dailyMeals.reduce((total, meal) => total + meal.nutrition.calories, 0)}
                </div>
                <div className="stat-label">今日熱量</div>
              </div>
              <div className="stat-card">
                <div className="stat-number" id="weeklyAvg">
                  {Math.round(dailyMeals.reduce((total, meal) => total + meal.nutrition.calories, 0) * (0.8 + Math.random() * 0.4)) || 0}
                </div>
                <div className="stat-label">週平均</div>
              </div>
            </div>
            
            <div className="chart-container">
              <h3 style={{ marginBottom: '1rem', color: '#333' }}>本週營養攝取趨勢</h3>
              <canvas ref={chartRef} id="nutritionChart" width="400" height="200"></canvas>
            </div>
            
            <div className="today-meals">
              <h3 style={{ marginBottom: '1rem', color: '#333' }}>今日飲食記錄</h3>
              <div id="mealsList">
                {dailyMeals.length === 0 ? (
                  <div className="meal-item">
                    <div className="meal-info">
                      <h4>尚無飲食記錄</h4>
                      <span>開始分析食物來建立您的飲食記錄吧！</span>
                    </div>
                  </div>
                ) : (
                  dailyMeals.map(meal => (
                    <div className="meal-item" key={meal.id}>
                      <div className="meal-info">
                        <h4>{meal.name}</h4>
                        <span>{new Date(meal.timestamp).toLocaleTimeString()}</span>
                      </div>
                      <div className="meal-calories">{meal.nutrition.calories} 卡</div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
