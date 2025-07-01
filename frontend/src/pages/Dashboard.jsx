import React, { useState } from 'react';
import { UserIcon, CalculatorIcon, CalendarIcon, CloudArrowUpIcon, ClipboardDocumentListIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

export default function Dashboard() {
  // 狀態區
  const [user, setUser] = useState({ name: '', age: '', height: '', weight: '', id: '' });
  const [userCreated, setUserCreated] = useState(false);
  const [foodDate, setFoodDate] = useState('');
  const [foodCal, setFoodCal] = useState('');
  const [foodCarb, setFoodCarb] = useState('');
  const [foodProtein, setFoodProtein] = useState('');
  const [foodMsg, setFoodMsg] = useState('');
  const [bmi, setBmi] = useState(null);
  const [bmiMsg, setBmiMsg] = useState('');
  const [waterDate, setWaterDate] = useState('');
  const [water, setWater] = useState('');
  const [waterMsg, setWaterMsg] = useState('');
  const [aiResult, setAiResult] = useState('');
  const [history, setHistory] = useState([]);

  // 處理邏輯
  const handleCreateUser = (e) => { e.preventDefault(); setUserCreated(true); setUser({ ...user, id: '6' }); };
  const handleAddFood = (e) => { e.preventDefault(); setFoodMsg('Food log added successfully.'); setHistory([...history, { date: foodDate, cal: foodCal, carb: foodCarb, protein: foodProtein }]); };
  const handleCalcBmi = () => {
    if (user.height && user.weight) {
      const bmiVal = (user.weight / ((user.height / 100) ** 2)).toFixed(2);
      setBmi(bmiVal);
      let msg = '';
      if (bmiVal < 18.5) msg = '體重過輕，建議均衡飲食與適度運動';
      else if (bmiVal < 24) msg = '正常範圍，請繼續保持';
      else msg = '體重過重，建議增加運動與飲食控制';
      setBmiMsg(msg);
    }
  };
  const handleAddWater = (e) => { e.preventDefault(); let msg = ''; if (water >= 2000) msg = '今日補水充足！'; else msg = '今日飲水量不足，請多補充水分！'; setWaterMsg(msg); };
  const handleAi = () => { setAiResult('AI 分析結果：雞肉沙拉，約 350 kcal'); };
  const handleQueryHistory = () => { setHistory(history); };

  return (
    <div className="min-h-screen bg-gray-100 py-10 px-2">
      <div className="max-w-4xl mx-auto">
        {/* 上方切換選單間隔 */}
        <div className="flex flex-wrap gap-4 justify-center mb-10">
          <a href="#user" className="tab-btn">用戶</a>
          <a href="#food" className="tab-btn">飲食</a>
          <a href="#bmi" className="tab-btn">BMI</a>
          <a href="#water" className="tab-btn">水分</a>
          <a href="#ai" className="tab-btn">AI</a>
          <a href="#history" className="tab-btn">歷史</a>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
          {/* 用戶卡片 */}
          <section id="user" className="bg-white rounded-2xl shadow-lg p-6 flex flex-col gap-4 border border-gray-100">
            <div className="flex items-center gap-2 mb-2">
              <UserIcon className="h-5 w-5 text-indigo-400" />
              <span className="font-bold text-xl">用戶資料</span>
            </div>
            <form onSubmit={handleCreateUser} className="flex flex-col gap-2">
              <input className="input" placeholder="姓名" value={user.name} onChange={e => setUser({ ...user, name: e.target.value })} />
              <input className="input" placeholder="年齡" value={user.age} onChange={e => setUser({ ...user, age: e.target.value })} />
              <input className="input" placeholder="身高 (cm)" value={user.height} onChange={e => setUser({ ...user, height: e.target.value })} />
              <input className="input" placeholder="體重 (kg)" value={user.weight} onChange={e => setUser({ ...user, weight: e.target.value })} />
              <button className="btn-primary mt-2 text-lg">建立用戶</button>
            </form>
            {userCreated && (
              <>
                <div className="text-xs text-gray-400 mt-1">用戶ID：6</div>
                <button className="btn-secondary mt-1" onClick={() => setUserCreated(false)}>變更用戶資料</button>
                <div className="mt-2 text-gray-700 text-base">
                  <div>姓名：{user.name}</div>
                  <div>年齡：{user.age}</div>
                  <div>身高：{user.height} cm</div>
                  <div>體重：{user.weight} kg</div>
                </div>
              </>
            )}
          </section>
          {/* 飲食紀錄卡片 */}
          <section id="food" className="bg-white rounded-2xl shadow-lg p-6 flex flex-col gap-4 border border-gray-100">
            <div className="flex items-center gap-2 mb-2">
              <ClipboardDocumentListIcon className="h-5 w-5 text-indigo-400" />
              <span className="font-bold text-xl">飲食紀錄</span>
            </div>
            <form onSubmit={handleAddFood} className="flex flex-col gap-2">
              <input className="input" type="date" value={foodDate} onChange={e => setFoodDate(e.target.value)} />
              <input className="input" placeholder="熱量 (kcal)" value={foodCal} onChange={e => setFoodCal(e.target.value)} />
              <input className="input" placeholder="碳水 (g)" value={foodCarb} onChange={e => setFoodCarb(e.target.value)} />
              <input className="input" placeholder="蛋白質 (g)" value={foodProtein} onChange={e => setFoodProtein(e.target.value)} />
              <button className="btn-primary mt-2 text-lg">新增紀錄</button>
            </form>
            {foodMsg && <div className="text-green-600 text-xs mt-1">{foodMsg}</div>}
          </section>
          {/* BMI 卡片 */}
          <section id="bmi" className="bg-white rounded-2xl shadow-lg p-6 flex flex-col gap-4 border border-gray-100">
            <div className="flex items-center gap-2 mb-2">
              <CalculatorIcon className="h-5 w-5 text-indigo-400" />
              <span className="font-bold text-xl">BMI 與建議</span>
            </div>
            <button className="btn-primary mb-2 text-lg" onClick={handleCalcBmi}>查詢 BMI</button>
            {bmi && <div className="text-indigo-700 font-bold text-xl">BMI：{bmi}</div>}
            {bmiMsg && <div className="text-base text-gray-600">{bmiMsg}</div>}
          </section>
          {/* 水分卡片 */}
          <section id="water" className="bg-white rounded-2xl shadow-lg p-6 flex flex-col gap-4 border border-gray-100">
            <div className="flex items-center gap-2 mb-2">
              <CalendarIcon className="h-5 w-5 text-indigo-400" />
              <span className="font-bold text-xl">水分攝取</span>
            </div>
            <form onSubmit={handleAddWater} className="flex flex-col gap-2">
              <input className="input" type="date" value={waterDate} onChange={e => setWaterDate(e.target.value)} />
              <input className="input" placeholder="今日飲水量 (ml)" value={water} onChange={e => setWater(e.target.value)} />
              <button className="btn-primary mt-2 text-lg">登錄水分攝取</button>
            </form>
            {waterMsg && <div className="text-xs mt-1 text-blue-700">{waterMsg}</div>}
          </section>
          {/* AI 卡片 */}
          <section id="ai" className="bg-white rounded-2xl shadow-lg p-6 flex flex-col gap-4 border border-gray-100">
            <div className="flex items-center gap-2 mb-2">
              <CloudArrowUpIcon className="h-5 w-5 text-indigo-400" />
              <span className="font-bold text-xl">AI 食物辨識</span>
            </div>
            <input className="input mb-2 text-base" style={{fontSize:'1rem',padding:'0.5rem'}} placeholder="圖片檔案（模擬）" />
            <button className="btn-primary text-lg" onClick={handleAi}>上傳與辨識</button>
            {aiResult && <div className="text-green-700 text-xs mt-1">{aiResult}</div>}
          </section>
          {/* 歷史紀錄卡片 */}
          <section id="history" className="bg-white rounded-2xl shadow-lg p-6 flex flex-col gap-4 border border-gray-100 md:col-span-2">
            <div className="flex items-center gap-2 mb-2">
              <ArrowPathIcon className="h-5 w-5 text-indigo-400" />
              <span className="font-bold text-xl">歷史紀錄查詢</span>
            </div>
            <button className="btn-secondary mb-2 self-start text-lg" onClick={handleQueryHistory}>查詢所有歷史紀錄</button>
            <div className="w-full overflow-x-auto">
              <table className="min-w-full text-base">
                <thead>
                  <tr>
                    <th className="px-2 py-1">日期</th>
                    <th className="px-2 py-1">熱量</th>
                    <th className="px-2 py-1">碳水</th>
                    <th className="px-2 py-1">蛋白質</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((h, i) => (
                    <tr key={i} className="border-t">
                      <td className="px-2 py-1">{h.date}</td>
                      <td className="px-2 py-1">{h.cal}</td>
                      <td className="px-2 py-1">{h.carb}</td>
                      <td className="px-2 py-1">{h.protein}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {userCreated && (
              <div className="mt-2 text-gray-700 text-base text-left w-full">
                <div>用戶資料：</div>
                <div>姓名：{user.name}</div>
                <div>年齡：{user.age}</div>
                <div>身高：{user.height} cm</div>
                <div>體重：{user.weight} kg</div>
                <div>用戶固定測試ID：6</div>
              </div>
            )}
          </section>
        </div>
      </div>
      {/* 簡單樣式 */}
      <style>{`
        .input { @apply rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-300 text-lg; }
        .btn-primary { @apply bg-gradient-to-r from-indigo-400 to-cyan-400 text-white px-4 py-2 rounded font-bold shadow hover:from-indigo-500 hover:to-cyan-500 transition; }
        .btn-secondary { @apply bg-white border border-indigo-300 text-indigo-700 px-4 py-2 rounded font-bold shadow hover:bg-indigo-50 transition; }
        .tab-btn {@apply px-4 py-2 rounded-full bg-white shadow text-indigo-600 font-bold border border-indigo-200 hover:bg-indigo-50 text-lg;}
      `}</style>
    </div>
  );
}
