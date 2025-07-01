import React from 'react';

export default function Login() {
  return (
    <div className="bg-white p-6 rounded-lg shadow max-w-md mx-auto mt-10">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">登入</h2>
      <form className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">帳號</label>
          <input className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" type="text" placeholder="請輸入帳號" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">密碼</label>
          <input className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" type="password" placeholder="請輸入密碼" />
        </div>
        <button type="submit" className="w-full px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">登入</button>
      </form>
    </div>
  );
}
