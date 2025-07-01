import React from 'react';
import { useState } from 'react';
import { PlusIcon, MinusIcon } from '@heroicons/react/24/outline';

export default function WaterTracker() {
  const [waterIntake, setWaterIntake] = useState(0);
  const goal = 2000; // 每日目標 (ml)

  const addWater = (amount) => {
    setWaterIntake(prev => Math.min(prev + amount, 5000));
  };

  const removeWater = (amount) => {
    setWaterIntake(prev => Math.max(prev - amount, 0));
  };

  const progress = (waterIntake / goal) * 100;

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">今日飲水追蹤</h2>

        {/* 進度顯示 */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">目前進度</span>
            <span className="text-sm font-medium text-gray-700">{waterIntake} / {goal} ml</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div
              className="bg-blue-600 h-4 rounded-full transition-all duration-300"
              style={{ width: `${Math.min(progress, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* 快速添加按鈕 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <button
            onClick={() => addWater(200)}
            className="flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            200ml
          </button>
          <button
            onClick={() => addWater(300)}
            className="flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            300ml
          </button>
          <button
            onClick={() => addWater(500)}
            className="flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            500ml
          </button>
          <button
            onClick={() => removeWater(200)}
            className="flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
          >
            <MinusIcon className="h-5 w-5 mr-2" />
            取消
          </button>
        </div>

        {/* 自定義輸入 */}
        <div className="flex gap-4">
          <div className="flex-1">
            <label htmlFor="custom-amount" className="block text-sm font-medium text-gray-700">
              自定義添加量 (ml)
            </label>
            <input
              type="number"
              id="custom-amount"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              placeholder="輸入毫升數"
              min="0"
              step="50"
            />
          </div>
          <button
            className="mt-7 px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            添加
          </button>
        </div>
      </div>

      {/* 今日記錄 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">今日記錄</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">時間</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">數量 (ml)</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">14:30</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">300</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">12:00</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">500</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">09:15</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">200</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
