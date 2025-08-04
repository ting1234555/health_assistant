// API 服務配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://huggingface.co/spaces/yuting111222/health-assistant';

class ApiService {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    // 通用請求方法
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // 健康檢查
    async healthCheck() {
        return this.makeRequest('/health');
    }

    // 食物分析
    async analyzeFood(imageUrl = null, foodName = null) {
        const payload = {};
        
        if (imageUrl) payload.image_url = imageUrl;
        if (foodName) payload.food_name = foodName;

        return this.makeRequest('/api/analyze-food', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
    }

    // 營養查詢
    async getNutrition(foodName) {
        return this.makeRequest(`/api/nutrition/${encodeURIComponent(foodName)}`);
    }

    // 獲取系統日誌
    async getLogs() {
        return this.makeRequest('/api/logs');
    }

    // 上傳圖片並分析
    async uploadAndAnalyze(file) {
        // 將文件轉換為 base64 或上傳到臨時存儲
        const imageUrl = await this.uploadImage(file);
        return this.analyzeFood(imageUrl);
    }

    // 上傳圖片（模擬）
    async uploadImage(file) {
        // 這裡可以實現真實的圖片上傳邏輯
        // 目前返回一個模擬的 URL
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = () => {
                resolve(reader.result);
            };
            reader.readAsDataURL(file);
        });
    }
}

// 創建單例實例
const apiService = new ApiService();

export default apiService; 