# 部署腳本 - 確保代碼推送到 GitHub 和 Hugging Face Spaces

Write-Host "🚀 開始部署流程..." -ForegroundColor Green

# 檢查是否有未提交的更改
$status = git status --porcelain
if ($status) {
    Write-Host "📝 發現未提交的更改，正在添加..." -ForegroundColor Yellow
    git add .
    
    Write-Host "💾 提交更改..." -ForegroundColor Yellow
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git commit -m "Auto-deploy: $timestamp"
} else {
    Write-Host "✅ 沒有未提交的更改" -ForegroundColor Green
}

# 推送到 GitHub
Write-Host "📤 推送到 GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ GitHub 推送成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔗 GitHub 倉庫: https://github.com/ting1234555/health_assistant" -ForegroundColor Cyan
    Write-Host "🔗 Hugging Face Space: https://huggingface.co/spaces/yuting111222/health-assistant" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 下一步操作：" -ForegroundColor Yellow
    Write-Host "1. 訪問 Hugging Face Spaces 設定頁面" -ForegroundColor White
    Write-Host "2. 點擊 'Factory rebuild' 按鈕" -ForegroundColor White
    Write-Host "3. 等待重建完成（1-5分鐘）" -ForegroundColor White
    Write-Host "4. 檢查 /docs 頁面確認 API 端點" -ForegroundColor White
    Write-Host ""
    Write-Host "🎯 部署完成！" -ForegroundColor Green
} else {
    Write-Host "❌ GitHub 推送失敗！" -ForegroundColor Red
    exit 1
} 