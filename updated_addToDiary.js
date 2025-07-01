// 將食物加入飲食記錄
function addToDiary(foodName) {
    if (!foodName) {
        console.warn('無法加入空的食物名稱');
        return false;
    }
    
    try {
        // 確保 dailyMeals 是陣列
        if (!Array.isArray(dailyMeals)) {
            dailyMeals = [];
        }
        
        const today = new Date().toISOString().split('T')[0];
        const now = new Date();
        
        // 從營養資料庫獲取食物資訊，如果沒有則使用預設值
        const foodInfo = nutritionDatabase[foodName] || {
            calories: 200,
            protein: 10,
            carbs: 30,
            fat: 5,
            fiber: 2,
            sugar: 5
        };
        
        const meal = {
            id: Date.now(),
            name: foodName,
            ...foodInfo,  // 展開營養資訊
            date: today,
            time: now.toLocaleTimeString('zh-TW', {hour: '2-digit', minute:'2-digit'}),
            timestamp: now.toISOString()
        };
        
        // 加入飲食記錄
        dailyMeals.push(meal);
        
        // 儲存到 localStorage
        localStorage.setItem('dailyMeals', JSON.stringify(dailyMeals));
        
        // 顯示成功訊息
        showNotification(`已將「${foodName}」加入飲食記錄`, 'success');
        
        // 更新 UI
        if (typeof updateMealsList === 'function') {
            updateMealsList();
        }
        
        if (typeof updateTrackingStats === 'function') {
            updateTrackingStats();
        }
        
        // 觸發自定義事件，通知其他組件
        document.dispatchEvent(new CustomEvent('mealAdded', { detail: meal }));
        
        return true;
        
    } catch (error) {
        console.error('加入飲食記錄失敗:', error);
        showNotification('加入飲食記錄時發生錯誤', 'error');
        return false;
    }
}

// 顯示通知訊息
function showNotification(message, type = 'info') {
    // 檢查是否已經存在通知容器
    let notificationContainer = document.getElementById('notification-container');
    
    if (!notificationContainer) {
        // 創建通知容器
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.style.position = 'fixed';
        notificationContainer.style.top = '20px';
        notificationContainer.style.right = '20px';
        notificationContainer.style.zIndex = '1000';
        document.body.appendChild(notificationContainer);
    }
    
    // 創建通知元素
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.padding = '12px 20px';
    notification.style.marginBottom = '10px';
    notification.style.borderRadius = '4px';
    notification.style.color = 'white';
    notification.style.opacity = '0';
    notification.style.transition = 'opacity 0.3s ease-in-out';
    notification.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
    
    // 根據類型設置背景色
    const colors = {
        success: '#4CAF50',
        error: '#F44336',
        warning: '#FF9800',
        info: '#2196F3'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    notification.textContent = message;
    
    // 添加到容器
    notificationContainer.appendChild(notification);
    
    // 觸發動畫
    setTimeout(() => {
        notification.style.opacity = '1';
    }, 10);
    
    // 3秒後自動移除
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
            // 如果容器為空，則移除容器
            if (notificationContainer && notificationContainer.children.length === 0) {
                notificationContainer.remove();
            }
        }, 300);
    }, 3000);
}
