/**
 * US Market Smart Money Alpha Platform
 * Frontend Application Logic
 */

// ============================================
// Global Variables & State Management
// ============================================

// Language state (ko/en) - persisted in localStorage
window.currentLang = localStorage.getItem('appLang') || 'ko';

// AI Model state (gemini/gpt) - persisted in localStorage
window.currentModel = localStorage.getItem('appModel') || 'gemini';

// Lightweight Charts instance for stock chart
window.usStockChart = null;

// Current selected stock pick for chart display
window.currentChartPick = null;

// Technical indicators state
window.indicatorState = {
    rsi: false,
    macd: false,
    bb: false,  // Bollinger Bands
    sr: false   // Support/Resistance
};

// Chart period state
window.currentChartPeriod = '6M';

// Update intervals
window.realtimePriceInterval = null;
window.macroAnalysisInterval = null;

// API base URL
window.API_BASE = '';

// i18n translations
window.i18n = {
    ko: {
        'dashboard': '대시보드',
        'smartMoney': 'Smart Money Picks',
        'macro': '매크로 분석',
        'etfFlows': 'ETF 자금 흐름',
        'calendar': '경제 캘린더',
        'portfolio': '포트폴리오',
        'marketOverview': '시장 개요',
        'analysis': '분석',
        'sectors': '섹터',
        'lastUpdate': '마지막 업데이트',
        'dataSource': '데이터 소스',
        'aiModel': 'AI 모델',
        'language': '언어',
        'realTime': '실시간',
        'top10': '상위 10개',
        'priceChart': '가격 차트',
        'aiSummary': 'AI 요약',
        'macroAnalysis': '매크로 분석',
        'economicCalendar': '경제 캘린더',
        'loading': '로딩 중...',
        'error': '오류',
        'noData': '데이터 없음'
    },
    en: {
        'dashboard': 'Dashboard',
        'smartMoney': 'Smart Money Picks',
        'macro': 'Macro Analysis',
        'etfFlows': 'ETF Flows',
        'calendar': 'Economic Calendar',
        'portfolio': 'Portfolio',
        'marketOverview': 'Market Overview',
        'analysis': 'Analysis',
        'sectors': 'Sectors',
        'lastUpdate': 'Last Update',
        'dataSource': 'Data Source',
        'aiModel': 'AI Model',
        'language': 'Language',
        'realTime': 'Real-time',
        'top10': 'Top 10',
        'priceChart': 'Price Chart',
        'aiSummary': 'AI Summary',
        'macroAnalysis': 'Macro Analysis',
        'economicCalendar': 'Economic Calendar',
        'loading': 'Loading...',
        'error': 'Error',
        'noData': 'No Data'
    }
};

// ============================================
// Utility Functions
// ============================================

/**
 * Save state to localStorage
 */
window.saveState = function() {
    localStorage.setItem('appLang', window.currentLang);
    localStorage.setItem('appModel', window.currentModel);
};

/**
 * Load state from localStorage
 */
window.loadState = function() {
    window.currentLang = localStorage.getItem('appLang') || 'ko';
    window.currentModel = localStorage.getItem('appModel') || 'gemini';
};

/**
 * Format number with commas
 */
window.formatNumber = function(num) {
    if (num === null || num === undefined || isNaN(num)) return 'N/A';
    return Number(num).toLocaleString('en-US', { 
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2 
    });
};

/**
 * Format percentage
 */
window.formatPercent = function(num) {
    if (num === null || num === undefined || isNaN(num)) return 'N/A';
    const sign = num >= 0 ? '+' : '';
    return `${sign}${Number(num).toFixed(2)}%`;
};

/**
 * Get color class based on value
 */
window.getColorClass = function(value) {
    if (value === null || value === undefined || isNaN(value)) return 'text-gray-400';
    return value >= 0 ? 'text-green' : 'text-red';
};

/**
 * Translate UI elements
 */
window.translateUI = function() {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (window.i18n[window.currentLang] && window.i18n[window.currentLang][key]) {
            el.textContent = window.i18n[window.currentLang][key];
        }
    });
};

/**
 * Log error with context
 */
window.logError = function(context, error) {
    console.error(`[${context}]`, error);
    // Could send to error tracking service here
};

/**
 * Fetch API with error handling
 */
window.fetchAPI = async function(endpoint, options = {}) {
    try {
        const response = await fetch(`${window.API_BASE}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        window.logError(`API: ${endpoint}`, error);
        throw error;
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        currentLang,
        currentModel,
        usStockChart,
        currentChartPick,
        indicatorState,
        currentChartPeriod,
        saveState,
        loadState,
        formatNumber,
        formatPercent,
        getColorClass,
        translateUI,
        fetchAPI,
        i18n
    };
}

