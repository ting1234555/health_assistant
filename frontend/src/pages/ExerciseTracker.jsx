import React from 'react';
import { useState } from 'react';
import { PlusIcon } from '@heroicons/react/24/outline';

const exerciseTypes = [
  { id: 'walking', name: '步行', caloriesPerMinute: 4 },
  { id: 'running', name: '跑步', caloriesPerMinute: 10 },
  { id: 'cycling', name: '騎自行車', caloriesPerMinute: 7 },
  { id: 'swimming', name: '游泳', caloriesPerMinute: 8 },
  { id: 'yoga', name: '瑜伽', caloriesPerMinute: 3 },
  { id: 'weightlifting', name: '重訓', caloriesPerMinute: 6 },
];

export default function ExerciseTracker() {
  const [selectedExercise, setSelectedExercise] = useState('');
  const [duration, setDuration] = useState('');

  const calculateCalories = () => {
    const exercise = exerciseTypes.find(e => e.id === selectedExercise);
    if (exercise && duration) {
      return exercise.caloriesPerMinute * parseInt(duration);
    }
    return 0;
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">記錄運動</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label htmlFor="exercise-type" className="block text-sm font-medium text-gray-700">
                運動類型
              </label>
              <select
                id="exercise-type"
                value={selectedExercise}
                onChange={(e) => setSelectedExercise(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="">選擇運動類型</option>
                {exerciseTypes.map(type => (
                  <option key={type.id} value={type.id}>{type.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="duration" className="block text-sm font-medium text-gray-700">
                運動時間 (分鐘)
              </label>
              <input
                type="number"
                id="duration"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                placeholder="0"
                min="0"
              />
            </div>

            {selectedExercise && duration && (
              <div className="p-4 bg-green-50 rounded-md">
                <p className="text-green-700">預計消耗卡路里: {calculateCalories()} kcal</p>
              </div>
            )}

            <button
              type="button"
              className="w-full flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              新增記錄
            </button>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-medium text-gray-900 mb-4">本週運動統計</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm text-gray-600">
                  <span>總運動時間</span>
                  <span>180 分鐘</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                  <div className="bg-indigo-600 h-2.5 rounded-full" style={{ width: '60%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm text-gray-600">
                  <span>消耗卡路里</span>
                  <span>1,200 kcal</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                  <div className="bg-green-600 h-2.5 rounded-full" style={{ width: '40%' }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 運動記錄 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">最近的運動記錄</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">日期</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">運動類型</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">時間 (分鐘)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">消耗卡路里</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2025-04-21</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">跑步</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">30</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">300</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2025-04-20</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">重訓</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">45</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">270</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
