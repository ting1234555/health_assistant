import React, { useState, useRef, useEffect } from 'react';
import { XMarkIcon, InboxArrowDownIcon, CalendarIcon, ClockIcon, ChartBarIcon, CameraIcon, PhotoIcon } from '@heroicons/react/24/outline';
import axios from 'axios';
import Chart from 'chart.js/auto';

export default function FoodTracker() {
  // 狀態管理
  const [activeTab, setActiveTab] = useState('analyzer');
  const [selectedImage, setSelectedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  // 個人資料狀態
  const [userProfile, setUserProfile] = useState({
    name: '',
    age: '',
    gender: '',
    weight: '',
    height: '',
    activityLevel: 'moderate',
    goal: 'maintain',
    dailyCalories: 2000,
    proteinGoal: 150,
    fiberGoal: 25
  });
  
  // 食物記錄狀態
  const [foodDiary, setFoodDiary] = useState([]);
  const [nutritionSummary, setNutritionSummary] = useState(null);
  const [recentMeals, setRecentMeals] = useState([]);
  
  // 相機相關
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  // 初始化
  useEffect(() => {
    loadStoredData();
    if (activeTab === 'tracking') {
      updateTrackingPage();
    }
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === 'tracking' && chartRef.current) {
      renderWeeklyChart();
    }
  }, [activeTab, foodDiary]);

  // 載入儲存的資料
  const loadStoredData = () => {
    try {
      const storedProfile = localStorage.getItem('userProfile');
      const storedDiary = localStorage.getItem('foodDiary');
      
      if (storedProfile) {
        setUserProfile(JSON.parse(storedProfile));
      }
      
      if (storedDiary) {
        setFoodDiary(JSON.parse(storedDiary));
      }
    } catch (error) {
      console.error('Error loading stored data:', error);
    }
  };

  // 儲存資料
  const saveData = () => {
    localStorage.setItem('userProfile', JSON.stringify(userProfile));
    localStorage.setItem('foodDiary', JSON.stringify(foodDiary));
  };

  useEffect(() => {
    saveData();
  }, [userProfile, foodDiary]);

  // 相機功能
  const startCamera = async () => {
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      alert('無法存取相機，請檢查權限設定');
    }
  };

  const capturePhoto = () => {
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

  // 檔案上傳處理
  const handleDrop = async (event) => {
    event.preventDefault();
    setIsDragging(false);
    if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
      await handleImageUpload({ target: { files: event.dataTransfer.files } });
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result);
      };
      reader.readAsDataURL(file);
      analyzeImage(reader.result);
    }
  };

  // 圖片分析
  const analyzeImage = async (imageData) => {
      setIsAnalyzing(true);
      try {
      // 將 base64 圖片數據轉換為 Blob
      const base64Response = await fetch(imageData);
      const blob = await base64Response.blob();
      
      // 創建 FormData 並添加圖片
        const formData = new FormData();
      formData.append('file', blob, 'food-image.jpg');

      // 發送到後端 API
      const response = await fetch('http://localhost:8000/api/ai/analyze-food-image/', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('分析請求失敗');
        }

        const data = await response.json();

      // 模擬詳細的分析結果
      const mockAnalysis = {
        foodName: data.food_name,
        description: `這是 ${data.food_name}，富含營養價值`,
        healthIndex: 75,
        glycemicIndex: 50,
        benefits: ['富含維生素', '低熱量', '高纖維'],
        nutrition: {
          calories: 150,
          protein: 8,
          carbs: 20,
          fat: 5,
          fiber: 3,
          sugar: 2
        },
        vitamins: {
          '維生素C': 25,
          '維生素A': 15
        },
        minerals: {
          '鈣': 50,
          '鐵': 2
        }
      };
      
      setAnalysisResults(mockAnalysis);
      
      } catch (error) {
        console.error('Error analyzing image:', error);
      alert('圖片分析失敗，請稍後再試');
      } finally {
        setIsAnalyzing(false);
      }
  };

  // 個人資料處理
  const handleProfileChange = (field, value) => {
    setUserProfile(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const saveProfile = () => {
    if (!userProfile.name || !userProfile.age || !userProfile.gender || !userProfile.height || !userProfile.weight) {
      alert('請填寫所有必填欄位！');
      return;
    }
    
    // 計算基礎代謝率和每日熱量需求
    const bmr = calculateBMR(userProfile);
    const dailyCalories = calculateDailyCalories(userProfile);
    
    const updatedProfile = {
      ...userProfile,
      bmr,
      dailyCalories,
      bmi: (userProfile.weight / Math.pow(userProfile.height / 100, 2)).toFixed(1)
    };
    
    setUserProfile(updatedProfile);
    alert('個人資料已儲存成功！✅');
    setActiveTab('analyzer');
  };

  const calculateBMR = (profile) => {
    let bmr;
    if (profile.gender === 'male') {
      bmr = 88.362 + (13.397 * profile.weight) + (4.799 * profile.height) - (5.677 * profile.age);
    } else {
      bmr = 447.593 + (9.247 * profile.weight) + (3.098 * profile.height) - (4.330 * profile.age);
    }
    return Math.round(bmr);
  };

  const calculateDailyCalories = (profile) => {
    const activityMultipliers = {
      sedentary: 1.2,
      light: 1.375,
      moderate: 1.55,
      active: 1.725,
      extra: 1.9
    };
    
    let calories = profile.bmr * activityMultipliers[profile.activityLevel];
    
    if (profile.goal === 'lose') {
      calories -= 300;
    } else if (profile.goal === 'gain') {
      calories += 300;
    }
    
    return Math.round(calories);
  };

  // 食物記錄功能
  const addToFoodDiary = () => {
    if (!analysisResults) {
      alert('沒有可加入的分析結果。');
      return;
    }
    
    const meal = {
      ...analysisResults,
      id: Date.now(),
      timestamp: new Date().toISOString()
    };
    
    setFoodDiary(prev => [...prev, meal]);
    alert(`${meal.foodName} 已加入記錄！`);
    setAnalysisResults(null);
    setSelectedImage(null);
  };

  // 追蹤頁面更新
  const updateTrackingPage = () => {
    if (!userProfile.name) return;
    
    const todayTotals = foodDiary.reduce((totals, meal) => {
      totals.calories += meal.nutrition.calories || 0;
      totals.protein += meal.nutrition.protein || 0;
      totals.fiber += meal.nutrition.fiber || 0;
      return totals;
    }, { calories: 0, protein: 0, fiber: 0 });
    
    setNutritionSummary(todayTotals);
  };

  // 圖表渲染
  const renderWeeklyChart = () => {
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    
    // 模擬一週的數據
    const days = ['週一', '週二', '週三', '週四', '週五', '週六', '週日'];
    const caloriesData = Array(7).fill(0).map(() => Math.floor(Math.random() * 1000 + 1000));
    
    // 今天的數據
    const today = new Date().getDay() || 7;
    caloriesData[today - 1] = foodDiary.reduce((total, meal) => total + (meal.nutrition.calories || 0), 0) || 
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
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
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

  // 通知功能
  const showNotification = (message, type = 'info') => {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 12px 20px;
      margin-bottom: 10px;
      border-radius: 4px;
      color: white;
      opacity: 0;
      transition: opacity 0.3s ease-in-out;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
      z-index: 1000;
      background-color: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#F44336' : type === 'warning' ? '#FF9800' : '#2196F3'};
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.opacity = '1';
    }, 10);
    
    setTimeout(() => {
      notification.style.opacity = '0';
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500 py-6">
      <div className="max-w-6xl mx-auto px-4">
        {/* 標題 */}
        <div className="text-center text-white mb-8">
          <h1 className="text-4xl font-bold mb-2">🍎 AI食物營養分析器</h1>
          <p className="text-xl opacity-90">智能分析您的飲食營養</p>
        </div>

        {/* 標籤導航 */}
        <div className="bg-white rounded-xl p-2 mb-8 shadow-lg">
          <div className="flex space-x-2">
            <button
              className={`flex-1 py-3 px-6 rounded-lg font-medium transition-all ${
                activeTab === 'analyzer'
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
              }`}
              onClick={() => setActiveTab('analyzer')}
            >
              分析食物
            </button>
            <button
              className={`flex-1 py-3 px-6 rounded-lg font-medium transition-all ${
                activeTab === 'profile'
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
              }`}
              onClick={() => setActiveTab('profile')}
            >
              個人資料
            </button>
            <button
              className={`flex-1 py-3 px-6 rounded-lg font-medium transition-all ${
                activeTab === 'tracking'
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
              }`}
              onClick={() => setActiveTab('tracking')}
            >
              營養追蹤
            </button>
          </div>
        </div>

        {/* 內容區域 */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {/* 食物分析頁面 */}
          {activeTab === 'analyzer' && (
            <div className="p-8">
              {!userProfile.name && (
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
                  <p className="text-yellow-700">
                    請先到「個人資料」頁面完成設定，以獲得個人化營養建議和追蹤功能 👆
                  </p>
                </div>
              )}

              <div className="max-w-4xl mx-auto">
                {/* 相機區域 */}
                <div className="mb-8">
                  <div className="bg-gray-100 rounded-xl p-8 text-center">
                    <video
                      ref={videoRef}
                      className="max-w-full h-64 object-cover rounded-lg mb-4 hidden"
                      autoPlay
                      playsInline
                    />
                    <canvas ref={canvasRef} className="hidden" />
                    
                    {selectedImage && (
                      <div className="relative mb-4">
                        <img
                          src={selectedImage}
                          alt="預覽"
                          className="max-w-full h-64 object-cover rounded-lg mx-auto"
                        />
                        <button
                          onClick={() => {
                            setSelectedImage(null);
                            setAnalysisResults(null);
                          }}
                          className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-2 hover:bg-red-600"
                        >
                          <XMarkIcon className="h-5 w-5" />
                        </button>
                      </div>
                    )}

                    {!selectedImage && (
                      <div className="space-y-4">
                        <div className="text-6xl mb-4">📷</div>
                        <h3 className="text-xl font-semibold text-gray-700">上傳食物照片</h3>
                        <p className="text-gray-500">支援 JPG、PNG 格式，最大 5MB</p>
                      </div>
                    )}
                        </div>

                  {/* 控制按鈕 */}
                  <div className="flex flex-wrap gap-4 justify-center mt-6">
                    <button
                      onClick={startCamera}
                      className="flex items-center gap-2 bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors"
                    >
                      <CameraIcon className="h-5 w-5" />
                      開啟相機
                    </button>
                    <button
                      onClick={capturePhoto}
                      className="flex items-center gap-2 bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-colors"
                    >
                      <PhotoIcon className="h-5 w-5" />
                      拍照分析
                    </button>
                    <label className="flex items-center gap-2 bg-purple-500 text-white px-6 py-3 rounded-lg hover:bg-purple-600 transition-colors cursor-pointer">
                      <InboxArrowDownIcon className="h-5 w-5" />
                      上傳圖片
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handleImageUpload}
                          className="hidden"
                        />
                    </label>
                  </div>
                      </div>

                {/* 載入中 */}
                {isAnalyzing && (
                  <div className="text-center py-8">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-4"></div>
                    <p className="text-gray-600">AI正在分析食物...</p>
                  </div>
                )}

                {/* 分析結果 */}
                {analysisResults && !isAnalyzing && (
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6">
                    <div className="flex justify-between items-center mb-6">
                      <h3 className="text-2xl font-bold text-gray-800">{analysisResults.foodName}</h3>
                      <button
                        onClick={addToFoodDiary}
                        className="bg-gradient-to-r from-red-400 to-red-600 text-white px-6 py-2 rounded-full hover:from-red-500 hover:to-red-700 transition-all"
                      >
                        + 加入記錄
                      </button>
                  </div>

                    <p className="text-gray-600 mb-6">{analysisResults.description}</p>
                      
                    {/* 健康指數 */}
                    <div className="grid grid-cols-2 gap-4 mb-6">
                      <div className="bg-white p-4 rounded-lg shadow-sm">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm text-gray-500">健康指數</span>
                          <span className="font-semibold">{analysisResults.healthIndex}/100</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full transition-all"
                            style={{ width: `${analysisResults.healthIndex}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="bg-white p-4 rounded-lg shadow-sm">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm text-gray-500">升糖指數</span>
                          <span className="font-semibold">{analysisResults.glycemicIndex}/100</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-pink-400 to-orange-400 h-2 rounded-full transition-all"
                            style={{ width: `${analysisResults.glycemicIndex}%` }}
                          ></div>
                        </div>
                        </div>
                      </div>

                    {/* 營養益處 */}
                    <div className="mb-6">
                      <h4 className="font-semibold text-gray-700 mb-3">營養益處</h4>
                      <div className="flex flex-wrap gap-2">
                        {analysisResults.benefits.map((benefit, index) => (
                          <span
                            key={index}
                            className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm"
                          >
                            {benefit}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* 營養資訊 */}
                    <div className="mb-6">
                      <h4 className="font-semibold text-gray-700 mb-3">營養資訊 (每100g)</h4>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {Object.entries(analysisResults.nutrition).map(([key, value]) => (
                          <div key={key} className="bg-white p-4 rounded-lg shadow-sm text-center">
                            <div className="text-sm text-gray-500 mb-1">
                              {key === 'calories' ? '熱量' : 
                               key === 'protein' ? '蛋白質' :
                               key === 'carbs' ? '碳水化合物' :
                               key === 'fat' ? '脂肪' :
                               key === 'fiber' ? '纖維' : '糖分'}
                            </div>
                            <div className="text-lg font-bold text-gray-800">
                              {value} {key === 'calories' ? '卡' : 'g'}
                            </div>
                          </div>
                        ))}
                          </div>
                        </div>
                        
                    {/* 維生素和礦物質 */}
                    {(analysisResults.vitamins || analysisResults.minerals) && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {analysisResults.vitamins && (
                          <div>
                            <h4 className="font-semibold text-gray-700 mb-3">維生素</h4>
                            <div className="grid grid-cols-2 gap-3">
                              {Object.entries(analysisResults.vitamins).map(([key, value]) => (
                                <div key={key} className="bg-white p-3 rounded-lg shadow-sm text-center">
                                  <div className="text-sm text-gray-500 mb-1">{key}</div>
                                  <div className="font-semibold text-gray-800">{value} mg</div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        {analysisResults.minerals && (
                          <div>
                            <h4 className="font-semibold text-gray-700 mb-3">礦物質</h4>
                            <div className="grid grid-cols-2 gap-3">
                              {Object.entries(analysisResults.minerals).map(([key, value]) => (
                                <div key={key} className="bg-white p-3 rounded-lg shadow-sm text-center">
                                  <div className="text-sm text-gray-500 mb-1">{key}</div>
                                  <div className="font-semibold text-gray-800">{value} mg</div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* 個人化建議 */}
                    {userProfile.name && (
                      <div className="mt-6 bg-gradient-to-r from-red-50 to-orange-50 p-4 rounded-lg border-l-4 border-red-400">
                        <div className="font-semibold text-gray-800 mb-2">💡 個人化建議</div>
                        <div className="text-gray-600">
                          這份食物約佔您每日熱量建議的 {Math.round((analysisResults.nutrition.calories / userProfile.dailyCalories) * 100)}%。
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 個人資料頁面 */}
          {activeTab === 'profile' && (
            <div className="p-8">
              <div className="max-w-2xl mx-auto">
                <h2 className="text-2xl font-bold text-gray-800 mb-6">個人資料設定</h2>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">姓名</label>
                    <input
                      type="text"
                      value={userProfile.name}
                      onChange={(e) => handleProfileChange('name', e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="請輸入您的姓名"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">年齡</label>
                      <input
                        type="number"
                        value={userProfile.age}
                        onChange={(e) => handleProfileChange('age', e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="歲"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">性別</label>
                      <select
                        value={userProfile.gender}
                        onChange={(e) => handleProfileChange('gender', e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="">請選擇</option>
                        <option value="male">男性</option>
                        <option value="female">女性</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">身高 (cm)</label>
                      <input
                        type="number"
                        value={userProfile.height}
                        onChange={(e) => handleProfileChange('height', e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="公分"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">體重 (kg)</label>
                      <input
                        type="number"
                        value={userProfile.weight}
                        onChange={(e) => handleProfileChange('weight', e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="公斤"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">活動量</label>
                      <select
                        value={userProfile.activityLevel}
                        onChange={(e) => handleProfileChange('activityLevel', e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="sedentary">久坐少動</option>
                        <option value="light">輕度活動</option>
                        <option value="moderate">中度活動</option>
                        <option value="active">高度活動</option>
                        <option value="extra">超高活動</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">健康目標</label>
                      <select
                        value={userProfile.goal}
                        onChange={(e) => handleProfileChange('goal', e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="lose">減重</option>
                        <option value="maintain">維持體重</option>
                        <option value="gain">增重</option>
                      </select>
                    </div>
                  </div>

                  <button
                    onClick={saveProfile}
                    className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-6 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all font-medium"
                      >
                    💾 儲存個人資料
                        </button>
                </div>
              </div>
            </div>
          )}

          {/* 營養追蹤頁面 */}
          {activeTab === 'tracking' && (
            <div className="p-8">
              {!userProfile.name ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📊</div>
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">請先完成個人資料設定</h3>
                  <p className="text-gray-500">開始追蹤您的營養攝取 👆</p>
                </div>
              ) : (
                <div className="max-w-6xl mx-auto">
                  {/* 歡迎訊息 */}
                  <div className="text-center mb-8">
                    <h3 className="text-2xl font-bold text-gray-800 mb-2">
                      👋 你好, {userProfile.name}!
                    </h3>
                    <p className="text-gray-600">這是您今天的營養總覽。</p>
                  </div>

                  {/* 統計卡片 */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-gradient-to-r from-red-400 to-red-600 text-white p-6 rounded-xl shadow-lg">
                      <div className="text-3xl font-bold mb-2">
                        {nutritionSummary?.calories || 0}
                      </div>
                      <div className="text-sm opacity-90">今日熱量</div>
                    </div>
                    <div className="bg-gradient-to-r from-blue-400 to-blue-600 text-white p-6 rounded-xl shadow-lg">
                      <div className="text-3xl font-bold mb-2">
                        {nutritionSummary?.protein || 0}g
                      </div>
                      <div className="text-sm opacity-90">蛋白質</div>
                    </div>
                    <div className="bg-gradient-to-r from-green-400 to-green-600 text-white p-6 rounded-xl shadow-lg">
                      <div className="text-3xl font-bold mb-2">
                        {nutritionSummary?.fiber || 0}g
                      </div>
                      <div className="text-sm opacity-90">纖維</div>
                    </div>
                    <div className="bg-gradient-to-r from-purple-400 to-purple-600 text-white p-6 rounded-xl shadow-lg">
                      <div className="text-3xl font-bold mb-2">
                        {userProfile.dailyCalories}
                      </div>
                      <div className="text-sm opacity-90">目標熱量</div>
                    </div>
                      </div>

                  {/* 目標進度 */}
                  <div className="bg-white rounded-xl p-6 shadow-lg mb-8">
                    <h3 className="text-xl font-semibold text-gray-800 mb-4">目標進度</h3>
                    <div className="space-y-4">
                      {[
                        { label: '熱量', current: nutritionSummary?.calories || 0, goal: userProfile.dailyCalories, color: 'from-red-400 to-red-600' },
                        { label: '蛋白質', current: nutritionSummary?.protein || 0, goal: userProfile.proteinGoal, color: 'from-blue-400 to-blue-600' },
                        { label: '纖維', current: nutritionSummary?.fiber || 0, goal: userProfile.fiberGoal, color: 'from-green-400 to-green-600' }
                      ].map((item, index) => {
                        const progress = item.goal > 0 ? Math.min(100, (item.current / item.goal) * 100) : 0;
                        return (
                          <div key={index}>
                            <div className="flex justify-between items-center mb-2">
                              <span className="font-medium text-gray-700">{item.label}</span>
                              <span className="text-sm text-gray-500">
                                {item.current} / {item.goal} {item.label === '熱量' ? '卡' : 'g'}
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className={`bg-gradient-to-r ${item.color} h-2 rounded-full transition-all`}
                                style={{ width: `${progress}%` }}
                              ></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* 本週趨勢圖 */}
                  <div className="bg-white rounded-xl p-6 shadow-lg mb-8">
                    <h3 className="text-xl font-semibold text-gray-800 mb-4">本週營養攝取趨勢</h3>
                    <div style={{ height: '300px' }}>
                      <canvas ref={chartRef}></canvas>
                    </div>
                  </div>

                  {/* 今日飲食記錄 */}
                  <div className="bg-white rounded-xl p-6 shadow-lg">
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-xl font-semibold text-gray-800">今日飲食記錄</h3>
                      <span className="text-sm text-gray-500">
                        {foodDiary.length} 項記錄
                      </span>
                    </div>
                    
                    {foodDiary.length === 0 ? (
                      <div className="text-center py-12">
                        <div className="text-6xl mb-4">🍽️</div>
                        <p className="text-gray-500">今天尚未記錄任何食物</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {foodDiary.map((meal) => (
                          <div key={meal.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                            <div>
                              <h4 className="font-medium text-gray-800">{meal.foodName}</h4>
                              <span className="text-sm text-gray-500">
                                {new Date(meal.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </span>
                            </div>
                            <div className="text-lg font-semibold text-gray-800">
                              {Math.round(meal.nutrition.calories)} 卡
                            </div>
                          </div>
                        ))}
                    </div>
                  )}
                </div>
              </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
