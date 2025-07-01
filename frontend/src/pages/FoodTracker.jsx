import React, { useState, useRef, useEffect } from 'react';
import { XMarkIcon, InboxArrowDownIcon, CalendarIcon, ClockIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import axios from 'axios';

export default function FoodTracker() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [mealType, setMealType] = useState('lunch');
  const [mealDate, setMealDate] = useState(new Date().toISOString().split('T')[0]);
  const [mealTime, setMealTime] = useState(new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' }));
  const [portionSize, setPortionSize] = useState('medium');
  const [nutritionSummary, setNutritionSummary] = useState(null);
  const [recentMeals, setRecentMeals] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const imageRef = useRef(null);

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

      setIsAnalyzing(true);
      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://localhost:8000/api/ai/analyze-food', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('分析請求失敗');
        }

        const data = await response.json();

        if (data.success && data.top_prediction) {
          setAnalysisResults(data);
        } else {
          throw new Error(data.error || 'AI 無法識別這道食物');
        }
      } catch (error) {
        console.error('Error analyzing image:', error);
        alert(error.message || '圖片分析失敗，請稍後再試');
      } finally {
        setIsAnalyzing(false);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="relative px-4 py-10 bg-white mx-8 md:mx-0 shadow rounded-3xl sm:p-10">
          <div className="max-w-md mx-auto">
            <div className="divide-y divide-gray-200">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <div className="flex flex-col items-center">
                  <h2 className="text-2xl font-bold mb-4">AI 智慧食物分析</h2>

                  {/* 上傳區域 */}
                  <div
                    className={`border-2 ${isDragging ? 'border-indigo-500 bg-indigo-100' : 'border-gray-300'} 
                    border-dashed rounded-lg p-8 w-full max-w-sm transition-all`}
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                  >
                    {selectedImage ? (
                      <div className="relative">
                        <img
                          ref={imageRef}
                          src={selectedImage}
                          alt="預覽"
                          className="max-w-full h-48 object-contain rounded-lg"
                        />
                        <button
                          onClick={() => {
                            setSelectedImage(null);
                            setAnalysisResults(null);
                          }}
                          className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                        >
                          <XMarkIcon className="h-5 w-5" />
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-3 flex flex-col items-center justify-center">
                        <InboxArrowDownIcon className="h-12 w-12 text-gray-400" />
                        <div className="text-gray-600">
                          拖曳圖片到這裡，或
                          <label htmlFor="food-image" className="text-indigo-600 hover:text-indigo-700 cursor-pointer mx-1">
                            點擊上傳
                          </label>
                        </div>
                        <input
                          id="food-image"
                          type="file"
                          accept="image/*"
                          onChange={handleImageUpload}
                          className="hidden"
                        />
                      </div>
                    )}
                  </div>

                  {/* 載入中動畫 */}
                  {analysisResults && (
                    <div className="mt-4 p-4 bg-green-50 rounded-lg">
                      <h3 className="text-lg font-semibold text-green-800 mb-2">分析結果</h3>
                      <p className="text-green-700 mb-4">這是：{analysisResults.top_prediction}</p>
                      
                      {/* 營養資訊 */}
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="bg-white p-3 rounded-lg shadow-sm">
                          <p className="text-sm text-gray-500">熱量</p>
                          <p className="font-semibold">{analysisResults.nutrition?.calories || '--'} kcal</p>
                        </div>
                        <div className="bg-white p-3 rounded-lg shadow-sm">
                          <p className="text-sm text-gray-500">蛋白質</p>
                          <p className="font-semibold">{analysisResults.nutrition?.protein || '--'} g</p>
                        </div>
                        <div className="bg-white p-3 rounded-lg shadow-sm">
                          <p className="text-sm text-gray-500">碳水化合物</p>
                          <p className="font-semibold">{analysisResults.nutrition?.carbs || '--'} g</p>
                        </div>
                        <div className="bg-white p-3 rounded-lg shadow-sm">
                          <p className="text-sm text-gray-500">脂肪</p>
                          <p className="font-semibold">{analysisResults.nutrition?.fat || '--'} g</p>
                        </div>
                      </div>

                      {/* 用餐記錄 */}
                      <div className="space-y-4">
                        <div className="flex items-center space-x-4">
                          <div className="flex-1">
                            <label className="block text-sm font-medium text-gray-700 mb-1">用餐類型</label>
                            <select
                              value={mealType}
                              onChange={(e) => setMealType(e.target.value)}
                              className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                            >
                              <option value="breakfast">早餐</option>
                              <option value="lunch">午餐</option>
                              <option value="dinner">晚餐</option>
                              <option value="snack">點心</option>
                            </select>
                          </div>
                          <div className="flex-1">
                            <label className="block text-sm font-medium text-gray-700 mb-1">份量</label>
                            <select
                              value={portionSize}
                              onChange={(e) => setPortionSize(e.target.value)}
                              className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                            >
                              <option value="small">小份</option>
                              <option value="medium">中份</option>
                              <option value="large">大份</option>
                            </select>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                          <div className="flex-1">
                            <label className="block text-sm font-medium text-gray-700 mb-1">日期</label>
                            <div className="relative">
                              <CalendarIcon className="h-5 w-5 text-gray-400 absolute left-3 top-2.5" />
                              <input
                                type="date"
                                value={mealDate}
                                onChange={(e) => setMealDate(e.target.value)}
                                className="w-full pl-10 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                              />
                            </div>
                          </div>
                          <div className="flex-1">
                            <label className="block text-sm font-medium text-gray-700 mb-1">時間</label>
                            <div className="relative">
                              <ClockIcon className="h-5 w-5 text-gray-400 absolute left-3 top-2.5" />
                              <input
                                type="time"
                                value={mealTime}
                                onChange={(e) => setMealTime(e.target.value)}
                                className="w-full pl-10 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                              />
                            </div>
                          </div>
                        </div>

                        <button
                        onClick={async () => {
                          try {
                            setIsLoading(true);
                            const mealDateTime = new Date(`${mealDate}T${mealTime}`);
                            
                            // 儲存用餐記錄
                            await axios.post('http://localhost:8000/api/meals/log', {
                              food_name: analysisResults.top_prediction,
                              meal_type: mealType,
                              portion_size: portionSize,
                              meal_date: mealDateTime.toISOString(),
                              nutrition: analysisResults.nutrition,
                              image_url: selectedImage,
                              ai_analysis: analysisResults
                            });

                            // 更新營養總結
                            const today = new Date();
                            const startDate = new Date(today.getFullYear(), today.getMonth(), today.getDate());
                            const endDate = new Date(startDate);
                            endDate.setDate(endDate.getDate() + 1);

                            const summaryResponse = await axios.post('http://localhost:8000/api/meals/nutrition-summary', {
                              start_date: startDate.toISOString(),
                              end_date: endDate.toISOString()
                            });
                            
                            setNutritionSummary(summaryResponse.data.data);

                            // 更新最近用餐記錄
                            const logsResponse = await axios.post('http://localhost:8000/api/meals/list', {
                              start_date: startDate.toISOString(),
                              end_date: endDate.toISOString()
                            });
                            
                            setRecentMeals(logsResponse.data.data);
                            alert('記錄已儲存！');
                            
                            // 清空當前分析
                            setSelectedImage(null);
                            setAnalysisResults(null);
                          } catch (error) {
                            console.error('Error saving meal log:', error);
                            alert('儲存失敗：' + (error.response?.data?.detail || error.message));
                          } finally {
                            setIsLoading(false);
                          }
                        }}
                        className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                      >
                        記錄這餐
                        </button>
                      </div>
                    </div>
                  )}

                  {/* 分析結果 */}
                  {analysisResults && analysisResults.success && (
                    <div className="mt-6 space-y-4 w-full">
                      {/* 主要預測結果 */}
                      <div className="text-center">
                        <h3 className="text-xl font-semibold text-indigo-600 mb-2">
                          分析結果
                        </h3>
                        <p className="text-lg text-gray-800">
                          {analysisResults.top_prediction?.label}
                          <span className="text-gray-500 text-base ml-2">
                            ({Math.round(analysisResults.top_prediction?.confidence)}% 確信度)
                          </span>
                        </p>
                      </div>

                      {/* 營養資訊 */}
                      {analysisResults.top_prediction?.nutrition && (
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <h4 className="font-semibold mb-3 text-gray-700">營養資訊</h4>
                          <div className="grid grid-cols-2 gap-3">
                            <div className="flex justify-between">
                              <span>熱量:</span>
                              <span>{analysisResults.top_prediction.nutrition.calories} kcal</span>
                            </div>
                            <div className="flex justify-between">
                              <span>蛋白質:</span>
                              <span>{analysisResults.top_prediction.nutrition.protein}g</span>
                            </div>
                            <div className="flex justify-between">
                              <span>碳水化合物:</span>
                              <span>{analysisResults.top_prediction.nutrition.carbs}g</span>
                            </div>
                            <div className="flex justify-between">
                              <span>脂肪:</span>
                              <span>{analysisResults.top_prediction.nutrition.fat}g</span>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* 食物描述 */}
                      {analysisResults.top_prediction?.description && (
                        <div className="bg-blue-50 p-4 rounded-lg">
                          <h4 className="font-semibold mb-2 text-gray-700">食物描述</h4>
                          <p className="text-gray-600">
                            {analysisResults.top_prediction.description}
                          </p>
                        </div>
                      )}

                      {/* 分析時間 */}
                      <div className="text-xs text-gray-500 text-center">
                        分析時間: {new Date(analysisResults.analysis_time).toLocaleString()}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
