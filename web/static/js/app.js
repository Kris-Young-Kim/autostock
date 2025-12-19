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

// ============================================
// Initialization Functions
// ============================================

/**
 * Initialize the application
 * Called on DOMContentLoaded
 */
window.initApp = function() {
    console.log('🚀 Initializing US Market Smart Money Alpha Platform...');
    
    // Load saved state from localStorage
    loadState();
    console.log(`📝 Loaded state - Language: ${window.currentLang}, Model: ${window.currentModel}`);
    
    // Update UI with loaded state
    updateUIState();
    
    // Register event listeners
    registerEventListeners();
    
    // Initialize dashboard data
    if (typeof updateUSMarketDashboard === 'function') {
        updateUSMarketDashboard().catch(error => {
            logError('Dashboard initialization', error);
        });
    }
    
    // Initialize macro analysis (separate from main dashboard)
    if (typeof reloadMacroAnalysis === 'function') {
        reloadMacroAnalysis().catch(error => {
            logError('Macro analysis initialization', error);
        });
    }
    
    // Set up real-time update intervals
    setupUpdateIntervals();
    
    // Translate UI
    translateUI();
    
    console.log('✅ Application initialized successfully');
};

/**
 * Update UI elements with current state
 */
window.updateUIState = function() {
    // Update language display
    const langText = document.getElementById('lang-text');
    const footerLang = document.getElementById('footer-lang');
    if (langText) langText.textContent = window.currentLang.toUpperCase();
    if (footerLang) footerLang.textContent = window.currentLang.toUpperCase();
    
    // Update AI model display
    const aiModelBtn = document.getElementById('ai-model-btn');
    if (aiModelBtn) {
        const modelText = window.currentModel.charAt(0).toUpperCase() + window.currentModel.slice(1);
        const span = aiModelBtn.querySelector('span');
        if (span) span.textContent = modelText;
    }
    
    // Update footer AI model display
    const footerModel = document.querySelector('#fnb span:contains("Gemini")');
    // Note: This is a placeholder, actual implementation depends on footer structure
};

/**
 * Register all event listeners
 */
window.registerEventListeners = function() {
    // SNB Toggle
    const snbToggle = document.getElementById('snb-toggle');
    if (snbToggle) {
        snbToggle.addEventListener('click', function() {
            const snb = document.getElementById('snb');
            if (snb) snb.classList.toggle('show');
        });
    }
    
    // Close SNB when clicking outside on mobile
    if (window.innerWidth <= 1023) {
        document.addEventListener('click', function(e) {
            const snb = document.getElementById('snb');
            const toggle = document.getElementById('snb-toggle');
            if (snb && toggle && 
                !snb.contains(e.target) && 
                !toggle.contains(e.target) && 
                snb.classList.contains('show')) {
                snb.classList.remove('show');
            }
        });
    }
    
    // Accordion functionality
    document.querySelectorAll('.accordion-header').forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            const icon = this.querySelector('i');
            if (content) {
                content.classList.toggle('open');
                if (icon) icon.classList.toggle('rotate-180');
            }
        });
    });
    
    // Modal functionality
    const aiModelBtn = document.getElementById('ai-model-btn');
    const closeModalBtn = document.getElementById('close-modal');
    const aiModelModal = document.getElementById('ai-model-modal');
    
    if (aiModelBtn && aiModelModal) {
        aiModelBtn.addEventListener('click', function() {
            aiModelModal.classList.add('show');
        });
    }
    
    if (closeModalBtn && aiModelModal) {
        closeModalBtn.addEventListener('click', function() {
            aiModelModal.classList.remove('show');
        });
    }
    
    // Close modal on overlay click
    if (aiModelModal) {
        aiModelModal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('show');
            }
        });
    }
    
    // AI Model Selection
    if (aiModelModal) {
        aiModelModal.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', function() {
                const modelText = this.querySelector('.font-medium')?.textContent.toLowerCase();
                if (modelText) {
                    window.currentModel = modelText.includes('gemini') ? 'gemini' : 'gpt';
                    saveState();
                    
                    // Update UI
                    if (aiModelBtn) {
                        const span = aiModelBtn.querySelector('span');
                        if (span) {
                            span.textContent = modelText.charAt(0).toUpperCase() + modelText.slice(1);
                        }
                    }
                    
                    aiModelModal.classList.remove('show');
                    
                    // Reload macro analysis with new model
                    if (typeof reloadMacroAnalysis === 'function') {
                        reloadMacroAnalysis();
                    }
                }
            });
        });
    }
    
    // Tab switching
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.nav-tab').forEach(t => {
                t.classList.remove('active', 'text-white', 'border-white');
                t.classList.add('text-gray-400', 'border-transparent');
            });
            this.classList.add('active', 'text-white', 'border-white');
            this.classList.remove('text-gray-400', 'border-transparent');
            
            // Handle tab content switching
            const tabName = this.getAttribute('data-tab');
            if (tabName && typeof switchTab === 'function') {
                switchTab(tabName);
            }
        });
    });
    
    // Language toggle
    const langToggle = document.getElementById('lang-toggle');
    if (langToggle) {
        langToggle.addEventListener('click', function() {
            window.currentLang = window.currentLang === 'ko' ? 'en' : 'ko';
            saveState();
            
            // Update UI
            const langText = document.getElementById('lang-text');
            const footerLang = document.getElementById('footer-lang');
            if (langText) langText.textContent = window.currentLang.toUpperCase();
            if (footerLang) footerLang.textContent = window.currentLang.toUpperCase();
            
            // Translate UI
            translateUI();
            
            // Reload data with new language
            if (typeof updateUSMarketDashboard === 'function') {
                updateUSMarketDashboard();
            }
            if (typeof reloadMacroAnalysis === 'function') {
                reloadMacroAnalysis();
            }
        });
    }
    
    // Chart period buttons
    document.querySelectorAll('.chart-period-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const period = this.getAttribute('data-period');
            if (period) {
                window.currentChartPeriod = period;
                
                // Update button states
                document.querySelectorAll('.chart-period-btn').forEach(b => {
                    b.classList.remove('text-white', 'bg-tertiary');
                    b.classList.add('text-gray-400');
                });
                this.classList.add('text-white', 'bg-tertiary');
                this.classList.remove('text-gray-400');
                
                // Reload chart if a stock is selected
                if (window.currentChartPick && typeof loadUSStockChart === 'function') {
                    loadUSStockChart(window.currentChartPick, null, period);
                }
            }
        });
    });
    
    // Indicator toggle buttons
    document.querySelectorAll('.indicator-toggle').forEach(btn => {
        btn.addEventListener('click', function() {
            const indicator = this.getAttribute('data-indicator');
            if (indicator && typeof toggleIndicator === 'function') {
                toggleIndicator(indicator);
            }
        });
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        const snb = document.getElementById('snb');
        if (snb && window.innerWidth >= 1024) {
            snb.classList.remove('show');
        }
        
        // Resize chart if exists
        if (window.usStockChart && typeof window.usStockChart.resize === 'function') {
            const container = document.getElementById('chart-container');
            if (container) {
                window.usStockChart.resize(container.clientWidth, container.clientHeight);
            }
        }
    });
    
    console.log('📌 Event listeners registered');
};

/**
 * Set up real-time update intervals
 */
window.setupUpdateIntervals = function() {
    // Clear existing intervals
    if (window.realtimePriceInterval) {
        clearInterval(window.realtimePriceInterval);
    }
    if (window.macroAnalysisInterval) {
        clearInterval(window.macroAnalysisInterval);
    }
    
    // Real-time price updates (20 seconds)
    if (typeof updateRealtimePrices === 'function') {
        window.realtimePriceInterval = setInterval(() => {
            updateRealtimePrices().catch(error => {
                logError('Real-time price update', error);
            });
        }, 20000); // 20 seconds
        console.log('⏱️ Real-time price updates: 20s interval');
    }
    
    // Macro analysis refresh (10 minutes)
    if (typeof reloadMacroAnalysis === 'function') {
        window.macroAnalysisInterval = setInterval(() => {
            reloadMacroAnalysis().catch(error => {
                logError('Macro analysis refresh', error);
            });
        }, 600000); // 10 minutes
        console.log('⏱️ Macro analysis refresh: 10min interval');
    }
    
    // Update time display (1 second)
    const updateTime = function() {
        const timeEl = document.getElementById('last-update-time');
        if (timeEl) {
            const now = new Date();
            timeEl.textContent = now.toLocaleTimeString();
        }
    };
    updateTime();
    setInterval(updateTime, 1000);
};

/**
 * Cleanup function (called on page unload)
 */
window.cleanupApp = function() {
    // Clear intervals
    if (window.realtimePriceInterval) {
        clearInterval(window.realtimePriceInterval);
        window.realtimePriceInterval = null;
    }
    if (window.macroAnalysisInterval) {
        clearInterval(window.macroAnalysisInterval);
        window.macroAnalysisInterval = null;
    }
    
    // Destroy chart if exists
    if (window.usStockChart && typeof window.usStockChart.remove === 'function') {
        window.usStockChart.remove();
        window.usStockChart = null;
    }
    
    console.log('🧹 Application cleaned up');
};

// ============================================
// Data Fetching Functions
// ============================================

/**
 * Update US Market Dashboard
 * Fetches and renders all major dashboard sections in parallel
 */
window.updateUSMarketDashboard = async function() {
    console.log('📊 Updating US Market Dashboard...');
    
    try {
        // Parallel data fetching using Promise.all
        const [portfolioData, smartMoneyData, etfFlowsData, historyDatesData] = await Promise.all([
            fetchAPI('/api/us/portfolio').catch(err => {
                logError('Portfolio data', err);
                return null;
            }),
            fetchAPI('/api/us/smart-money').catch(err => {
                logError('Smart Money data', err);
                return null;
            }),
            fetchAPI('/api/us/etf-flows').catch(err => {
                logError('ETF Flows data', err);
                return null;
            }),
            fetchAPI('/api/us/history-dates').catch(err => {
                logError('History dates', err);
                return null;
            })
        ]);
        
        // Render each section
        if (portfolioData && typeof renderUSMarketIndices === 'function') {
            renderUSMarketIndices(portfolioData);
        }
        
        if (smartMoneyData && typeof renderUSSmartMoneyPicks === 'function') {
            renderUSSmartMoneyPicks(smartMoneyData);
        }
        
        if (etfFlowsData && typeof renderUSETFFlows === 'function') {
            renderUSETFFlows(etfFlowsData);
        }
        
        // Store history dates for later use
        if (historyDatesData && historyDatesData.dates) {
            window.availableHistoryDates = historyDatesData.dates;
        }
        
        console.log('✅ Dashboard updated successfully');
        
        return {
            portfolio: portfolioData,
            smartMoney: smartMoneyData,
            etfFlows: etfFlowsData,
            historyDates: historyDatesData
        };
        
    } catch (error) {
        logError('Dashboard update', error);
        throw error;
    }
};

/**
 * Reload Macro Analysis
 * Refreshes macro analysis section separately (may take longer due to AI)
 */
window.reloadMacroAnalysis = async function() {
    console.log('🌍 Reloading Macro Analysis...');
    
    try {
        const params = new URLSearchParams({
            lang: window.currentLang,
            model: window.currentModel
        });
        
        const data = await fetchAPI(`/api/us/macro-analysis?${params.toString()}`);
        
        if (data && typeof renderUSMacroAnalysis === 'function') {
            renderUSMacroAnalysis(data);
        }
        
        console.log('✅ Macro analysis reloaded');
        
        return data;
        
    } catch (error) {
        logError('Macro analysis reload', error);
        throw error;
    }
};

/**
 * Update Real-time Prices
 * Updates prices for visible stocks in the table and chart
 */
window.updateRealtimePrices = async function() {
    try {
        // Collect visible tickers from the Smart Money Picks table
        const tableBody = document.getElementById('picks-table-body');
        if (!tableBody) {
            console.debug('No picks table found, skipping real-time update');
            return;
        }
        
        const rows = tableBody.querySelectorAll('tr[data-ticker]');
        if (rows.length === 0) {
            console.debug('No ticker rows found, skipping real-time update');
            return;
        }
        
        // Extract tickers from table rows
        const tickers = Array.from(rows).map(row => row.getAttribute('data-ticker'));
        
        if (tickers.length === 0) {
            return;
        }
        
        // Fetch real-time prices
        const response = await fetchAPI('/api/realtime-prices', {
            method: 'POST',
            body: JSON.stringify({ tickers: tickers })
        });
        
        if (!response.success || !response.prices) {
            console.warn('Real-time price update failed:', response);
            return;
        }
        
        // Update table cells
        response.prices.forEach(priceData => {
            const row = tableBody.querySelector(`tr[data-ticker="${priceData.ticker}"]`);
            if (!row) return;
            
            // Update price cell
            const priceCell = row.querySelector('.price-cell');
            if (priceCell) {
                const oldPrice = parseFloat(priceCell.textContent.replace(/,/g, '')) || 0;
                const newPrice = priceData.price;
                
                priceCell.textContent = formatNumber(newPrice);
                
                // Flash effect for price change
                if (oldPrice > 0 && newPrice !== oldPrice) {
                    priceCell.classList.add('flash');
                    setTimeout(() => priceCell.classList.remove('flash'), 500);
                    
                    // Add color class
                    priceCell.classList.remove('text-green', 'text-red', 'text-gray-400');
                    if (newPrice > oldPrice) {
                        priceCell.classList.add('text-green');
                    } else if (newPrice < oldPrice) {
                        priceCell.classList.add('text-red');
                    }
                }
            }
            
            // Update change cell
            const changeCell = row.querySelector('.change-cell');
            if (changeCell) {
                changeCell.textContent = formatPercent(priceData.change_percent);
                changeCell.classList.remove('text-green', 'text-red', 'text-gray-400');
                changeCell.classList.add(getColorClass(priceData.change_percent));
            }
        });
        
        // Update chart if current ticker matches
        if (window.currentChartPick && window.usStockChart) {
            const currentTicker = window.currentChartPick.ticker;
            const priceData = response.prices.find(p => p.ticker === currentTicker);
            
            if (priceData && typeof updateChartLastCandle === 'function') {
                updateChartLastCandle(priceData);
            }
        }
        
        console.debug(`✅ Updated ${response.prices.length} prices`);
        
    } catch (error) {
        logError('Real-time price update', error);
        // Don't throw - this is a background update, failures shouldn't break the app
    }
};

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initApp);
} else {
    // DOM is already ready
    window.initApp();
}

// Cleanup on page unload
window.addEventListener('beforeunload', window.cleanupApp);

