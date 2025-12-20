/**
 * US Market Smart Money Alpha Platform
 * Frontend Application Logic
 */

// ============================================
// Global Variables & State Management
// ============================================

// Language state (ko/en) - persisted in localStorage
window.currentLang = localStorage.getItem("appLang") || "ko";

// AI Model state (gemini/gpt) - persisted in localStorage
window.currentModel = localStorage.getItem("appModel") || "gemini";

// Lightweight Charts instance for stock chart
window.usStockChart = null;

// Current selected stock pick for chart display
window.currentChartPick = null;

// Technical indicators state
window.indicatorState = {
  rsi: false,
  macd: false,
  bb: false, // Bollinger Bands
  sr: false, // Support/Resistance
};

// Chart period state
window.currentChartPeriod = "6M";

// Update intervals
window.realtimePriceInterval = null;
window.macroAnalysisInterval = null;

// API base URL
window.API_BASE = "";

// Sector translations
window.sectorTranslations = {
  ko: {
    'Tech': '기술',
    'Health': '헬스케어',
    'Finance': '금융',
    'Consumer': '소비재',
    'Cons': '소비재',
    'Industrial': '산업',
    'Indust': '산업',
    'Energy': '에너지',
    'Materials': '소재',
    'Mater': '소재',
    'Real Estate': '부동산',
    'Utilities': '유틸리티',
    'Telecom': '통신',
    'Unknown': '알 수 없음'
  },
  en: {
    'Tech': 'Technology',
    'Health': 'Healthcare',
    'Finance': 'Financial',
    'Consumer': 'Consumer',
    'Cons': 'Consumer',
    'Industrial': 'Industrial',
    'Indust': 'Industrial',
    'Energy': 'Energy',
    'Materials': 'Materials',
    'Mater': 'Materials',
    'Real Estate': 'Real Estate',
    'Utilities': 'Utilities',
    'Telecom': 'Telecommunications',
    'Unknown': 'Unknown'
  }
};

// i18n translations
window.i18n = {
  ko: {
    dashboard: "대시보드",
    smartMoney: "스마트 머니 추천",
    macro: "매크로 분석",
    etfFlows: "ETF 자금 흐름",
    calendar: "경제 캘린더",
    calendarTab: "캘린더",
    portfolio: "포트폴리오",
    portfolioComingSoon: "포트폴리오 기능은 곧 출시됩니다",
    portfolioDescription: "보유 종목 관리 및 성과 추적 기능을 준비 중입니다",
    optionsFlowComingSoon: "옵션 흐름 분석 기능은 곧 출시됩니다",
    optionsFlowDescription: "주요 종목의 옵션 체인 데이터 및 비정상 거래 감지 기능을 준비 중입니다",
    insiderComingSoon: "내부자 거래 추적 기능은 곧 출시됩니다",
    insiderDescription: "기업 임원 및 내부자의 매수/매도 활동 추적 기능을 준비 중입니다",
    riskComingSoon: "리스크 분석 기능은 곧 출시됩니다",
    riskDescription: "포트폴리오 변동성, 상관관계, 베타 분석 기능을 준비 중입니다",
    marketOverview: "시장 개요",
    marketIndices: "시장 지수",
    analysis: "분석",
    sectors: "섹터",
    lastUpdate: "마지막 업데이트",
    dataSource: "데이터 출처",
    aiModel: "AI 모델",
    language: "언어",
    realTime: "실시간",
    top10: "상위 10개",
    priceChart: "가격 차트",
    aiSummary: "AI 요약",
    macroAnalysis: "매크로 분석",
    economicCalendar: "경제 캘린더",
    advanced: "고급 기능",
    optionsFlow: "옵션 흐름",
    insiderActivity: "내부자 거래",
    riskAnalysis: "리스크 분석",
    rank: "순위",
    ticker: "티커",
    name: "종목명",
    score: "점수",
    price: "가격",
    change: "변동",
    sector: "섹터",
    selectAIModel: "AI 모델 선택",
    loading: "로딩 중...",
    error: "오류",
    noData: "데이터 없음",
    networkError: "네트워크 연결 오류",
    apiError: "서버 오류가 발생했습니다",
    timeoutError: "요청 시간이 초과되었습니다",
    unknownError: "알 수 없는 오류가 발생했습니다",
    retry: "다시 시도",
    close: "닫기",
  },
  en: {
    dashboard: "Dashboard",
    smartMoney: "Smart Money Picks",
    macro: "Macro Analysis",
    etfFlows: "ETF Flows",
    calendar: "Economic Calendar",
    calendarTab: "Calendar",
    portfolio: "Portfolio",
    portfolioComingSoon: "Portfolio feature coming soon",
    portfolioDescription: "Portfolio management and performance tracking features are under development",
    optionsFlowComingSoon: "Options flow analysis feature coming soon",
    optionsFlowDescription: "Options chain data and unusual activity detection features are under development",
    insiderComingSoon: "Insider activity tracking feature coming soon",
    insiderDescription: "Corporate executive and insider buy/sell activity tracking features are under development",
    riskComingSoon: "Risk analysis feature coming soon",
    riskDescription: "Portfolio volatility, correlation, and beta analysis features are under development",
    marketOverview: "Market Overview",
    marketIndices: "Market Indices",
    analysis: "Analysis",
    sectors: "Sectors",
    lastUpdate: "Last Update",
    dataSource: "Data Source",
    aiModel: "AI Model",
    language: "Language",
    realTime: "Real-time",
    top10: "Top 10",
    priceChart: "Price Chart",
    aiSummary: "AI Summary",
    macroAnalysis: "Macro Analysis",
    economicCalendar: "Economic Calendar",
    advanced: "Advanced",
    optionsFlow: "Options Flow",
    insiderActivity: "Insider Activity",
    riskAnalysis: "Risk Analysis",
    rank: "Rank",
    ticker: "Ticker",
    name: "Name",
    score: "Score",
    price: "Price",
    change: "Change",
    sector: "Sector",
    selectAIModel: "Select AI Model",
    loading: "Loading...",
    error: "Error",
    noData: "No Data",
    networkError: "Network connection error",
    apiError: "Server error occurred",
    timeoutError: "Request timeout",
    unknownError: "Unknown error occurred",
    retry: "Retry",
    close: "Close",
  },
};

// ============================================
// Utility Functions
// ============================================

/**
 * Save state to localStorage
 */
window.saveState = function () {
  localStorage.setItem("appLang", window.currentLang);
  localStorage.setItem("appModel", window.currentModel);
};

/**
 * Load state from localStorage
 */
window.loadState = function () {
  // Force Korean as default for Korean market launch
  const storedLang = localStorage.getItem("appLang");
  window.currentLang = storedLang || "ko";
  // Reset to Korean if no preference is stored (for Korean market)
  if (!storedLang) {
    window.currentLang = "ko";
    localStorage.setItem("appLang", "ko");
  }
  window.currentModel = localStorage.getItem("appModel") || "gemini";
};

/**
 * Format number with commas
 */
window.formatNumber = function (num) {
  if (num === null || num === undefined || isNaN(num)) return "N/A";
  return Number(num).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

/**
 * Format percentage
 */
window.formatPercent = function (num) {
  if (num === null || num === undefined || isNaN(num)) return "N/A";
  const sign = num >= 0 ? "+" : "";
  return `${sign}${Number(num).toFixed(2)}%`;
};

/**
 * Get color class based on value
 */
window.getColorClass = function (value) {
  if (value === null || value === undefined || isNaN(value))
    return "text-gray-400";
  return value >= 0 ? "text-green" : "text-red";
};

/**
 * Translate sector name to Korean
 */
window.translateSector = function (sector) {
  if (!sector) return "알 수 없음";
  const lang = window.currentLang || "ko";
  const translations = window.sectorTranslations[lang] || window.sectorTranslations.ko;
  return translations[sector] || sector;
};

/**
 * Translate stock name to Korean (if available)
 * For now, returns English name, but can be extended with a translation map
 */
window.translateStockName = function (name, ticker) {
  const lang = window.currentLang || "ko";
  
  // If Korean is selected, try to get Korean name from API or use English
  // For now, we'll keep English names but can add translation map later
  if (lang === "ko") {
    // Common stock name translations (can be extended)
    const stockNameMap = {
      'AAPL': '애플',
      'MSFT': '마이크로소프트',
      'GOOGL': '구글',
      'AMZN': '아마존',
      'TSLA': '테슬라',
      'META': '메타',
      'NVDA': '엔비디아',
      'JPM': 'JP모건',
      'V': '비자',
      'JNJ': '존슨앤존슨',
      'WMT': '월마트',
      'PG': '프록터앤갬블',
      'MA': '마스터카드',
      'DIS': '월트디즈니',
      'NFLX': '넷플릭스',
      'AMD': 'AMD',
      'INTC': '인텔',
      'CSCO': '시스코',
      'PEP': '펩시',
      'KO': '코카콜라',
      'NKE': '나이키',
      'BA': '보잉',
      'CAT': '캐터필러',
      'GE': '제너럴일렉트릭',
      'IBM': 'IBM',
      'XOM': '엑슨모빌',
      'CVX': '셰브론',
      'BAC': '뱅크오브아메리카',
      'GS': '골드만삭스',
      'C': '시티그룹',
      'WFC': '웰스파고',
      'AXP': '아메리칸익스프레스',
      'HD': '홈디포',
      'LOW': '로우스',
      'TGT': '타겟',
      'COST': '코스트코',
      'SBUX': '스타벅스',
      'MCD': '맥도날드',
      'NKE': '나이키',
      'ADBE': '어도비',
      'CRM': '세일즈포스',
      'ORCL': '오라클',
      'INTU': '인투이트',
      'NOW': '서비스나우',
      'SHOP': '샵ify',
      'SQ': '스퀘어',
      'PYPL': '페이팔',
      'ZM': '줌',
      'DOCU': '도큐사인',
      'SPOT': '스포티파이',
      'UBER': '우버',
      'LYFT': '리프트',
      'ABNB': '에어비앤비',
      'DASH': '도어대시',
      'GRUB': '그럽허브',
      'ETSY': '이츠이',
      'PINS': '핀터레스트',
      'SNAP': '스냅',
      'TWTR': '트위터',
      'ROKU': '로쿠',
      'FUBO': '푸보TV',
      'PLTR': '팔란티어',
      'SNOW': '스노우플레이크',
      'DDOG': '데이터독',
      'NET': '클라우드플레어',
      'CRWD': '크라우드스트라이크',
      'ZS': '줄로스케일',
      'OKTA': '옥타',
      'FTNT': '포트넷',
      'PANW': '팔로알토',
      'CHKP': '체크포인트',
      'QLYS': '퀄리스',
      'TENB': '테나블',
      'VRNS': '바란스',
      'RPD': '래피드7',
      'ESTC': '엘라스틱',
      'MIME': '마임캐스트',
      'VEEV': '비브',
      'TEAM': '아틀라시안',
      'ZM': '줌',
      'DOCN': '디지털오션',
      'NET': '클라우드플레어',
      'AKAM': '아카마이',
      'FFIV': 'F5',
      'JNPR': '주니퍼',
      'ANET': '아리스타',
      'ARRS': '아루바',
      'CIEN': '시에나',
      'COMM': '코뮤스코프',
      'EXTR': '익스트림',
      'INFN': '인피논',
      'LITE': '라이트',
      'MRVL': '마벨',
      'NTNX': '누타닉스',
      'QLYS': '퀄리스',
      'RDWR': '라드웨어',
      'RVBD': '리버베드',
      'SCWX': '시큐어웍스',
      'SPLK': '스플렁크',
      'TUFN': '투판',
      'VEEV': '비브',
      'VRNS': '바란스',
      'WDAY': '워크데이',
      'ZEN': '젠데스크',
      'ZUO': '주오라',
      'ELV': '엘레반스 헬스',
      'MU': '마이크론 테크놀로지',
      'DECK': '데커스 아웃도어',
      'BALL': '볼 코퍼레이션',
      'JBL': '자빌',
      'NEM': '뉴몬트',
      'CTSH': '코그니잔트',
      'ADBE': '어도비',
      'TXT': '텍스트론',
      'STLD': '스틸 다이나믹스'
    };
    
    // Check if we have a Korean translation
    if (stockNameMap[ticker]) {
      return stockNameMap[ticker];
    }
    
    // If no translation, return English name
    return name;
  }
  
  return name;
};

/**
 * Translate UI elements
 */
window.translateUI = function () {
  const elements = document.querySelectorAll("[data-i18n]");
  elements.forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (
      window.i18n[window.currentLang] &&
      window.i18n[window.currentLang][key]
    ) {
      el.textContent = window.i18n[window.currentLang][key];
    }
  });
  
  // Also update placeholder text
  const searchInput = document.getElementById("search-input");
  if (searchInput) {
    searchInput.placeholder = window.currentLang === "ko" 
      ? "티커 또는 회사명 검색..." 
      : "Search ticker or company name...";
  }
};

/**
 * Log error with context
 */
window.logError = function (context, error) {
  console.error(`[${context}]`, error);
  // Could send to error tracking service here
};

/**
 * Show error message to user
 * @param {string} message - Error message
 * @param {string} type - Error type ('error', 'warning', 'info')
 * @param {number} duration - Display duration in ms (0 = permanent until closed)
 */
window.showErrorMessage = function (message, type = "error", duration = 5000) {
  // Remove existing error toast if any
  const existingToast = document.getElementById("error-toast");
  if (existingToast) {
    existingToast.remove();
  }

  // Create toast element
  const toast = document.createElement("div");
  toast.id = "error-toast";
  toast.className = `fixed top-4 right-4 z-50 max-w-md p-4 rounded-lg shadow-lg border ${
    type === "error"
      ? "bg-red-900 border-red-700 text-red-100"
      : type === "warning"
      ? "bg-yellow-900 border-yellow-700 text-yellow-100"
      : "bg-blue-900 border-blue-700 text-blue-100"
  }`;

  toast.innerHTML = `
    <div class="flex items-start gap-3">
      <div class="flex-shrink-0">
        <i class="fas ${
          type === "error"
            ? "fa-exclamation-circle"
            : type === "warning"
            ? "fa-exclamation-triangle"
            : "fa-info-circle"
        } text-xl"></i>
      </div>
      <div class="flex-1">
        <p class="text-sm font-medium">${message}</p>
      </div>
      <button onclick="this.parentElement.parentElement.remove()" class="flex-shrink-0 text-gray-400 hover:text-white">
        <i class="fas fa-times"></i>
      </button>
    </div>
  `;

  document.body.appendChild(toast);

  // Auto-remove after duration
  if (duration > 0) {
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, duration);
  }
};

/**
 * Get user-friendly error message
 * @param {Error} error - Error object
 * @param {string} context - Error context
 * @returns {string} User-friendly error message
 */
window.getErrorMessage = function (error, context = "") {
  const lang = window.currentLang || "ko";
  const i18n = window.i18n[lang] || window.i18n.ko;

  // Network errors
  if (
    error.message.includes("Failed to fetch") ||
    error.message.includes("NetworkError") ||
    error.message.includes("network")
  ) {
    return i18n.networkError || "네트워크 연결 오류";
  }

  // Timeout errors
  if (
    error.message.includes("timeout") ||
    error.message.includes("Timeout")
  ) {
    return i18n.timeoutError || "요청 시간이 초과되었습니다";
  }

  // HTTP errors
  if (error.message.includes("HTTP error")) {
    const statusMatch = error.message.match(/status: (\d+)/);
    if (statusMatch) {
      const status = parseInt(statusMatch[1]);
      if (status === 404) {
        return lang === "ko" ? "요청한 데이터를 찾을 수 없습니다" : "Requested data not found";
      } else if (status === 500) {
        return i18n.apiError || "서버 오류가 발생했습니다";
      } else if (status >= 400 && status < 500) {
        return lang === "ko" ? "잘못된 요청입니다" : "Bad request";
      } else if (status >= 500) {
        return i18n.apiError || "서버 오류가 발생했습니다";
      }
    }
    return i18n.apiError || "서버 오류가 발생했습니다";
  }

  // API response errors
  if (error.error) {
    return error.error;
  }

  // Unknown errors
  return i18n.unknownError || "알 수 없는 오류가 발생했습니다";
};

/**
 * Fetch API with error handling
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Fetch options
 * @param {boolean} showErrorToast - Whether to show error toast to user
 * @returns {Promise<Object>} API response
 */
window.fetchAPI = async function (endpoint, options = {}, showErrorToast = false) {
  try {
    // Add timeout to fetch request (30 seconds)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    const response = await fetch(`${window.API_BASE}${endpoint}`, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      // Try to parse error message from response
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData.error) {
          errorMessage = errorData.error;
        }
      } catch (e) {
        // Response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }

      const error = new Error(errorMessage);
      error.status = response.status;
      error.response = response;

      window.logError(`API: ${endpoint}`, error);

      if (showErrorToast) {
        const userMessage = getErrorMessage(error, endpoint);
        showErrorMessage(userMessage, "error");
      }

      throw error;
    }

    return await response.json();
  } catch (error) {
    // Handle abort (timeout)
    if (error.name === "AbortError") {
      const timeoutError = new Error("Request timeout");
      window.logError(`API: ${endpoint}`, timeoutError);
      if (showErrorToast) {
        const userMessage = getErrorMessage(timeoutError, endpoint);
        showErrorMessage(userMessage, "error");
      }
      throw timeoutError;
    }

    // Handle network errors
    if (
      error.message.includes("Failed to fetch") ||
      error.message.includes("NetworkError")
    ) {
      window.logError(`API: ${endpoint}`, error);
      if (showErrorToast) {
        const userMessage = getErrorMessage(error, endpoint);
        showErrorMessage(userMessage, "error");
      }
      throw error;
    }

    // Re-throw if already handled
    if (error.status) {
      throw error;
    }

    // Log and re-throw other errors
    window.logError(`API: ${endpoint}`, error);
    if (showErrorToast) {
      const userMessage = getErrorMessage(error, endpoint);
      showErrorMessage(userMessage, "error");
    }
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
window.initApp = function () {
  console.log("🚀 Initializing US Market Smart Money Alpha Platform...");

  // Load saved state from localStorage
  loadState();
  console.log(
    `📝 Loaded state - Language: ${window.currentLang}, Model: ${window.currentModel}`
  );

  // Update UI with loaded state
  updateUIState();

  // Translate UI immediately after state is loaded
  translateUI();

  // Register event listeners
  registerEventListeners();

  // Initialize dashboard data
  if (typeof updateUSMarketDashboard === "function") {
    updateUSMarketDashboard().catch((error) => {
      logError("Dashboard initialization", error);
      const userMessage = getErrorMessage(error, "Dashboard initialization");
      showErrorMessage(userMessage, "error");
    });
  }

  // Initialize macro analysis (separate from main dashboard)
  if (typeof reloadMacroAnalysis === "function") {
    reloadMacroAnalysis().catch((error) => {
      logError("Macro analysis initialization", error);
      // Don't show toast for macro analysis errors on init (it's not critical)
    });
  }

  // Load options flow and risk analysis data
  loadOptionsFlow();
  loadRiskAnalysis();

  // Set up real-time update intervals
  setupUpdateIntervals();

  // Translate UI
  translateUI();

  console.log("✅ Application initialized successfully");
};

/**
 * Update UI elements with current state
 */
window.updateUIState = function () {
  // Update language display
  const langText = document.getElementById("lang-text");
  const footerLang = document.getElementById("footer-lang");
  if (langText) langText.textContent = window.currentLang.toUpperCase();
  if (footerLang) footerLang.textContent = window.currentLang.toUpperCase();

  // Update AI model display
  const aiModelBtn = document.getElementById("ai-model-btn");
  if (aiModelBtn) {
    const modelText =
      window.currentModel.charAt(0).toUpperCase() +
      window.currentModel.slice(1);
    const span = aiModelBtn.querySelector("span");
    if (span) span.textContent = modelText;
  }

  // Update footer AI model display
  // Note: Footer model display is handled by footer structure, no need for separate update
};

/**
 * Register all event listeners
 */
window.registerEventListeners = function () {
  // SNB Toggle
  const snbToggle = document.getElementById("snb-toggle");
  if (snbToggle) {
    snbToggle.addEventListener("click", function () {
      const snb = document.getElementById("snb");
      if (snb) snb.classList.toggle("show");
    });
  }

  // Close SNB when clicking outside on mobile
  if (window.innerWidth <= 1023) {
    document.addEventListener("click", function (e) {
      const snb = document.getElementById("snb");
      const toggle = document.getElementById("snb-toggle");
      if (
        snb &&
        toggle &&
        !snb.contains(e.target) &&
        !toggle.contains(e.target) &&
        snb.classList.contains("show")
      ) {
        snb.classList.remove("show");
      }
    });
  }

  // Accordion functionality
  document.querySelectorAll(".accordion-header").forEach((header) => {
    header.addEventListener("click", function () {
      const content = this.nextElementSibling;
      const icon = this.querySelector("i");
      if (content) {
        content.classList.toggle("open");
        if (icon) icon.classList.toggle("rotate-180");
      }
    });
  });

  // Modal functionality
  const aiModelBtn = document.getElementById("ai-model-btn");
  const closeModalBtn = document.getElementById("close-modal");
  const aiModelModal = document.getElementById("ai-model-modal");

  if (aiModelBtn && aiModelModal) {
    aiModelBtn.addEventListener("click", function () {
      aiModelModal.classList.add("show");
    });
  }

  if (closeModalBtn && aiModelModal) {
    closeModalBtn.addEventListener("click", function () {
      aiModelModal.classList.remove("show");
    });
  }

  // Close modal on overlay click
  if (aiModelModal) {
    aiModelModal.addEventListener("click", function (e) {
      if (e.target === this) {
        this.classList.remove("show");
      }
    });
  }

  // AI Model Selection
  if (aiModelModal) {
    aiModelModal.querySelectorAll("button").forEach((btn) => {
      btn.addEventListener("click", function () {
        const modelText =
          this.querySelector(".font-medium")?.textContent.toLowerCase();
        if (modelText) {
          window.currentModel = modelText.includes("gemini") ? "gemini" : "gpt";
          saveState();

          // Update UI
          if (aiModelBtn) {
            const span = aiModelBtn.querySelector("span");
            if (span) {
              span.textContent =
                modelText.charAt(0).toUpperCase() + modelText.slice(1);
            }
          }

          aiModelModal.classList.remove("show");

          // Reload macro analysis with new model
          if (typeof reloadMacroAnalysis === "function") {
            reloadMacroAnalysis();
          }
        }
      });
    });
  }

  // Tab switching
  document.querySelectorAll(".nav-tab").forEach((tab) => {
    tab.addEventListener("click", function () {
      document.querySelectorAll(".nav-tab").forEach((t) => {
        t.classList.remove("active", "text-white", "border-white");
        t.classList.add("text-gray-400", "border-transparent");
      });
      this.classList.add("active", "text-white", "border-white");
      this.classList.remove("text-gray-400", "border-transparent");

      // Handle tab content switching
      const tabName = this.getAttribute("data-tab");
      if (tabName && typeof switchTab === "function") {
        switchTab(tabName);
      }
    });
  });

  // Language toggle
  const langToggle = document.getElementById("lang-toggle");
  if (langToggle) {
    langToggle.addEventListener("click", function () {
      // Toggle between ko and en
      window.currentLang = window.currentLang === "ko" ? "en" : "ko";
      saveState();

      // Update UI
      const langText = document.getElementById("lang-text");
      const footerLang = document.getElementById("footer-lang");
      const summaryLang = document.getElementById("summary-lang");
      if (langText) langText.textContent = window.currentLang.toUpperCase();
      if (footerLang) footerLang.textContent = window.currentLang.toUpperCase();
      if (summaryLang) summaryLang.textContent = window.currentLang.toUpperCase();

      // Translate UI
      translateUI();

      // Reload data with new language
      if (typeof updateUSMarketDashboard === "function") {
        updateUSMarketDashboard();
      }
      if (typeof reloadMacroAnalysis === "function") {
        reloadMacroAnalysis();
      }
      
      // Reload AI summary if a stock is selected
      if (window.currentChartPick && typeof loadUSAISummary === "function") {
        loadUSAISummary(window.currentChartPick.ticker);
      }
    });
  }

  // Chart period buttons
  document.querySelectorAll(".chart-period-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      const period = this.getAttribute("data-period");
      if (period) {
        window.currentChartPeriod = period;

        // Update button states
        document.querySelectorAll(".chart-period-btn").forEach((b) => {
          b.classList.remove("text-white", "bg-tertiary");
          b.classList.add("text-gray-400");
        });
        this.classList.add("text-white", "bg-tertiary");
        this.classList.remove("text-gray-400");

        // Reload chart if a stock is selected
        if (window.currentChartPick && typeof loadUSStockChart === "function") {
          loadUSStockChart(window.currentChartPick, null, period);
        }
      }
    });
  });

  // Indicator toggle buttons
  document.querySelectorAll(".indicator-toggle").forEach((btn) => {
    btn.addEventListener("click", function () {
      const indicator = this.getAttribute("data-indicator");
      if (indicator && typeof toggleIndicator === "function") {
        toggleIndicator(indicator);
      }
    });
  });

  // AI Summary language toggle
  const summaryLangToggle = document.getElementById("summary-lang-toggle");
  if (summaryLangToggle) {
    summaryLangToggle.addEventListener("click", function () {
      window.currentLang = window.currentLang === "ko" ? "en" : "ko";
      saveState();

      // Update UI
      const summaryLang = document.getElementById("summary-lang");
      const langText = document.getElementById("lang-text");
      const footerLang = document.getElementById("footer-lang");
      if (summaryLang) summaryLang.textContent = window.currentLang.toUpperCase();
      if (langText) langText.textContent = window.currentLang.toUpperCase();
      if (footerLang) footerLang.textContent = window.currentLang.toUpperCase();

      // Translate UI
      translateUI();

      // Reload AI summary if a stock is selected
      if (window.currentChartPick && typeof loadUSAISummary === "function") {
        loadUSAISummary(window.currentChartPick.ticker);
      }

      // Reload data with new language
      if (typeof updateUSMarketDashboard === "function") {
        updateUSMarketDashboard();
      }
      if (typeof reloadMacroAnalysis === "function") {
        reloadMacroAnalysis();
      }
    });
  }

  // Navigation link clicks
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const href = this.getAttribute("href");
      if (href && href.startsWith("#")) {
        // Remove active class from all nav links
        document.querySelectorAll(".nav-link").forEach((l) => {
          l.classList.remove("active");
        });
        // Add active class to clicked link
        this.classList.add("active");
        
        // Scroll to section if needed
        const targetId = href.substring(1);
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
          // Find the scrollable container (main content area)
          const scrollContainer = document.querySelector("main .flex-1.overflow-y-auto");
          
          if (scrollContainer) {
            // Get the position of the target element relative to the scroll container
            const containerRect = scrollContainer.getBoundingClientRect();
            const targetRect = targetElement.getBoundingClientRect();
            
            // Calculate the scroll position within the container
            const scrollTop = scrollContainer.scrollTop;
            const targetTop = targetRect.top - containerRect.top + scrollTop;
            
            // Scroll the container smoothly
            scrollContainer.scrollTo({
              top: targetTop - 20, // 20px offset for better visibility
              behavior: "smooth"
            });
          } else {
            // Fallback to window scroll if container not found
            const headerOffset = 56;
            const elementPosition = targetElement.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
            
            window.scrollTo({
              top: offsetPosition,
              behavior: "smooth"
            });
          }
          
          // Also open accordion if it's an accordion section
          if (targetId === "macro" || targetId === "etf-flows" || targetId === "calendar") {
            const accordionContent = targetElement.querySelector(".accordion-content");
            if (accordionContent && !accordionContent.classList.contains("open")) {
              accordionContent.classList.add("open");
              const icon = targetElement.querySelector(".accordion-header i");
              if (icon) icon.classList.add("rotate-180");
            }
          }
        } else {
          console.warn(`Section with id "${targetId}" not found`);
        }
      }
    });
  });

  // Handle window resize
  window.addEventListener("resize", function () {
    const snb = document.getElementById("snb");
    if (snb && window.innerWidth >= 1024) {
      snb.classList.remove("show");
    }

    // Resize chart if exists
    if (
      window.usStockChart &&
      typeof window.usStockChart.resize === "function"
    ) {
      const container = document.getElementById("chart-container");
      if (container) {
        window.usStockChart.resize(
          container.clientWidth,
          container.clientHeight
        );
      }
    }
  });

  console.log("📌 Event listeners registered");
};

/**
 * Set up real-time update intervals
 */
window.setupUpdateIntervals = function () {
  // Clear existing intervals
  if (window.realtimePriceInterval) {
    clearInterval(window.realtimePriceInterval);
  }
  if (window.macroAnalysisInterval) {
    clearInterval(window.macroAnalysisInterval);
  }

  // Real-time price updates (20 seconds)
  if (typeof updateRealtimePrices === "function") {
    window.realtimePriceInterval = setInterval(() => {
      updateRealtimePrices().catch((error) => {
        logError("Real-time price update", error);
      });
    }, 20000); // 20 seconds
    console.log("⏱️ Real-time price updates: 20s interval");
  }

  // Macro analysis refresh (10 minutes)
  if (typeof reloadMacroAnalysis === "function") {
    window.macroAnalysisInterval = setInterval(() => {
      reloadMacroAnalysis().catch((error) => {
        logError("Macro analysis refresh", error);
      });
    }, 600000); // 10 minutes
    console.log("⏱️ Macro analysis refresh: 10min interval");
  }

  // Update time display (1 second)
  const updateTime = function () {
    const timeEl = document.getElementById("last-update-time");
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
window.cleanupApp = function () {
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
  if (window.usStockChart && typeof window.usStockChart.remove === "function") {
    window.usStockChart.remove();
    window.usStockChart = null;
  }

  console.log("🧹 Application cleaned up");
};

// ============================================
// Tab Switching Functions
// ============================================

/**
 * Switch between tabs (Market, Analysis, Sectors, Calendar)
 * @param {string} tabName - Name of the tab to switch to
 */
window.switchTab = function (tabName) {
  console.log(`🔄 Switching to tab: ${tabName}`);
  
  // Hide all tab content sections
  const allSections = document.querySelectorAll('[data-tab-content]');
  allSections.forEach(section => {
    section.style.display = 'none';
  });
  
  // Show the selected tab's content
  const targetSection = document.querySelector(`[data-tab-content="${tabName}"]`);
  if (targetSection) {
    targetSection.style.display = 'block';
    
    // Scroll to top of content area
    const scrollContainer = document.querySelector("main .flex-1.overflow-y-auto");
    if (scrollContainer) {
      scrollContainer.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    // Load data for specific tabs if needed
    if (tabName === 'sectors') {
      if (typeof loadSectorHeatmap === "function") {
        loadSectorHeatmap();
      }
    } else if (tabName === 'calendar') {
      // Load calendar data if not already loaded
      const calendarContent = document.getElementById('calendar-tab-content');
      if (calendarContent && (!calendarContent.innerHTML || calendarContent.innerHTML.trim() === '')) {
        // Calendar data should be loaded on init, but reload if empty
        if (typeof updateUSMarketDashboard === "function") {
          // Calendar is part of main dashboard, but we can reload it
        }
      }
    } else if (tabName === 'analysis') {
      // Analysis tab: show technical analysis, AI insights, etc.
      // Content is already in HTML
    }
  } else {
    console.warn(`Tab content section not found for: ${tabName}`);
  }
};

/**
 * Load Sector Heatmap
 */
window.loadSectorHeatmap = async function () {
  try {
    const data = await fetchAPI("/api/us/sector-heatmap");
    if (data && typeof renderUSSectorHeatmap === "function") {
      renderUSSectorHeatmap(data);
    }
  } catch (error) {
    logError("Sector heatmap", error);
  }
};

// ============================================
// Options Flow & Risk Analysis Functions
// ============================================

/**
 * Load Options Flow Data
 */
window.loadOptionsFlow = async function () {
  try {
    const data = await fetchAPI("/api/us/options-flow");
    if (data && typeof renderUSOptionsFlow === "function") {
      renderUSOptionsFlow(data);
    }
  } catch (error) {
    logError("Options flow", error);
    // Don't show toast, just log
  }
};

/**
 * Load Risk Analysis Data
 */
window.loadRiskAnalysis = async function () {
  try {
    const data = await fetchAPI("/api/us/portfolio-risk");
    if (data && typeof renderUSRiskAnalysis === "function") {
      renderUSRiskAnalysis(data);
    }
  } catch (error) {
    logError("Risk analysis", error);
    // Don't show toast, just log
  }
};

// ============================================
// Data Fetching Functions
// ============================================

/**
 * Update US Market Dashboard
 * Fetches and renders all major dashboard sections in parallel
 */
window.updateUSMarketDashboard = async function () {
  console.log("📊 Updating US Market Dashboard...");

  try {
    // Parallel data fetching using Promise.all
    // Note: Individual errors are caught and logged, but don't show toast for each
    // Only show toast if all requests fail
    const [portfolioData, smartMoneyData, etfFlowsData, historyDatesData] =
      await Promise.all([
        fetchAPI("/api/us/portfolio").catch((err) => {
          logError("Portfolio data", err);
          return null;
        }),
        fetchAPI("/api/us/smart-money").catch((err) => {
          logError("Smart Money data", err);
          return null;
        }),
        fetchAPI("/api/us/etf-flows").catch((err) => {
          logError("ETF Flows data", err);
          return null;
        }),
        fetchAPI("/api/us/history-dates").catch((err) => {
          logError("History dates", err);
          return null;
        }),
      ]);

    // Show error if all requests failed
    if (
      !portfolioData &&
      !smartMoneyData &&
      !etfFlowsData &&
      !historyDatesData
    ) {
      const lang = window.currentLang || "ko";
      const i18n = window.i18n[lang] || window.i18n.ko;
      showErrorMessage(
        i18n.apiError || "데이터를 불러올 수 없습니다",
        "error"
      );
    }

    // Render each section
    if (portfolioData && typeof renderUSMarketIndices === "function") {
      renderUSMarketIndices(portfolioData);
    }

    if (smartMoneyData && typeof renderUSSmartMoneyPicks === "function") {
      renderUSSmartMoneyPicks(smartMoneyData);
    }

    if (etfFlowsData && typeof renderUSETFFlows === "function") {
      renderUSETFFlows(etfFlowsData);
    }

    // Store history dates for later use
    if (historyDatesData && historyDatesData.dates) {
      window.availableHistoryDates = historyDatesData.dates;
    }

    console.log("✅ Dashboard updated successfully");

    return {
      portfolio: portfolioData,
      smartMoney: smartMoneyData,
      etfFlows: etfFlowsData,
      historyDates: historyDatesData,
    };
  } catch (error) {
    logError("Dashboard update", error);
    const userMessage = getErrorMessage(error, "Dashboard update");
    showErrorMessage(userMessage, "error");
    throw error;
  }
};

/**
 * Reload Macro Analysis
 * Refreshes macro analysis section separately (may take longer due to AI)
 */
window.reloadMacroAnalysis = async function () {
  console.log("🌍 Reloading Macro Analysis...");

  try {
    const params = new URLSearchParams({
      lang: window.currentLang,
      model: window.currentModel,
    });

    const data = await fetchAPI(`/api/us/macro-analysis?${params.toString()}`);

    if (data && typeof renderUSMacroAnalysis === "function") {
      renderUSMacroAnalysis(data);
    }

    console.log("✅ Macro analysis reloaded");

    return data;
  } catch (error) {
    logError("Macro analysis reload", error);
    throw error;
  }
};

/**
 * Update Real-time Prices
 * Updates prices for visible stocks in the table and chart
 */
window.updateRealtimePrices = async function () {
  try {
    // Collect visible tickers from the Smart Money Picks table
    const tableBody = document.getElementById("picks-table-body");
    if (!tableBody) {
      console.debug("No picks table found, skipping real-time update");
      return;
    }

    const rows = tableBody.querySelectorAll("tr[data-ticker]");
    if (rows.length === 0) {
      console.debug("No ticker rows found, skipping real-time update");
      return;
    }

    // Extract tickers from table rows
    const tickers = Array.from(rows).map((row) =>
      row.getAttribute("data-ticker")
    );

    if (tickers.length === 0) {
      return;
    }

    // Fetch real-time prices
    const response = await fetchAPI("/api/realtime-prices", {
      method: "POST",
      body: JSON.stringify({ tickers: tickers }),
    });

    if (!response.success || !response.prices) {
      console.warn("Real-time price update failed:", response);
      return;
    }

    // Update table cells
    response.prices.forEach((priceData) => {
      const row = tableBody.querySelector(
        `tr[data-ticker="${priceData.ticker}"]`
      );
      if (!row) return;

      // Update price cell
      const priceCell = row.querySelector(".price-cell");
      if (priceCell) {
        const oldPrice =
          parseFloat(priceCell.textContent.replace(/,/g, "")) || 0;
        const newPrice = priceData.price;

        priceCell.textContent = formatNumber(newPrice);

        // Flash effect for price change
        if (oldPrice > 0 && newPrice !== oldPrice) {
          priceCell.classList.add("flash");
          setTimeout(() => priceCell.classList.remove("flash"), 500);

          // Add color class
          priceCell.classList.remove("text-green", "text-red", "text-gray-400");
          if (newPrice > oldPrice) {
            priceCell.classList.add("text-green");
          } else if (newPrice < oldPrice) {
            priceCell.classList.add("text-red");
          }
        }
      }

      // Update change cell
      const changeCell = row.querySelector(".change-cell");
      if (changeCell) {
        changeCell.textContent = formatPercent(priceData.change_percent);
        changeCell.classList.remove("text-green", "text-red", "text-gray-400");
        changeCell.classList.add(getColorClass(priceData.change_percent));
      }
    });

    // Update chart if current ticker matches
    if (window.currentChartPick && window.usStockChart) {
      const currentTicker = window.currentChartPick.ticker;
      const priceData = response.prices.find((p) => p.ticker === currentTicker);

      if (priceData && typeof updateChartLastCandle === "function") {
        updateChartLastCandle(priceData);
      }
    }

    console.debug(`✅ Updated ${response.prices.length} prices`);
  } catch (error) {
    logError("Real-time price update", error);
    // Don't throw - this is a background update, failures shouldn't break the app
  }
};

/**
 * Chart-related functions
 */

// Store indicator series references
window.indicatorSeries = {
  rsi: null,
  macd: null,
  macdSignal: null,
  macdHistogram: null,
  bbUpper: null,
  bbMiddle: null,
  bbLower: null,
  supportResistance: [],
};

// Store indicator data cache
window.indicatorDataCache = {};

/**
 * Load US stock chart
 * @param {Object} pick - Stock pick object with ticker, name, score, etc.
 * @param {number} idx - Index of the pick (optional)
 * @param {string} period - Chart period (1M, 3M, 6M, 1Y, 2Y, 5Y)
 */
window.loadUSStockChart = async function (pick, idx, period) {
  if (!pick || !pick.ticker) {
    console.error("Invalid pick data:", pick);
    return;
  }

  const ticker = pick.ticker;
  const usePeriod = period || window.currentChartPeriod || "6M";
  const chartContainer = document.getElementById("chart-container");

  if (!chartContainer) {
    console.error("Chart container not found");
    return;
  }

  try {
    // Update UI: highlight selected row
    const tableBody = document.getElementById("picks-table-body");
    if (tableBody) {
      tableBody.querySelectorAll("tr").forEach((row) => {
        row.classList.remove("bg-tertiary", "border-accent-blue");
      });
      const selectedRow = tableBody.querySelector(
        `tr[data-ticker="${ticker}"]`
      );
      if (selectedRow) {
        selectedRow.classList.add("bg-tertiary", "border-accent-blue");
      }
    }

    // Update chart header (using existing chart-ticker element)
    const chartTicker = document.getElementById("chart-ticker");
    if (chartTicker) {
      chartTicker.textContent = `${ticker} - ${pick.name || ticker}${pick.score ? ` (Score: ${pick.score})` : ""}`;
    }

    // Show loading state
    chartContainer.innerHTML =
      '<div class="flex items-center justify-center h-full text-gray-500"><i class="fas fa-spinner fa-spin text-2xl"></i></div>';

    // Fetch chart data
    const params = new URLSearchParams({ period: usePeriod });
    const response = await fetchAPI(
      `/api/us/stock-chart/${ticker}?${params.toString()}`
    );

    if (response.error) {
      chartContainer.innerHTML = `<div class="flex items-center justify-center h-full text-gray-500">${response.error}</div>`;
      return;
    }

    // Clear container
    chartContainer.innerHTML = "";

    // Destroy existing chart if present
    if (window.usStockChart && typeof window.usStockChart.remove === "function") {
      window.usStockChart.remove();
      window.usStockChart = null;
    }

    // Clear indicator series references
    Object.keys(window.indicatorSeries).forEach((key) => {
      if (Array.isArray(window.indicatorSeries[key])) {
        window.indicatorSeries[key] = [];
      } else {
        window.indicatorSeries[key] = null;
      }
    });

    // Create new chart instance
    window.usStockChart = LightweightCharts.createChart(chartContainer, {
      width: chartContainer.clientWidth,
      height: chartContainer.clientHeight || 384,
      layout: {
        background: { color: "#1a1a1a" },
        textColor: "#999",
      },
      grid: {
        vertLines: { color: "#2a2a2a" },
        horzLines: { color: "#2a2a2a" },
      },
      timeScale: {
        borderColor: "#2a2a2a",
        timeVisible: true,
        rightOffset: 5,
        fixLeftEdge: false,
        fixRightEdge: false,
      },
      rightPriceScale: {
        borderColor: "#2a2a2a",
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
    });

    // Add candlestick series
    const candleSeries = window.usStockChart.addCandlestickSeries({
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderUpColor: "#22c55e",
      borderDownColor: "#ef4444",
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444",
    });

    // Set candle data
    if (response.candles && response.candles.length > 0) {
      // Ensure timestamps are in correct format (seconds since epoch)
      const formattedCandles = response.candles.map(candle => ({
        time: candle.time,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
        volume: candle.volume
      }));
      
      candleSeries.setData(formattedCandles);
      window.usStockChart.timeScale().fitContent();
      
      console.log(`✅ Set ${formattedCandles.length} candles to chart`);
    } else {
      console.warn('No candle data received');
    }

    // Store current chart pick
    window.currentChartPick = pick;

    // Re-apply active indicators
    const activeIndicators = Object.keys(window.indicatorState).filter(
      (key) => window.indicatorState[key]
    );
    if (activeIndicators.length > 0) {
      // Fetch indicator data and render
      for (const indicator of activeIndicators) {
        await toggleIndicator(indicator, true); // true = skip toggle, just render
      }
    }

    // Load AI summary
    if (typeof loadUSAISummary === "function") {
      loadUSAISummary(ticker);
    }

    console.log(`✅ Chart loaded for ${ticker} (${usePeriod})`);
  } catch (error) {
    logError("Chart loading", error);
    const userMessage = getErrorMessage(error, "Chart loading");
    if (chartContainer) {
      chartContainer.innerHTML = `<div class="flex items-center justify-center h-full text-red-500">${userMessage}</div>`;
    }
    showErrorMessage(userMessage, "error");
  }
};

/**
 * Load AI summary for a ticker
 * @param {string} ticker - Stock ticker
 */
window.loadUSAISummary = async function (ticker) {
  const summaryContainer = document.getElementById("ai-summary-content");
  if (!summaryContainer) return;

  try {
    summaryContainer.innerHTML =
      '<div class="flex items-center justify-center py-4"><i class="fas fa-spinner fa-spin text-gray-500"></i></div>';

    const params = new URLSearchParams({ lang: window.currentLang });
    const response = await fetchAPI(`/api/us/ai-summary/${ticker}?${params.toString()}`);

    if (response.error) {
      summaryContainer.innerHTML = `<div class="text-sm text-gray-500">${response.error}</div>`;
      return;
    }

    // Format summary text with line breaks
    const summaryText = response.summary
      ? response.summary.replace(/\n/g, "<br>")
      : "No summary available";

    summaryContainer.innerHTML = `<div class="text-sm text-gray-300 leading-relaxed">${summaryText}</div>`;

    // Update summary language toggle
    const summaryLangToggle = document.getElementById("summary-lang-toggle");
    const summaryLang = document.getElementById("summary-lang");
    if (summaryLangToggle && summaryLang) {
      summaryLangToggle.onclick = async function () {
        window.currentLang = window.currentLang === "ko" ? "en" : "ko";
        await loadUSAISummary(ticker);
      };
      summaryLang.textContent = window.currentLang.toUpperCase();
    }
  } catch (error) {
    logError("AI Summary loading", error);
    const userMessage = getErrorMessage(error, "AI Summary loading");
    const lang = window.currentLang || "ko";
    const i18n = window.i18n[lang] || window.i18n.ko;
    summaryContainer.innerHTML = `<div class="text-sm text-red-500">${userMessage}</div>`;
    // Don't show toast for AI summary errors (not critical)
  }
};

/**
 * Toggle technical indicator
 * @param {string} type - Indicator type (rsi, macd, bb, sr)
 * @param {boolean} skipToggle - If true, skip toggle logic and just render
 */
window.toggleIndicator = async function (type, skipToggle = false) {
  if (!window.usStockChart || !window.currentChartPick) {
    console.warn("No chart loaded");
    return;
  }

  const ticker = window.currentChartPick.ticker;

  // Toggle state (unless skipToggle is true)
  if (!skipToggle) {
    window.indicatorState[type] = !window.indicatorState[type];
  }

  // Update button styling
  const button = document.querySelector(
    `.indicator-toggle[data-indicator="${type}"]`
  );
  if (button) {
    if (window.indicatorState[type]) {
      button.classList.add("bg-accent-blue", "text-white");
      button.classList.remove("bg-tertiary");
    } else {
      button.classList.remove("bg-accent-blue", "text-white");
      button.classList.add("bg-tertiary");
    }
  }

  // If indicator is now inactive, remove it
  if (!window.indicatorState[type]) {
    renderIndicator(type, null);
    return;
  }

  // Fetch indicator data if not cached
  if (!window.indicatorDataCache[ticker]) {
    try {
      const response = await fetchAPI(
        `/api/us/technical-indicators/${ticker}`
      );
      if (response.error) {
        console.error("Error fetching indicators:", response.error);
        return;
      }
      window.indicatorDataCache[ticker] = response;
    } catch (error) {
      logError("Indicator data fetch", error);
      return;
    }
  }

  const indicatorData = window.indicatorDataCache[ticker];
  renderIndicator(type, indicatorData);
};

/**
 * Render technical indicator on chart
 * @param {string} type - Indicator type (rsi, macd, bb, sr)
 * @param {Object} data - Indicator data from API
 */
window.renderIndicator = function (type, data) {
  if (!window.usStockChart) return;

  switch (type) {
    case "rsi":
      renderRSI(data);
      break;
    case "macd":
      renderMACD(data);
      break;
    case "bb":
      renderBollingerBands(data);
      break;
    case "sr":
      renderSupportResistance(data);
      break;
    default:
      console.warn(`Unknown indicator type: ${type}`);
  }
};

/**
 * Render RSI indicator
 * @param {Object} data - Indicator data
 */
function renderRSI(data) {
  if (!data || !data.rsi) return;

  // RSI is typically displayed as a separate pane or overlay
  // For simplicity, we'll show it as a line series on the main chart
  // In a production app, you might want a separate pane

  // Remove existing RSI series
  if (window.indicatorSeries.rsi) {
    window.usStockChart.removeSeries(window.indicatorSeries.rsi);
    window.indicatorSeries.rsi = null;
  }

  // Note: RSI requires historical calculation, which we don't have in the current API response
  // This is a placeholder - you would need to calculate RSI for each candle
  console.log(`RSI: ${data.rsi}`);
  // TODO: Implement RSI line series if historical RSI data is available
}

/**
 * Render MACD indicator
 * @param {Object} data - Indicator data
 */
function renderMACD(data) {
  if (!data || !data.macd) return;

  // MACD requires historical data for each candle
  // Current API only returns current values
  // This is a placeholder
  console.log(`MACD: ${JSON.stringify(data.macd)}`);
  // TODO: Implement MACD series if historical MACD data is available
}

/**
 * Render Bollinger Bands
 * @param {Object} data - Indicator data
 */
function renderBollingerBands(data) {
  if (!data || !data.bollinger_bands) return;

  const bb = data.bollinger_bands;

  // Remove existing BB series
  if (window.indicatorSeries.bbUpper) {
    window.usStockChart.removeSeries(window.indicatorSeries.bbUpper);
    window.usStockChart.removeSeries(window.indicatorSeries.bbMiddle);
    window.usStockChart.removeSeries(window.indicatorSeries.bbLower);
    window.indicatorSeries.bbUpper = null;
    window.indicatorSeries.bbMiddle = null;
    window.indicatorSeries.bbLower = null;
  }

  // Get current time from chart
  const timeScale = window.usStockChart.timeScale();
  const visibleRange = timeScale.getVisibleRange();
  if (!visibleRange) return;

  // Create horizontal lines for current BB levels
  // Note: This shows current levels only. For full BB bands, you'd need historical data
  const currentTime = visibleRange.to;

  // Upper band
  window.indicatorSeries.bbUpper = window.usStockChart.addLineSeries({
    color: "#3b82f6",
    lineWidth: 1,
    lineStyle: 2, // Dashed
    title: "BB Upper",
  });
  window.indicatorSeries.bbUpper.setData([
    { time: visibleRange.from, value: bb.upper },
    { time: currentTime, value: bb.upper },
  ]);

  // Middle band (SMA)
  window.indicatorSeries.bbMiddle = window.usStockChart.addLineSeries({
    color: "#f59e0b",
    lineWidth: 1,
    lineStyle: 0, // Solid
    title: "BB Middle",
  });
  window.indicatorSeries.bbMiddle.setData([
    { time: visibleRange.from, value: bb.middle },
    { time: currentTime, value: bb.middle },
  ]);

  // Lower band
  window.indicatorSeries.bbLower = window.usStockChart.addLineSeries({
    color: "#3b82f6",
    lineWidth: 1,
    lineStyle: 2, // Dashed
    title: "BB Lower",
  });
  window.indicatorSeries.bbLower.setData([
    { time: visibleRange.from, value: bb.lower },
    { time: currentTime, value: bb.lower },
  ]);
}

/**
 * Render Support/Resistance levels
 * @param {Object} data - Indicator data
 */
function renderSupportResistance(data) {
  if (!data || !data.support_resistance) return;

  const sr = data.support_resistance;

  // Remove existing S/R lines
  window.indicatorSeries.supportResistance.forEach((series) => {
    if (series) {
      window.usStockChart.removeSeries(series);
    }
  });
  window.indicatorSeries.supportResistance = [];

  // Get visible time range
  const timeScale = window.usStockChart.timeScale();
  const visibleRange = timeScale.getVisibleRange();
  if (!visibleRange) return;

  const currentTime = visibleRange.to;

  // Render resistance levels (red)
  sr.resistance_levels.forEach((level, idx) => {
    const series = window.usStockChart.addLineSeries({
      color: "#ef4444",
      lineWidth: 1,
      lineStyle: 2, // Dashed
      title: `Resistance ${idx + 1}`,
    });
    series.setData([
      { time: visibleRange.from, value: level },
      { time: currentTime, value: level },
    ]);
    window.indicatorSeries.supportResistance.push(series);
  });

  // Render support levels (green)
  sr.support_levels.forEach((level, idx) => {
    const series = window.usStockChart.addLineSeries({
      color: "#22c55e",
      lineWidth: 1,
      lineStyle: 2, // Dashed
      title: `Support ${idx + 1}`,
    });
    series.setData([
      { time: visibleRange.from, value: level },
      { time: currentTime, value: level },
    ]);
    window.indicatorSeries.supportResistance.push(series);
  });
}

/**
 * Update chart's last candle with real-time price
 * @param {Object} priceData - Real-time price data
 */
window.updateChartLastCandle = function (priceData) {
  if (!window.usStockChart || !priceData) return;

  // This function would update the last candle with new price data
  // Lightweight Charts doesn't have a direct method to update a single candle
  // You would need to get all candles, update the last one, and setData again
  // For now, this is a placeholder
  console.debug(`Updating chart candle for ${priceData.ticker}: $${priceData.price}`);
  // TODO: Implement real-time candle update if needed
};

// Initialize on DOM ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", window.initApp);
} else {
  // DOM is already ready
  window.initApp();
}

// Cleanup on page unload
window.addEventListener("beforeunload", window.cleanupApp);
