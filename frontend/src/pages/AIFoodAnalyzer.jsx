import React, { useState, useRef, useEffect } from 'react';
import Chart from 'chart.js/auto';
import './AIFoodAnalyzer.css';

const API_BASE_URL = 'http://127.0.0.1:8000';

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
  function addToFoodDiary() {
    if (!result) return alert('沒有可加入的分析結果。');
    const meal = { ...result, id: Date.now(), timestamp: new Date().toISOString() };
    const newDiary = [...foodDiary, meal];
    saveFoodDiary(newDiary);
    alert(`${meal.foodName} 已加入記錄！`);
  }

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
      if (blob) processImage(blob);
      else setError('無法擷取圖片，請再試一次');
    }, 'image/jpeg');
  };
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
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
      const aiResponse = await fetch(`${API_BASE_URL}/ai/analyze-food-image/`, {
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
      setError(`分析失敗: ${err.message}`);
    } finally {
      setLoading(false);
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
          <div className="camera-container">
            <video ref={videoRef} autoPlay playsInline style={{width:'100%',maxWidth:300, borderRadius:15, boxShadow:'0 5px 15px rgba(0,0,0,0.2)', background:'#000'}} />
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
                    {Object.entries(result.nutrition||{}).map(([k,v])=>(
                      <div key={k} className="nutrition-item">
                        <div className="nutrition-label">{k}</div>
                        <div className="nutrition-value">{v}</div>
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
                    這份食物約佔您每日熱量建議的 {Math.round((result.nutrition?.calories / profile.dailyCalories) * 100)}%。
                  </div>
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
      )}
    </div>
  );
}

export default AIFoodAnalyzer;
