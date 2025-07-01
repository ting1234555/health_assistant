import React, { useState, useEffect, useRef } from 'react';
import { XMarkIcon, InboxArrowDownIcon, CalendarIcon, ClockIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import Chart from 'chart.js/auto';
import './AIFoodAnalyzer.css';

const AIFoodAnalyzer = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const [userProfile, setUserProfile] = useState({
    name: '',
    age: '',
    gender: '',
    weight: '',
    height: '',
    activityLevel: 'moderate',
    goal: 'maintain'
  });
  const [foodLog, setFoodLog] = useState([]);
  const [nutritionGoals, setNutritionGoals] = useState({
    calories: 2000,
    protein: 150,
    carbs: 250,
    fat: 65,
    fiber: 25
  });
  const [currentNutrition, setCurrentNutrition] = useState({
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0,
    fiber: 0
  });

  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    // 載入本地儲存的資料
    const savedProfile = localStorage.getItem('userProfile');
    const savedFoodLog = localStorage.getItem('foodLog');
    const savedNutrition = localStorage.getItem('currentNutrition');

    if (savedProfile) {
      setUserProfile(JSON.parse(savedProfile));
    }
    if (savedFoodLog) {
      setFoodLog(JSON.parse(savedFoodLog));
    }
    if (savedNutrition) {
      setCurrentNutrition(JSON.parse(savedNutrition));
    }
  }, []);

  useEffect(() => {
    // 儲存資料到本地儲存
    localStorage.setItem('userProfile', JSON.stringify(userProfile));
    localStorage.setItem('foodLog', JSON.stringify(foodLog));
    localStorage.setItem('currentNutrition', JSON.stringify(currentNutrition));
  }, [userProfile, foodLog, currentNutrition]);

  useEffect(() => {
    if (activeTab === 'tracking' && chartRef.current) {
      createChart();
    }
  }, [activeTab, currentNutrition]);

  const createChart = () => {
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    chartInstance.current = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['蛋白質', '碳水化合物', '脂肪'],
        datasets: [{
          data: [currentNutrition.protein, currentNutrition.carbs, currentNutrition.fat],
          backgroundColor: ['#3498db', '#e74c3c', '#f39c12'],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    });
  };

  const handleProfileChange = (field, value) => {
    setUserProfile(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addFoodItem = (food) => {
    const newFoodLog = [...foodLog, {
      ...food,
      id: Date.now(),
      timestamp: new Date().toISOString()
    }];
    setFoodLog(newFoodLog);

    // 更新營養攝取
    setCurrentNutrition(prev => ({
      calories: prev.calories + (food.calories || 0),
      protein: prev.protein + (food.protein || 0),
      carbs: prev.carbs + (food.carbs || 0),
      fat: prev.fat + (food.fat || 0),
      fiber: prev.fiber + (food.fiber || 0)
    }));
  };

  const removeFoodItem = (id) => {
    const foodToRemove = foodLog.find(food => food.id === id);
    if (foodToRemove) {
      setCurrentNutrition(prev => ({
        calories: prev.calories - (foodToRemove.calories || 0),
        protein: prev.protein - (foodToRemove.protein || 0),
        carbs: prev.carbs - (foodToRemove.carbs || 0),
        fat: prev.fat - (foodToRemove.fat || 0),
        fiber: prev.fiber - (foodToRemove.fiber || 0)
      }));
    }
    setFoodLog(prev => prev.filter(food => food.id !== id));
  };

  const calculateProgress = (current, goal) => {
    return Math.min((current / goal) * 100, 100);
  };

  const getProgressColor = (current, goal) => {
    const percentage = (current / goal) * 100;
    if (percentage >= 100) return '#e74c3c';
    if (percentage >= 80) return '#f39c12';
    return '#27ae60';
  };

  return (
    <div className="ai-food-analyzer">
      <div className="container">
        <header className="header">
          <h1>AI食物營養分析器</h1>
          <p>個人化健康管理系統</p>
        </header>

        <nav className="tabs">
          <button 
            className={`tab ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            個人資料
          </button>
          <button 
            className={`tab ${activeTab === 'analysis' ? 'active' : ''}`}
            onClick={() => setActiveTab('analysis')}
          >
            食物分析
          </button>
          <button 
            className={`tab ${activeTab === 'tracking' ? 'active' : ''}`}
            onClick={() => setActiveTab('tracking')}
          >
            營養追蹤
          </button>
        </nav>

        <main className="content">
          {activeTab === 'profile' && (
            <div className="profile-section">
              <h2>個人資料設定</h2>
              <div className="profile-form">
                <div className="form-group">
                  <label>姓名</label>
                  <input
                    type="text"
                    value={userProfile.name}
                    onChange={(e) => handleProfileChange('name', e.target.value)}
                    placeholder="請輸入您的姓名"
                  />
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>年齡</label>
                    <input
                      type="number"
                      value={userProfile.age}
                      onChange={(e) => handleProfileChange('age', e.target.value)}
                      placeholder="歲"
                    />
                  </div>
                  <div className="form-group">
                    <label>性別</label>
                    <select
                      value={userProfile.gender}
                      onChange={(e) => handleProfileChange('gender', e.target.value)}
                    >
                      <option value="">請選擇</option>
                      <option value="male">男性</option>
                      <option value="female">女性</option>
                    </select>
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>體重 (kg)</label>
                    <input
                      type="number"
                      value={userProfile.weight}
                      onChange={(e) => handleProfileChange('weight', e.target.value)}
                      placeholder="公斤"
                    />
                  </div>
                  <div className="form-group">
                    <label>身高 (cm)</label>
                    <input
                      type="number"
                      value={userProfile.height}
                      onChange={(e) => handleProfileChange('height', e.target.value)}
                      placeholder="公分"
                    />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>活動量</label>
                    <select
                      value={userProfile.activityLevel}
                      onChange={(e) => handleProfileChange('activityLevel', e.target.value)}
                    >
                      <option value="sedentary">久坐不動</option>
                      <option value="light">輕度活動</option>
                      <option value="moderate">中度活動</option>
                      <option value="active">高度活動</option>
                      <option value="very_active">極度活動</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>目標</label>
                    <select
                      value={userProfile.goal}
                      onChange={(e) => handleProfileChange('goal', e.target.value)}
                    >
                      <option value="lose">減重</option>
                      <option value="maintain">維持體重</option>
                      <option value="gain">增重</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'analysis' && (
            <div className="analysis-section">
              <h2>食物營養分析</h2>
              <div className="analysis-content">
                <div className="upload-area">
                  <h3>上傳食物照片</h3>
                  <p>支援 JPG、PNG 格式，最大 5MB</p>
                  <input type="file" accept="image/*" />
                  <button className="analyze-btn">開始分析</button>
                </div>
                <div className="manual-input">
                  <h3>手動輸入食物</h3>
                  <div className="food-input">
                    <input type="text" placeholder="輸入食物名稱" />
                    <button className="search-btn">搜尋</button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'tracking' && (
            <div className="tracking-section">
              <h2>營養追蹤</h2>
              
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-icon">🔥</div>
                  <div className="stat-info">
                    <div className="stat-value">{currentNutrition.calories}</div>
                    <div className="stat-label">卡路里</div>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">💪</div>
                  <div className="stat-info">
                    <div className="stat-value">{currentNutrition.protein}g</div>
                    <div className="stat-label">蛋白質</div>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">🍞</div>
                  <div className="stat-info">
                    <div className="stat-value">{currentNutrition.carbs}g</div>
                    <div className="stat-label">碳水化合物</div>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">🥑</div>
                  <div className="stat-info">
                    <div className="stat-value">{currentNutrition.fat}g</div>
                    <div className="stat-label">脂肪</div>
                  </div>
                </div>
              </div>

              <div className="chart-card">
                <div className="chart-header">
                  <h3>營養分配</h3>
                </div>
                <div style={{ height: '300px' }}>
                  <canvas ref={chartRef}></canvas>
                </div>
              </div>

              <div className="chart-card">
                <div className="chart-header">
                  <h3>營養進度</h3>
                </div>
                <div className="progress-bars">
                  <div className="progress-item">
                    <div className="progress-header">
                      <span className="progress-label">卡路里</span>
                      <span className="progress-value">{currentNutrition.calories} / {nutritionGoals.calories}</span>
                    </div>
                    <div className="progress-bar-container">
                      <div 
                        className="progress-bar-fill"
                        style={{
                          width: `${calculateProgress(currentNutrition.calories, nutritionGoals.calories)}%`,
                          backgroundColor: getProgressColor(currentNutrition.calories, nutritionGoals.calories)
                        }}
                      ></div>
                    </div>
                  </div>
                  <div className="progress-item">
                    <div className="progress-header">
                      <span className="progress-label">蛋白質</span>
                      <span className="progress-value">{currentNutrition.protein}g / {nutritionGoals.protein}g</span>
                    </div>
                    <div className="progress-bar-container">
                      <div 
                        className="progress-bar-fill"
                        style={{
                          width: `${calculateProgress(currentNutrition.protein, nutritionGoals.protein)}%`,
                          backgroundColor: getProgressColor(currentNutrition.protein, nutritionGoals.protein)
                        }}
                      ></div>
                    </div>
                  </div>
                  <div className="progress-item">
                    <div className="progress-header">
                      <span className="progress-label">碳水化合物</span>
                      <span className="progress-value">{currentNutrition.carbs}g / {nutritionGoals.carbs}g</span>
                    </div>
                    <div className="progress-bar-container">
                      <div 
                        className="progress-bar-fill"
                        style={{
                          width: `${calculateProgress(currentNutrition.carbs, nutritionGoals.carbs)}%`,
                          backgroundColor: getProgressColor(currentNutrition.carbs, nutritionGoals.carbs)
                        }}
                      ></div>
                    </div>
                  </div>
                  <div className="progress-item">
                    <div className="progress-header">
                      <span className="progress-label">脂肪</span>
                      <span className="progress-value">{currentNutrition.fat}g / {nutritionGoals.fat}g</span>
                    </div>
                    <div className="progress-bar-container">
                      <div 
                        className="progress-bar-fill"
                        style={{
                          width: `${calculateProgress(currentNutrition.fat, nutritionGoals.fat)}%`,
                          backgroundColor: getProgressColor(currentNutrition.fat, nutritionGoals.fat)
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="meals-card">
                <div className="meals-header">
                  <h3>今日食物記錄</h3>
                  <button className="btn-small">+ 新增食物</button>
                </div>
                <div className="meals-list">
                  {foodLog.length === 0 ? (
                    <div className="empty-state">
                      <div className="empty-icon">🍽️</div>
                      <p>還沒有記錄任何食物</p>
                      <p>點擊「新增食物」開始記錄您的飲食</p>
                    </div>
                  ) : (
                    foodLog.map(food => (
                      <div key={food.id} className="food-item">
                        <div className="food-info">
                          <h4>{food.name}</h4>
                          <p>{food.calories} 卡路里</p>
                        </div>
                        <button 
                          className="remove-btn"
                          onClick={() => removeFoodItem(food.id)}
                        >
                          ✕
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default AIFoodAnalyzer;
