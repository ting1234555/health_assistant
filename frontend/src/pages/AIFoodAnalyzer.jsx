import React, { useState, useEffect, useRef } from 'react';
import './AIFoodAnalyzer.css';

const TABS = [
  { id: 'analyzer', label: '分析食物' },
  { id: 'profile', label: '個人資料' },
  { id: 'tracking', label: '營養追蹤' },
];

const defaultProfile = {
  name: '',
  age: '',
  gender: '',
  height: '',
  weight: '',
  activityLevel: 'sedentary',
  healthGoal: 'maintain',
  dailyCalories: 0,
  proteinGoal: 0,
  fiberGoal: 25,
  waterGoal: 2000
};

const nutritionLabels = {
  calories: '熱量', protein: '蛋白質', carbs: '碳水化合物', fat: '脂肪', fiber: '纖維', sugar: '糖分'
};
const nutritionUnits = {
  calories: '卡', protein: 'g', carbs: 'g', fat: 'g', fiber: 'g', sugar: 'g'
};

function calculateBMR({ gender, weight, height, age }) {
  if (gender === 'male') {
    return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age);
  }
  return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age);
}

function calculateDailyCalories(bmr, activityLevel, healthGoal) {
  const activityMultipliers = {
    sedentary: 1.2,
    light: 1.375,
    moderate: 1.55,
    active: 1.725,
    extra: 1.9,
  };
  let calories = bmr * (activityMultipliers[activityLevel] || 1.2);
  const goalAdjustments = { lose: -300, gain: 300, muscle: 200 };
  calories += goalAdjustments[healthGoal] || 0;
  return Math.round(calories);
}

const API_BASE_URL = 'http://127.0.0.1:8000';

const AnalyzerTab = ({ userProfile, onAddToDiary }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const [stream, setStream] = useState(null);

  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream]);

  const showNotification = (msg) => {
    alert(msg);
  };

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
        processImage(blob);
      } else {
        setError('無法擷取圖片，請再試一次');
      }
    }, 'image/jpeg');
  };

  const handleFileUpload = (e) => {
    setError('');
    const file = e.target.files[0];
    if (file) {
      processImage(file);
      e.target.value = '';
    }
  };

  const processImage = async (imageSource) => {
    setIsLoading(true);
    setAnalysis(null);
    setError('');
    const formData = new FormData();
    formData.append('file', imageSource);
    try {
      const aiResponse = await fetch(`${API_BASE_URL}/ai/analyze-food-image/`, {
        method: 'POST',
        body: formData,
      });
      if (!aiResponse.ok) {
        const errorData = await aiResponse.json();
        throw new Error(errorData.detail || `AI辨識失敗 (狀態碼: ${aiResponse.status})`);
      }
      const aiData = await aiResponse.json();
      const foodName = aiData.food_name;
      if (!foodName || foodName === 'Unknown') {
        throw new Error('AI無法辨識出食物名稱。');
      }
      let result = {
        foodName,
        description: `AI 辨識結果：${foodName}`,
        healthIndex: 75,
        glycemicIndex: 50,
        benefits: [`含有 ${foodName} 的營養成分`],
        nutrition: {
          calories: 150,
          protein: 8,
          carbs: 20,
          fat: 5,
          fiber: 3,
          sugar: 2
        },
        vitamins: {
          'Vitamin C': 15,
          'Vitamin A': 10
        },
        minerals: {
          'Iron': 2,
          'Calcium': 50
        }
      };
      try {
        const nutritionResponse = await fetch(`${API_BASE_URL}/api/analyze-nutrition/${encodeURIComponent(foodName)}`);
        if (nutritionResponse.ok) {
          const nutritionData = await nutritionResponse.json();
          if (nutritionData.success) {
            result = {
              foodName,
              ...nutritionData
            };
          }
        }
      } catch (nutritionError) {
        // ignore, fallback to default
      }
      setAnalysis(result);
    } catch (err) {
      setError(`分析失敗: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddToDiary = () => {
    if (!analysis) return;
    onAddToDiary(analysis);
    showNotification(`${analysis.foodName} 已加入記錄！`);
  };

  // UI
  if (!userProfile) {
    return (
      <div id="profileCheck" className="no-profile" style={{display:'block'}}>
        <p>請先到「個人資料」頁面完成設定，以獲得個人化營養建議和追蹤功能 👆</p>
      </div>
    );
  }

    return (
    <div id="analyzerContent">
      <div className="camera-container">
        <video ref={videoRef} autoPlay playsInline style={{width:'100%',maxWidth:300, borderRadius:15, boxShadow:'0 5px 15px rgba(0,0,0,0.2)', background:'#000'}} />
        <canvas ref={canvasRef} style={{display:'none'}} />
      </div>
      <div className="controls">
        <button onClick={startCamera}>📷 開啟相機</button>
        <button onClick={capturePhoto}>📸 拍照分析</button>
        <button className="upload-btn" onClick={()=>fileInputRef.current.click()}>📁 上傳圖片</button>
        <input ref={fileInputRef} type="file" className="file-input" accept="image/*" onChange={handleFileUpload} />
      </div>
      {isLoading && (
        <div className="loading" style={{display:'flex'}}>
          <div className="spinner"></div>
          <p>AI正在分析食物中...</p>
        </div>
      )}
      {error && <div style={{color:'red',textAlign:'center',margin:'1rem 0'}}>{error}</div>}
      {analysis && (
        <div className="result" style={{display:'block'}}>
          <div className="food-info">
            <h3 className="food-name">{analysis.foodName}</h3>
            <button className="add-to-diary" onClick={handleAddToDiary}>加入飲食記錄</button>
          </div>
          <div className="health-indices">
            <div className="health-index">
              <div className="index-label">健康指數</div>
              <div className="index-meter">
                <div className="meter-fill" style={{width:`${analysis.healthIndex||75}%`, background:'linear-gradient(45deg,#43cea2,#185a9d)'}}></div>
              </div>
              <div className="index-value">{analysis.healthIndex||75}/100</div>
            </div>
            <div className="health-index">
              <div className="index-label">升糖指數</div>
              <div className="index-meter">
                <div className="meter-fill" style={{width:`${analysis.glycemicIndex||50}%`, background:'linear-gradient(45deg,#ff9a9e,#fad0c4)'}}></div>
              </div>
              <div className="index-value">{analysis.glycemicIndex||50}/100</div>
            </div>
          </div>
          <p className="food-description">{analysis.description || `這是 ${analysis.foodName}`}</p>
          <div className="benefits-tags">
            {(analysis.benefits||[`${analysis.foodName} 的營養價值`]).map((b,i)=>(
              <span key={i} className="benefit-tag">{b}</span>
            ))}
          </div>
          <div className="nutrition-details">
            <div className="nutrition-section">
              <h4 className="nutrition-section-title">基本營養素</h4>
              <div className="nutrition-grid">
                {Object.entries(analysis.nutrition||{}).map(([k,v])=>(
                  <div key={k} className="nutrition-item">
                    <div className="nutrition-label">{nutritionLabels[k]}</div>
                    <div className="nutrition-value">{v} {nutritionUnits[k]}</div>
                  </div>
                ))}
              </div>
            </div>
            <div className="nutrition-section">
              <h4 className="nutrition-section-title">維生素</h4>
              <div className="nutrition-grid">
                {analysis.vitamins && Object.entries(analysis.vitamins).map(([k,v])=>(
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
                {analysis.minerals && Object.entries(analysis.minerals).map(([k,v])=>(
                  <div key={k} className="nutrition-item">
                    <div className="nutrition-label">{k}</div>
                    <div className="nutrition-value">{v} mg</div>
                  </div>
                ))}
          </div>
          </div>
          </div>
          {userProfile && (
        <div className="daily-recommendation">
          <div className="recommendation-title">💡 個人化建議</div>
          <div className="recommendation-text">
                這份食物約佔您每日熱量建議的 {Math.round((analysis.nutrition?.calories / userProfile.dailyCalories) * 100)}%。
              </div>
          </div>
          )}
        </div>
      )}
      </div>
    );
  };

const TrackingTab = ({ userProfile, foodDiary }) => {
  const chartRef = useRef(null);
  // 彙總今日
  const todayTotals = foodDiary.reduce((totals, meal) => {
    totals.calories += meal.nutrition?.calories || 0;
    totals.protein += meal.nutrition?.protein || 0;
    totals.fiber += meal.nutrition?.fiber || 0;
    return totals;
  }, { calories: 0, protein: 0, fiber: 0 });

  // 取得本週資料
  const getWeekData = () => {
    const days = ['日','一','二','三','四','五','六'];
    const week = [];
    const now = new Date();
    for (let i = 6; i >= 0; i--) {
      const d = new Date(now);
      d.setDate(now.getDate() - i);
      const key = d.toISOString().slice(0,10);
      const diary = JSON.parse(localStorage.getItem(`foodDiary_${key}`) || '[]');
      const total = diary.reduce((sum, m) => sum + (m.nutrition?.calories||0), 0);
      week.push({
        day: days[d.getDay()],
        calories: total
      });
    }
    return week;
  };

  // Chart.js 繪圖
  useEffect(() => {
    if (!chartRef.current) return;
    const ctx = chartRef.current.getContext('2d');
    if (chartRef.current._chart) {
      chartRef.current._chart.destroy();
    }
    const weekData = getWeekData();
    chartRef.current._chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: weekData.map(d=>d.day),
        datasets: [{
          label: '熱量',
          data: weekData.map(d=>d.calories),
          borderColor: '#43cea2',
          backgroundColor: 'rgba(67,206,162,0.1)',
          tension: 0.3,
          pointRadius: 4,
          fill: true
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { stepSize: 200 } }
        },
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }, [foodDiary]);

  if (!userProfile) {
    return <div className="no-profile">請先設定個人資料</div>;
  }

  return (
    <div className="tracking-tab">
      <div className="overview-cards">
        <div className="overview-card">
          <div className="overview-label">今日攝取熱量</div>
          <div className="overview-value">{Math.round(todayTotals.calories)} <span>卡</span></div>
      </div>
        <div className="overview-card">
          <div className="overview-label">蛋白質</div>
          <div className="overview-value">{Math.round(todayTotals.protein)} <span>g</span></div>
          </div>
        <div className="overview-card">
          <div className="overview-label">纖維</div>
          <div className="overview-value">{Math.round(todayTotals.fiber)} <span>g</span></div>
            </div>
          </div>
      <div className="progress-section">
        {[{label:'熱量',current:todayTotals.calories,goal:userProfile.dailyCalories,unit:'卡',color:'#43cea2'},
          {label:'蛋白質',current:todayTotals.protein,goal:userProfile.proteinGoal,unit:'g',color:'#185a9d'},
          {label:'纖維',current:todayTotals.fiber,goal:userProfile.fiberGoal,unit:'g',color:'#ff9a9e'}].map(({label,current,goal,unit,color})=>{
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
                <div className="food-diary-name">{meal.foodName}</div>
                <div className="food-diary-time">{new Date(meal.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                <div className="food-diary-calories">{Math.round(meal.nutrition?.calories||0)} 卡</div>
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
  );
};

export default function AIFoodAnalyzer() {
  const [tab, setTab] = useState('analyzer');
  const [userProfile, setUserProfile] = useState(null);
  const [foodDiary, setFoodDiary] = useState([]);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [notification, setNotification] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const chartRef = useRef(null);
  const [stream, setStream] = useState(null);

  // 初始化
  useEffect(() => {
    const stored = localStorage.getItem('userProfile');
    if (stored) setUserProfile(JSON.parse(stored));
    loadFoodDiary();
  }, []);

  useEffect(() => {
    if (tab === 'profile') {
      const stored = localStorage.getItem('userProfile');
      if (stored) setUserProfile(JSON.parse(stored));
    }
    if (tab === 'tracking') {
      loadFoodDiary();
      setTimeout(() => renderWeeklyChart(), 100); // Chart.js 需等 DOM
    }
  }, [tab]);

  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream]);

  // 分頁切換
  const switchTab = (tabId) => {
    setTab(tabId);
    setError('');
    setNotification(null);
  };

  // 通知
  const showNotification = (msg, type = 'info') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 2000);
  };

  // Profile
  const [profile, setProfile] = useState(() => {
    const stored = localStorage.getItem('userProfile');
    return stored ? JSON.parse(stored) : { ...defaultProfile };
  });
  const handleProfileChange = e => {
    const { name, value } = e.target;
    setProfile(p => ({ ...p, [name]: value }));
  };
  const saveProfile = e => {
    e.preventDefault();
    localStorage.setItem('userProfile', JSON.stringify(profile));
    setNotification('個人資料已儲存！');
  };

  // Diary
  const loadFoodDiary = () => {
    const today = new Date().toISOString().slice(0, 10);
    const stored = localStorage.getItem(`foodDiary_${today}`);
    setFoodDiary(stored ? JSON.parse(stored) : []);
  };
  const saveFoodDiary = (diary) => {
    const today = new Date().toISOString().slice(0, 10);
    localStorage.setItem(`foodDiary_${today}`, JSON.stringify(diary));
    setFoodDiary(diary);
  };
  const addToFoodDiary = () => {
    if (!currentAnalysis) {
      showNotification('沒有可加入的分析結果。', 'error');
      return;
    }
    const meal = {
      ...currentAnalysis,
      id: Date.now(),
      timestamp: new Date().toISOString()
    };
    const newDiary = [...foodDiary, meal];
    saveFoodDiary(newDiary);
    showNotification(`${meal.foodName} 已加入記錄！`, 'success');
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
        processImage(blob);
      } else {
        setError('無法擷取圖片，請再試一次');
      }
    }, 'image/jpeg');
  };
  const handleFileUpload = (e) => {
    setError('');
    const file = e.target.files[0];
    if (file) {
      processImage(file);
      e.target.value = '';
    }
  };
  const processImage = async (imageSource) => {
    setLoading(true);
    setCurrentAnalysis(null);
    setError('');
    const formData = new FormData();
    formData.append('file', imageSource);
    try {
      const aiResponse = await fetch(`${API_BASE_URL}/ai/analyze-food-image/`, {
        method: 'POST',
        body: formData,
      });
      if (!aiResponse.ok) {
        const errorData = await aiResponse.json();
        throw new Error(errorData.detail || `AI辨識失敗 (狀態碼: ${aiResponse.status})`);
      }
      const aiData = await aiResponse.json();
      const foodName = aiData.food_name;
      if (!foodName || foodName === 'Unknown') {
        throw new Error('AI無法辨識出食物名稱。');
      }
      let result = {
        foodName,
        description: `AI 辨識結果：${foodName}`,
        healthIndex: 75,
        glycemicIndex: 50,
        benefits: [`含有 ${foodName} 的營養成分`],
        nutrition: {
          calories: 150,
          protein: 8,
          carbs: 20,
          fat: 5,
          fiber: 3,
          sugar: 2
        },
        vitamins: {
          'Vitamin C': 15,
          'Vitamin A': 10
        },
        minerals: {
          'Iron': 2,
          'Calcium': 50
        }
      };
      try {
        const nutritionResponse = await fetch(`${API_BASE_URL}/api/analyze-nutrition/${encodeURIComponent(foodName)}`);
        if (nutritionResponse.ok) {
          const nutritionData = await nutritionResponse.json();
          if (nutritionData.success) {
            result = {
              foodName,
              ...nutritionData
            };
          }
        }
      } catch (nutritionError) {}
      setCurrentAnalysis(result);
    } catch (err) {
      setError(`分析失敗: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Chart.js 本週熱量趨勢
  const renderWeeklyChart = () => {
    if (!chartRef.current) return;
    if (chartRef.current._chart) {
      chartRef.current._chart.destroy();
    }
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
      week.push({
        day: days[d.getDay()],
        calories: total
      });
    }
    // eslint-disable-next-line
    // @ts-ignore
    chartRef.current._chart = new window.Chart(chartRef.current.getContext('2d'), {
      type: 'line',
      data: {
        labels: week.map(d=>d.day),
        datasets: [{
          label: '熱量',
          data: week.map(d=>d.calories),
          borderColor: '#43cea2',
          backgroundColor: 'rgba(67,206,162,0.1)',
          tension: 0.3,
          pointRadius: 4,
          fill: true
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { stepSize: 200 } }
        },
        responsive: true,
        maintainAspectRatio: false
      }
    });
  };

  // 分頁內容
  return (
    <div className="app-container">
      <div className="header">
        <h1 className="title">🍎 AI食物營養分析器</h1>
        <p className="subtitle">智能分析您的飲食營養</p>
      </div>
      <div className="tab-nav">
        <button className={`tab-btn${tab === 'analyzer' ? ' active' : ''}`} onClick={() => setTab('analyzer')}>分析食物</button>
        <button className={`tab-btn${tab === 'profile' ? ' active' : ''}`} onClick={() => setTab('profile')}>個人資料</button>
        <button className={`tab-btn${tab === 'tracking' ? ' active' : ''}`} onClick={() => setTab('tracking')}>營養追蹤</button>
      </div>
      {notification && (
        <div style={{textAlign:'center',color: notification.type==='error'?'#e74c3c':'#43cea2',marginBottom:'1rem'}}>{notification.msg}</div>
      )}
      <div id="analyzer" className={`tab-content${tab === 'analyzer' ? ' active' : ''}`}>
        <div id="profileCheck" className="no-profile" style={{ display: 'none' }}>
            <p>請先到「個人資料」頁面完成設定，以獲得個人化營養建議和追蹤功能 👆</p>
          </div>
          <div id="analyzerContent">
            <div className="camera-container">
            <video id="video" autoPlay playsInline></video>
            <canvas id="canvas"></canvas>
            </div>
            <div className="controls">
            <button>📷 開啟相機</button>
            <button>📸 拍照分析</button>
            <button className="upload-btn" onClick={() => document.getElementById('fileInput').click()}>📁 上傳圖片</button>
            <input type="file" id="fileInput" className="file-input" accept="image/*" onChange={() => {}} />
            </div>
          <div className="loading" id="loading" style={{ display: 'none' }}>
                <div className="spinner"></div>
                <p>AI正在分析食物中...</p>
              </div>
          <div className="result" id="result" style={{ display: 'none' }}>
                <div className="food-info">
              <h3 className="food-name" id="foodName">識別的食物</h3>
              <button className="add-to-diary">加入飲食記錄</button>
                </div>
                <div className="health-indices">
                  <div className="health-index">
                    <div className="index-label">健康指數</div>
                    <div className="index-meter">
                  <div className="meter-fill" id="healthIndexFill"></div>
                    </div>
                <div className="index-value" id="healthIndexValue">--/100</div>
                  </div>
                  <div className="health-index">
                    <div className="index-label">升糖指數</div>
                    <div className="index-meter">
                  <div className="meter-fill" id="glycemicIndexFill"></div>
                    </div>
                <div className="index-value" id="glycemicIndexValue">--/100</div>
                  </div>
                </div>
            <p className="food-description" id="foodDescription">這裡會顯示食物的詳細描述和營養價值。</p>
            <div className="benefits-tags" id="benefitsTags"></div>
                <div className="nutrition-details">
                  <div className="nutrition-section">
                    <h4 className="nutrition-section-title">基本營養素</h4>
                <div className="nutrition-grid" id="nutritionGrid"></div>
                  </div>
                  <div className="nutrition-section">
                    <h4 className="nutrition-section-title">維生素</h4>
                <div className="nutrition-grid" id="vitaminsGrid"></div>
                  </div>
                  <div className="nutrition-section">
                    <h4 className="nutrition-section-title">礦物質</h4>
                <div className="nutrition-grid" id="mineralsGrid"></div>
                        </div>
                    </div>
            <div className="daily-recommendation" id="recommendation"></div>
                  </div>
                </div>
                    </div>
      <div id="profile" className={`tab-content${tab === 'profile' ? ' active' : ''}`}>
        <div className="profile-form">
          <div className="input-group">
            <label htmlFor="userName">姓名</label>
            <input type="text" id="userName" placeholder="請輸入您的姓名" />
          </div>
          <div className="input-row">
            <div className="input-group">
              <label htmlFor="userAge">年齡</label>
              <input type="number" id="userAge" placeholder="歲" min="1" max="120" />
            </div>
            <div className="input-group">
              <label htmlFor="userGender">性別</label>
              <select id="userGender">
                <option value="">請選擇</option>
                <option value="male">男性</option>
                <option value="female">女性</option>
              </select>
            </div>
          </div>
          <div className="input-row">
            <div className="input-group">
              <label htmlFor="userHeight">身高 (cm)</label>
              <input type="number" id="userHeight" placeholder="公分" min="100" max="250" />
            </div>
            <div className="input-group">
              <label htmlFor="userWeight">體重 (kg)</label>
              <input type="number" id="userWeight" placeholder="公斤" min="30" max="200" />
            </div>
          </div>
          <div className="input-group">
            <label htmlFor="activityLevel">活動量</label>
            <select id="activityLevel">
              <option value="sedentary">久坐少動 (辦公室工作)</option>
              <option value="light">輕度活動 (每週運動1-3次)</option>
              <option value="moderate">中度活動 (每週運動3-5次)</option>
              <option value="active">高度活動 (每週運動6-7次)</option>
              <option value="extra">超高活動 (體力勞動+運動)</option>
            </select>
          </div>
          <div className="input-group">
            <label htmlFor="healthGoal">健康目標</label>
            <select id="healthGoal">
              <option value="lose">減重</option>
              <option value="maintain">維持體重</option>
              <option value="gain">增重</option>
              <option value="muscle">增肌</option>
              <option value="health">保持健康</option>
            </select>
          </div>
          <button className="save-profile-btn">💾 儲存資料</button>
        </div>
        {userProfile && (
          <div className="profile-summary" style={{marginTop: '1.5rem', background: '#f5f7fa', borderRadius: '10px', padding: '1rem'}}>
            <h4>您的每日建議：</h4>
            <ul>
              <li>熱量：{userProfile.dailyCalories} 卡</li>
              <li>蛋白質：{userProfile.proteinGoal} g</li>
              <li>纖維：{userProfile.fiberGoal} g</li>
              <li>水分：{userProfile.waterGoal} ml</li>
            </ul>
          </div>
        )}
      </div>
      <div id="tracking" className={`tab-content${tab === 'tracking' ? ' active' : ''}`}>
        <div id="trackingCheck" className="no-profile" style={{ display: 'none' }}>
          <p>請先到「個人資料」頁面完成設定，以獲得個人化營養建議和追蹤功能 👆</p>
        </div>
        <div className="tracking-container" id="trackingContent">
          <div className="welcome-message" id="welcomeMessage"></div>
          <div className="stats-grid" id="statsGrid">
            <div className="stat-card">
              <div className="stat-icon">🔥</div>
              <div className="stat-info">
                <div className="stat-value" id="todayCalories">0</div>
                <div className="stat-label">今日攝取熱量</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🎯</div>
              <div className="stat-info">
                <div className="stat-value" id="calorieGoalText">0</div>
                <div className="stat-label">每日目標熱量</div>
              </div>
            </div>
          </div>
          <div className="goals-container" id="goalsContainer">
            <h3>今日目標進度</h3>
            <div className="goal-items" id="goalItems"></div>
          </div>
          <div className="meals-card">
            <div className="meals-header">
              <h3>今日食物記錄</h3>
              <button className="btn-small" onClick={() => {}}>+ 新增餐點</button>
            </div>
            <div id="mealsList" className="meals-list"></div>
          </div>
          <div className="chart-card full-width">
            <div className="chart-header">
              <h3>本週熱量趨勢</h3>
            </div>
            <div className="chart-container">
              <canvas id="weeklyChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
