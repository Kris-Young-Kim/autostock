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
            <td class="text-white">${name}</td>
            <td class="text-right ${scoreClass}">${score.toFixed(1)}</td>
            <td class="text-right price-cell text-white">${formatNumber(price)}</td>
            <td class="text-right change-cell ${changeClass}">
                <span>${changeIcon}</span>
                <span>${formatPercent(change)}</span>
            </td>
            <td class="text-center">
                <span class="px-2 py-1 rounded text-xs bg-tertiary">${sector}</span>
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

