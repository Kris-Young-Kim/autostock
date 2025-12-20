/**
 * Rendering Functions
 * Functions for rendering dashboard components
 */

// ============================================
// Market Indices Rendering
// ============================================

/**
 * Render US Market Indices
 * @param {Object} data - Portfolio data from API
 */
window.renderUSMarketIndices = function(data) {
    const container = document.getElementById('indices-grid');
    if (!container) {
        console.warn('Indices grid container not found');
        return;
    }
    
    if (!data || !data.indices || data.indices.length === 0) {
        container.innerHTML = '<div class="col-span-full text-center text-gray-500 py-8">No market data available</div>';
        return;
    }
    
    container.innerHTML = data.indices.map(index => {
        const changeClass = getColorClass(index.change);
        const changeIcon = index.change >= 0 ? '▲' : '▼';
        
        return `
            <div class="bg-secondary border border-card rounded p-4 hover:border-accent-blue transition-colors cursor-pointer">
                <div class="text-xs text-gray-400 mb-1">${index.name}</div>
                <div class="text-lg font-bold text-white mb-1">${formatNumber(index.price)}</div>
                <div class="text-sm ${changeClass} flex items-center gap-1">
                    <span>${changeIcon}</span>
                    <span>${formatPercent(index.change)}</span>
                </div>
            </div>
        `;
    }).join('');
    
    console.log(`✅ Rendered ${data.indices.length} market indices`);
};

// ============================================
// Smart Money Picks Rendering
// ============================================

/**
 * Render Smart Money Picks Table
 * @param {Object} data - Smart Money data from API
 */
window.renderUSSmartMoneyPicks = function(data) {
    const tableBody = document.getElementById('picks-table-body');
    if (!tableBody) {
        console.warn('Picks table body not found');
        return;
    }
    
    if (!data || !data.top_picks || data.top_picks.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center text-gray-500 py-8">No picks available</td></tr>';
        return;
    }
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Render each pick
    data.top_picks.forEach((pick, index) => {
        const rank = index + 1;
        const ticker = pick.ticker || 'N/A';
        const name = pick.name || pick.ticker || 'N/A';
        const score = pick.final_score || pick.composite_score || 0;
        const price = pick.current_price || pick.price || 0;
        const change = pick.change_since_rec || 0;
        const sector = pick.sector || 'Unknown';
        
        // Translate name and sector to Korean if needed
        const translatedName = typeof translateStockName === 'function' 
            ? translateStockName(name, ticker) 
            : name;
        const translatedSector = typeof translateSector === 'function' 
            ? translateSector(sector) 
            : sector;
        
        const changeClass = getColorClass(change);
        const changeIcon = change >= 0 ? '▲' : '▼';
        
        // Score color coding
        let scoreClass = 'text-gray-400';
        if (score >= 80) scoreClass = 'text-accent-blue font-bold';
        else if (score >= 60) scoreClass = 'text-accent-green';
        else if (score >= 40) scoreClass = 'text-accent-yellow';
        else scoreClass = 'text-gray-400';
        
        const row = document.createElement('tr');
        row.setAttribute('data-ticker', ticker);
        row.className = 'hover:bg-tertiary cursor-pointer transition-colors';
        
        row.innerHTML = `
            <td class="font-medium">${rank}</td>
            <td class="font-mono font-bold text-accent-blue">${ticker}</td>
            <td class="text-white">${translatedName}</td>
            <td class="text-right ${scoreClass}">${score.toFixed(1)}</td>
            <td class="text-right price-cell text-white">${formatNumber(price)}</td>
            <td class="text-right change-cell ${changeClass}">
                <span>${changeIcon}</span>
                <span>${formatPercent(change)}</span>
            </td>
            <td class="text-center">
                <span class="px-2 py-1 rounded text-xs bg-tertiary">${translatedSector}</span>
            </td>
        `;
        
        // Add click event listener
        row.addEventListener('click', function() {
            // Remove previous selection
            tableBody.querySelectorAll('tr').forEach(r => {
                r.classList.remove('bg-tertiary', 'border-l-2', 'border-accent-blue');
            });
            
            // Highlight selected row
            this.classList.add('bg-tertiary', 'border-l-2', 'border-accent-blue');
            
            // Load chart for this pick
            if (typeof loadUSStockChart === 'function') {
                loadUSStockChart(pick, index, window.currentChartPeriod);
            }
        });
        
        tableBody.appendChild(row);
    });
    
    console.log(`✅ Rendered ${data.top_picks.length} smart money picks`);
};

// ============================================
// Macro Analysis Rendering
// ============================================

/**
 * Render Macro Analysis
 * @param {Object} data - Macro analysis data from API
 */
window.renderUSMacroAnalysis = function(data) {
    if (!data) {
        console.warn('No macro analysis data');
        return;
    }
    
    // Render macro indicators grid
    const indicatorsContainer = document.getElementById('macro-indicators');
    if (indicatorsContainer && data.indicators) {
        const indicators = data.indicators;
        
        indicatorsContainer.innerHTML = Object.entries(indicators).map(([key, indicator]) => {
            if (!indicator || typeof indicator !== 'object') return '';
            
            const name = indicator.name || key;
            const value = indicator.current || indicator.value || 'N/A';
            const change = indicator.change || 0;
            const changeClass = getColorClass(change);
            const changeIcon = change >= 0 ? '▲' : '▼';
            
            // Special styling for different indicator types
            let bgClass = 'bg-tertiary';
            if (key.toLowerCase().includes('vix') || key.toLowerCase().includes('volatility')) {
                bgClass = 'bg-purple-900 bg-opacity-30';
            } else if (key.toLowerCase().includes('crypto') || key.toLowerCase().includes('btc')) {
                bgClass = 'bg-yellow-900 bg-opacity-30';
            } else if (key.toLowerCase().includes('yield') || key.toLowerCase().includes('rate')) {
                bgClass = 'bg-blue-900 bg-opacity-30';
            }
            
            return `
                <div class="${bgClass} border border-card rounded p-3">
                    <div class="text-xs text-gray-400 mb-1">${name}</div>
                    <div class="text-lg font-bold text-white mb-1">${typeof value === 'number' ? formatNumber(value) : value}</div>
                    <div class="text-sm ${changeClass} flex items-center gap-1">
                        <span>${changeIcon}</span>
                        <span>${formatPercent(change)}</span>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    // Render AI analysis text
    const analysisContainer = document.getElementById('macro-analysis-text');
    if (analysisContainer) {
        let analysisText = '';
        
        if (window.currentLang === 'en' && data.ai_analysis_en) {
            analysisText = data.ai_analysis_en;
        } else if (data.ai_analysis) {
            analysisText = data.ai_analysis;
        } else if (data.analysis) {
            analysisText = data.analysis;
        }
        
        if (analysisText) {
            analysisContainer.innerHTML = `<div class="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">${analysisText}</div>`;
        } else {
            analysisContainer.innerHTML = '<div class="text-sm text-gray-500 italic">No analysis available</div>';
        }
    }
    
    console.log('✅ Rendered macro analysis');
};

// ============================================
// ETF Flows Rendering
// ============================================

/**
 * Render ETF Flows
 * @param {Object} data - ETF flows data from API
 */
window.renderUSETFFlows = function(data) {
    const container = document.getElementById('etf-flows-content');
    if (!container) {
        console.warn('ETF flows container not found');
        return;
    }
    
    if (!data) {
        container.innerHTML = '<div class="text-sm text-gray-500">No ETF flow data available</div>';
        return;
    }
    
    let html = '';
    
    // Market sentiment score
    if (data.market_sentiment_score !== undefined) {
        const sentiment = data.market_sentiment_score;
        const sentimentClass = sentiment >= 60 ? 'text-green' : sentiment >= 40 ? 'text-yellow' : 'text-red';
        
        html += `
            <div class="mb-4 p-3 bg-tertiary rounded">
                <div class="text-xs text-gray-400 mb-1">Market Sentiment</div>
                <div class="text-2xl font-bold ${sentimentClass}">${sentiment.toFixed(1)}</div>
            </div>
        `;
    }
    
    // Top inflows
    if (data.top_inflows && data.top_inflows.length > 0) {
        html += '<div class="mb-4"><div class="text-sm font-bold text-white mb-2">Top Inflows</div>';
        html += '<div class="space-y-2">';
        data.top_inflows.forEach(etf => {
            const flowScore = etf.flow_score || 0;
            html += `
                <div class="flex items-center justify-between p-2 bg-tertiary rounded">
                    <span class="text-sm text-white">${etf.ticker || etf.name || 'N/A'}</span>
                    <span class="text-sm text-green font-bold">+${flowScore.toFixed(1)}</span>
                </div>
            `;
        });
        html += '</div></div>';
    }
    
    // Top outflows
    if (data.top_outflows && data.top_outflows.length > 0) {
        html += '<div class="mb-4"><div class="text-sm font-bold text-white mb-2">Top Outflows</div>';
        html += '<div class="space-y-2">';
        data.top_outflows.forEach(etf => {
            const flowScore = etf.flow_score || 0;
            html += `
                <div class="flex items-center justify-between p-2 bg-tertiary rounded">
                    <span class="text-sm text-white">${etf.ticker || etf.name || 'N/A'}</span>
                    <span class="text-sm text-red font-bold">${flowScore.toFixed(1)}</span>
                </div>
            `;
        });
        html += '</div></div>';
    }
    
    // AI analysis
    if (data.ai_analysis) {
        html += `
            <div class="mt-4 p-3 bg-tertiary rounded">
                <div class="text-xs text-gray-400 mb-2">AI Analysis</div>
                <div class="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">${data.ai_analysis}</div>
            </div>
        `;
    }
    
    container.innerHTML = html || '<div class="text-sm text-gray-500">No ETF flow data available</div>';
    
    console.log('✅ Rendered ETF flows');
};

// ============================================
// Options Flow Rendering
// ============================================

/**
 * Render Options Flow
 * @param {Object} data - Options flow data from API
 */
window.renderUSOptionsFlow = function(data) {
    const container = document.getElementById('options-flow-content');
    if (!container) {
        console.warn('Options flow container not found');
        return;
    }
    
    if (!data || !data.options_flow || data.options_flow.length === 0) {
        container.innerHTML = '<div class="text-center py-12"><i class="fas fa-chart-bar text-6xl text-gray-600 mb-4"></i><p class="text-gray-400 text-sm mb-2" data-i18n="optionsFlowComingSoon">옵션 흐름 데이터가 없습니다</p></div>';
        return;
    }
    
    let html = '';
    
    // Summary stats
    if (data.total_tickers) {
        html += `
            <div class="mb-4 p-3 bg-tertiary rounded">
                <div class="text-xs text-gray-400 mb-1">분석 종목 수</div>
                <div class="text-2xl font-bold text-white">${data.total_tickers}</div>
            </div>
        `;
    }
    
    // Options flow table
    html += '<div class="overflow-x-auto"><table class="w-full text-sm">';
    html += '<thead><tr class="border-b border-card text-gray-400">';
    html += '<th class="py-3 text-left" data-i18n="ticker">티커</th>';
    html += '<th class="py-3 text-left">만료일</th>';
    html += '<th class="py-3 text-right">P/C 비율</th>';
    html += '<th class="py-3 text-right">콜 볼륨</th>';
    html += '<th class="py-3 text-right">풋 볼륨</th>';
    html += '<th class="py-3 text-right">비정상 거래</th>';
    html += '<th class="py-3 text-center">센티먼트</th>';
    html += '</tr></thead><tbody class="divide-y divide-card">';
    
    data.options_flow.slice(0, 10).forEach(item => {
        const ticker = item.ticker || 'N/A';
        const expiration = item.expiration || 'N/A';
        const metrics = item.metrics || {};
        const unusual = item.unusual || {};
        const sentiment = item.sentiment || 'Neutral';
        
        const pcRatio = metrics.pc_ratio || 0;
        const callVol = metrics.call_vol || 0;
        const putVol = metrics.put_vol || 0;
        const unusualTotal = unusual.total || 0;
        
        const sentimentClass = sentiment.includes('Bullish') ? 'text-green' : 
                              sentiment.includes('Bearish') ? 'text-red' : 'text-gray-400';
        
        const translatedTicker = typeof translateStockName === 'function' 
            ? translateStockName(ticker, ticker) 
            : ticker;
        
        html += `
            <tr class="hover:bg-tertiary">
                <td class="font-mono font-bold text-accent-blue">${ticker}</td>
                <td class="text-gray-300">${expiration}</td>
                <td class="text-right text-gray-300">${pcRatio.toFixed(3)}</td>
                <td class="text-right text-green">${formatNumber(callVol)}</td>
                <td class="text-right text-red">${formatNumber(putVol)}</td>
                <td class="text-right ${unusualTotal > 10 ? 'text-yellow font-bold' : 'text-gray-300'}">${unusualTotal}</td>
                <td class="text-center ${sentimentClass}">${sentiment}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    
    container.innerHTML = html;
    console.log('✅ Rendered options flow');
};

// ============================================
// Risk Analysis Rendering
// ============================================

/**
 * Render Risk Analysis
 * @param {Object} data - Portfolio risk data from API
 */
window.renderUSRiskAnalysis = function(data) {
    const container = document.getElementById('risk-analysis-content');
    if (!container) {
        console.warn('Risk analysis container not found');
        return;
    }
    
    if (!data || !data.metrics) {
        container.innerHTML = '<div class="text-center py-12"><i class="fas fa-shield-alt text-6xl text-gray-600 mb-4"></i><p class="text-gray-400 text-sm mb-2" data-i18n="riskComingSoon">리스크 분석 데이터가 없습니다</p></div>';
        return;
    }
    
    let html = '';
    const metrics = data.metrics || {};
    
    // Key metrics grid
    html += '<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">';
    
    // Portfolio Volatility
    const volatility = metrics.portfolio_volatility_pct || 0;
    const volatilityClass = volatility < 15 ? 'text-green' : volatility < 25 ? 'text-yellow' : 'text-red';
    html += `
        <div class="bg-tertiary rounded p-4">
            <div class="text-xs text-gray-400 mb-1">포트폴리오 변동성</div>
            <div class="text-2xl font-bold ${volatilityClass}">${volatility.toFixed(2)}%</div>
        </div>
    `;
    
    // Beta
    const beta = metrics.beta || 0;
    const betaClass = beta < 0.8 ? 'text-green' : beta > 1.2 ? 'text-red' : 'text-yellow';
    html += `
        <div class="bg-tertiary rounded p-4">
            <div class="text-xs text-gray-400 mb-1">베타</div>
            <div class="text-2xl font-bold ${betaClass}">${beta.toFixed(2)}</div>
        </div>
    `;
    
    // Diversification Ratio
    const divRatio = metrics.diversification_ratio || 0;
    const divClass = divRatio > 2 ? 'text-green' : divRatio > 1.5 ? 'text-yellow' : 'text-red';
    html += `
        <div class="bg-tertiary rounded p-4">
            <div class="text-xs text-gray-400 mb-1">다각화 비율</div>
            <div class="text-2xl font-bold ${divClass}">${divRatio.toFixed(2)}</div>
        </div>
    `;
    
    // Risk Level
    const riskLevel = metrics.risk_level || 'Unknown';
    const riskClass = riskLevel === 'Low' ? 'text-green' : riskLevel === 'Medium' ? 'text-yellow' : 'text-red';
    html += `
        <div class="bg-tertiary rounded p-4">
            <div class="text-xs text-gray-400 mb-1">리스크 수준</div>
            <div class="text-2xl font-bold ${riskClass}">${riskLevel}</div>
        </div>
    `;
    
    html += '</div>';
    
    // Individual volatilities table
    if (data.individual_volatilities && Object.keys(data.individual_volatilities).length > 0) {
        html += '<div class="mb-4"><h3 class="text-sm font-bold text-white mb-2">개별 종목 변동성</h3>';
        html += '<div class="overflow-x-auto"><table class="w-full text-sm">';
        html += '<thead><tr class="border-b border-card text-gray-400">';
        html += '<th class="py-2 text-left" data-i18n="ticker">티커</th>';
        html += '<th class="py-2 text-right">변동성 (%)</th>';
        html += '</tr></thead><tbody class="divide-y divide-card">';
        
        const volatilities = Object.entries(data.individual_volatilities)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);
        
        volatilities.forEach(([ticker, vol]) => {
            const volClass = vol < 20 ? 'text-green' : vol < 35 ? 'text-yellow' : 'text-red';
            const translatedTicker = typeof translateStockName === 'function' 
                ? translateStockName(ticker, ticker) 
                : ticker;
            
            html += `
                <tr class="hover:bg-tertiary">
                    <td class="font-mono font-bold text-accent-blue">${ticker}</td>
                    <td class="text-right ${volClass}">${vol.toFixed(2)}%</td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div></div>';
    }
    
    container.innerHTML = html;
    console.log('✅ Rendered risk analysis');
};

// ============================================
// Sector Heatmap Rendering
// ============================================

/**
 * Render Sector Heatmap
 * @param {Object} data - Sector heatmap data from API
 */
window.renderUSSectorHeatmap = function(data) {
    const container = document.getElementById('sector-heatmap-content');
    if (!container) {
        console.warn('Sector heatmap container not found');
        return;
    }
    
    if (!data || !data.sectors || data.sectors.length === 0) {
        container.innerHTML = '<div class="text-center py-12"><i class="fas fa-chart-pie text-6xl text-gray-600 mb-4"></i><p class="text-gray-400 text-sm mb-2">섹터 데이터가 없습니다</p></div>';
        return;
    }
    
    let html = '<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">';
    
    data.sectors.forEach(sector => {
        const ticker = sector.ticker || 'N/A';
        const name = sector.name || 'N/A';
        const change = sector.change_pct || sector.change || 0;
        const changeClass = getColorClass(change);
        const changeIcon = change >= 0 ? '▲' : '▼';
        
        html += `
            <div class="bg-tertiary rounded p-4 hover:border-accent-blue border border-card transition-colors">
                <div class="text-xs text-gray-400 mb-1">${ticker}</div>
                <div class="text-sm font-bold text-white mb-1">${name}</div>
                <div class="text-sm ${changeClass} flex items-center gap-1">
                    <span>${changeIcon}</span>
                    <span>${formatPercent(change)}</span>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
    console.log('✅ Rendered sector heatmap');
};

// ============================================
// Economic Calendar Rendering
// ============================================

/**
 * Render Economic Calendar
 * @param {Object} data - Calendar data from API
 */
window.renderUSCalendar = function(data) {
    const container = document.getElementById('calendar-content');
    if (!container) {
        console.warn('Calendar container not found');
        return;
    }
    
    if (!data || !data.events || (Array.isArray(data.events) && data.events.length === 0)) {
        container.innerHTML = '<div class="text-sm text-gray-500">No calendar events available</div>';
        return;
    }
    
    const events = Array.isArray(data.events) ? data.events : [];
    
    if (events.length === 0) {
        container.innerHTML = '<div class="text-sm text-gray-500">No upcoming events</div>';
        return;
    }
    
    // Group events by date
    const eventsByDate = {};
    events.forEach(event => {
        const date = event.date || event.event_date || 'Unknown';
        if (!eventsByDate[date]) {
            eventsByDate[date] = [];
        }
        eventsByDate[date].push(event);
    });
    
    // Sort dates
    const sortedDates = Object.keys(eventsByDate).sort();
    
    let html = '<div class="space-y-4">';
    
    sortedDates.forEach(date => {
        html += `
            <div class="border-b border-card pb-3">
                <div class="text-xs font-bold text-gray-400 mb-2">${date}</div>
                <div class="space-y-2">
        `;
        
        eventsByDate[date].forEach(event => {
            const impact = event.impact || 'Low';
            const impactClass = impact === 'High' ? 'text-red' : impact === 'Medium' ? 'text-yellow' : 'text-gray-400';
            const eventName = event.event || event.name || 'Unknown Event';
            const description = event.description || '';
            
            html += `
                <div class="p-2 bg-tertiary rounded">
                    <div class="flex items-center justify-between mb-1">
                        <span class="text-sm text-white font-medium">${eventName}</span>
                        <span class="text-xs ${impactClass} px-2 py-0.5 rounded bg-secondary">${impact}</span>
                    </div>
                    ${description ? `<div class="text-xs text-gray-400">${description}</div>` : ''}
                </div>
            `;
        });
        
        html += '</div></div>';
    });
    
    html += '</div>';
    
    container.innerHTML = html;
    
    console.log(`✅ Rendered ${events.length} calendar events`);
};

