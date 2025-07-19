#!/bin/bash

# 部署腳本 - 確保代碼推送到 GitHub 和 Hugging Face Spaces

echo "🚀 開始部署流程..."

# 檢查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 發現未提交的更改，正在添加..."
    git add .
    
    echo "💾 提交更改..."
    git commit -m "Auto-deploy: $(date)"
else
    echo "✅ 沒有未提交的更改"
fi

# 推送到 GitHub
echo "📤 推送到 GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ GitHub 推送成功！"
    echo ""
    echo "🔗 GitHub 倉庫: https://github.com/ting1234555/health_assistant"
    echo "🔗 Hugging Face Space: https://huggingface.co/spaces/yuting111222/health-assistant"
    echo ""
    echo "📋 下一步操作："
    echo "1. 訪問 Hugging Face Spaces 設定頁面"
    echo "2. 點擊 'Factory rebuild' 按鈕"
    echo "3. 等待重建完成（1-5分鐘）"
    echo "4. 檢查 /docs 頁面確認 API 端點"
    echo ""
    echo "🎯 部署完成！"
else
    echo "❌ GitHub 推送失敗！"
    exit 1
fi 