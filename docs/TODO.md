# US Market Smart Money Alpha Platform - TODO

> 기술 문서를 기반으로 한 단계별 구현 계획서
> Part 1, 2, 3을 먼저 구축한 후, Part 4, 5, 6을 진행합니다.

---

## 📋 전체 진행 순서

```
Phase 1: 데이터 수집 및 분석 (Part 1, 2, 3)
  ↓
Phase 2: 웹 서버 및 프론트엔드 (Part 4, 5, 6)
```

---

## 🏗️ Phase 1: 데이터 수집 및 분석

### Part 1: 데이터 수집 (Data Collection)

#### 1.1 프로젝트 구조 설정

- [x] 디렉토리 구조 생성 (`DIR.md` 참조)

  - [x] `bin/` - 실행 스크립트 디렉토리
  - [x] `core/` - 핵심 비즈니스 로직
  - [x] `pipeline/` - 배치 작업 스크립트
  - [x] `data/raw/` - 원본 데이터 저장소
  - [x] `data/processed/` - 분석 완료 데이터
  - [x] `logs/` - 시스템 로그
  - [x] `us_market/` - US 시장 전용 데이터 디렉토리
  - [x] `web/templates/` - HTML 템플릿
  - [x] `web/static/css/` - CSS 파일

- [x] 환경 설정 파일 생성
  - [x] `.env.example` 파일 생성 (API 키 설정 템플릿)
    ```env
    GOOGLE_API_KEY=your_gemini_api_key
    OPENAI_API_KEY=your_openai_api_key
    FRED_API_KEY=your_fred_api_key
    DATA_DIR=./data
    PORT=3000
    ```
  - [x] `.gitignore` 설정 (`.env`, `data/`, `logs/` 제외)
  - [x] `requirements.txt` 생성 (이미 완료)
  - [x] `core/config.py` 구현 (로깅 설정 및 경로 상수)
  - [x] `core/__init__.py` 생성

#### 1.2 가격 데이터 수집 (`create_us_daily_prices.py`)

- [x] `pipeline/01_collect_prices.py` 구현
  - [x] S&P 500 종목 리스트 로드
  - [x] yfinance를 통한 일일 가격 데이터 수집
  - [x] 증분 업데이트 로직 (기존 데이터 확인 후 최신 데이터만 추가)
  - [x] `us_daily_prices.csv` 저장
  - [x] `us_stocks_list.csv` 저장
  - [x] 로깅 구현 (`logs/pipeline.log`)

**출력 파일:**

- `data/raw/us_daily_prices.csv`
- `data/raw/us_stocks_list.csv`

#### 1.3 거래량/수급 분석 (`analyze_volume.py`)

- [x] `pipeline/02_analyze_volume.py` 구현
  - [x] OBV (On-Balance Volume) 계산
  - [x] A/D Line (Accumulation/Distribution) 계산
  - [x] MFI (Money Flow Index) 계산
  - [x] Volume Surge 감지
  - [x] Supply/Demand Score 계산 (0-100)
  - [x] `us_volume_analysis.csv` 저장

**출력 파일:**

- `data/processed/us_volume_analysis.csv`

#### 1.4 기관 보유 분석 (`analyze_13f.py`)

- [x] `pipeline/03_analyze_13f.py` 구현
  - [x] yfinance를 통한 기관 보유율 수집
  - [x] 인사이더 거래 데이터 수집
  - [x] Short Interest 수집
  - [x] Institutional Score 계산 (0-100)
  - [x] `us_13f_holdings.csv` 저장

**출력 파일:**

- `data/processed/us_13f_holdings.csv`

#### 1.5 ETF 자금 흐름 분석 (`analyze_etf_flows.py`)

- [x] `pipeline/04_etf_flows.py` 구현
  - [x] 주요 ETF 24개 추적 (SPY, QQQ, IWM, GLD, USO 등)
  - [x] Flow Score 계산 (OBV, Volume Ratio 기반)
  - [x] `us_etf_flows.csv` 저장
  - [x] (선택) Gemini AI 분석 통합 → `etf_flow_analysis.json`

**출력 파일:**

- `data/processed/us_etf_flows.csv`
- `data/processed/etf_flow_analysis.json` (AI 분석 포함 시)

#### 1.6 통합 실행 스크립트

- [x] `pipeline/update_all.py` 구현
  - [x] Part 1의 모든 스크립트 순차 실행
  - [x] `--quick` 옵션 (AI 분석 제외)
  - [x] 에러 핸들링 및 로깅
  - [x] `--script` 옵션 (특정 스크립트만 실행)

**검증:**

```bash
python pipeline/update_all.py --quick  # 빠른 테스트
python pipeline/update_all.py           # 전체 실행
```

---

### Part 2: 분석 및 스크리닝 (Analysis & Screening)

#### 2.1 6-Factor 종합 스크리닝 (`smart_money_screener_v2.py`)

- [x] `pipeline/smart_money_screener_v2.py` 구현
  - [x] 데이터 로드 (Volume, 13F, ETF 데이터 병합)
  - [x] Technical Analysis 함수 구현
    - [x] RSI (14-day) 계산
    - [x] MACD (12, 26, 9) 계산
    - [x] Moving Averages (20, 50, 200) 계산
    - [x] Golden/Death Cross 감지
    - [x] Technical Score 계산 (0-100)
  - [x] Fundamental Analysis 함수 구현
    - [x] P/E, Forward P/E, P/B 수집
    - [x] Revenue Growth, Earnings Growth 수집
    - [x] ROE, Profit Margin 수집
    - [x] Fundamental Score 계산 (0-100)
  - [x] Analyst Ratings 함수 구현
    - [x] Target Price, Upside Potential 계산
    - [x] Recommendation Key 파싱
    - [x] Analyst Score 계산 (0-100)
  - [x] Relative Strength 함수 구현
    - [x] SPY 대비 20일, 60일 수익률 비교
    - [x] RS Score 계산 (0-100)
  - [x] Composite Score 계산 (가중 평균)
    - [x] Supply/Demand: 25%
    - [x] Institutional: 20%
    - [x] Technical: 20%
    - [x] Fundamental: 15%
    - [x] Analyst: 10%
    - [x] Relative Strength: 10%
  - [x] Grade 할당 (S, A, B, C, D, F)
  - [x] `smart_money_picks_v2.csv` 저장

**출력 파일:**

- `data/processed/smart_money_picks_v2.csv`

#### 2.2 섹터 히트맵 (`sector_heatmap.py`)

- [x] `pipeline/sector_heatmap.py` 구현
  - [x] 11개 S&P 섹터 ETF 추적
    - [x] XLK (Technology), XLF (Financials), XLV (Healthcare) 등
  - [x] 섹터별 퍼포먼스 계산
  - [x] Treemap 데이터 구조 생성
  - [x] `sector_heatmap.json` 저장

**출력 파일:**

- `data/processed/sector_heatmap.json`

#### 2.3 옵션 플로우 분석 (`options_flow.py`)

- [x] `pipeline/options_flow.py` 구현
  - [x] 주요 종목 옵션 체인 데이터 수집
  - [x] Put/Call Ratio 계산
  - [x] Unusual Activity 감지
  - [x] `options_flow.json` 저장

**출력 파일:**

- `data/processed/options_flow.json`

#### 2.4 인사이더 추적 (`insider_tracker.py`)

- [x] `pipeline/insider_tracker.py` 구현
  - [x] 최근 6개월 인사이더 매매 추적
  - [x] Cluster Buying 감지
  - [x] `insider_moves.json` 저장

**출력 파일:**

- `data/processed/insider_moves.json`

#### 2.5 포트폴리오 리스크 분석 (`portfolio_risk.py`)

- [x] `pipeline/portfolio_risk.py` 구현
  - [x] 상관관계 매트릭스 계산
  - [x] 포트폴리오 변동성 계산
  - [x] Beta 계산 (SPY 대비)
  - [x] Diversification Ratio 계산
  - [x] `portfolio_risk.json` 저장

**출력 파일:**

- `data/processed/portfolio_risk.json`

---

### Part 3: AI 분석 (AI Analysis)

#### 3.1 매크로 경제 분석 (`macro_analyzer.py`)

- [x] `pipeline/macro_analyzer.py` 구현
  - [x] 매크로 지표 수집
    - [x] VIX, DXY, 2Y/10Y Yield, GOLD, OIL, BTC
    - [x] SPY, QQQ
  - [x] Yield Spread 계산
  - [x] 뉴스 수집 (Google News RSS)
  - [x] Gemini 3.0 AI 분석 통합
    - [x] 한국어 분석 생성
    - [x] 영어 분석 생성
  - [x] `macro_analysis.json` 저장
  - [x] `macro_analysis_en.json` 저장

**출력 파일:**

- `data/processed/macro_analysis.json`
- `data/processed/macro_analysis_en.json`

#### 3.2 개별 종목 AI 요약 (`ai_summary_generator.py`)

- [x] `pipeline/ai_summary_generator.py` 구현
  - [x] Smart Money Picks 상위 20개 종목 선택
  - [x] 각 종목별 뉴스 수집
  - [x] Gemini AI로 투자 요약 생성
    - [x] 한국어 요약
    - [x] 영어 요약
  - [x] `ai_summaries.json` 저장

**출력 파일:**

- `data/processed/ai_summaries.json`

#### 3.3 최종 Top 10 리포트 (`final_report_generator.py`)

- [x] `pipeline/final_report_generator.py` 구현
  - [x] Quant Score와 AI 분석 결합
  - [x] Final Score 계산 (Quant 80% + AI 20%)
  - [x] Top 10 종목 선정
  - [x] `final_top10_report.json` 저장
  - [x] `smart_money_current.json` 저장 (대시보드용)

**출력 파일:**

- `data/processed/final_top10_report.json`
- `data/processed/smart_money_current.json`

#### 3.4 경제 캘린더 (`economic_calendar.py`)

- [x] `pipeline/economic_calendar.py` 구현
  - [x] 주요 경제 이벤트 수집
  - [x] AI 영향도 분석 (High Impact 이벤트)
  - [x] `weekly_calendar.json` 저장

**출력 파일:**

- `data/processed/weekly_calendar.json`

#### 3.5 통합 업데이트 스크립트 업데이트

- [x] `pipeline/update_all.py`에 Part 3 스크립트 추가
  - [x] `macro_analyzer.py` 실행
  - [x] `ai_summary_generator.py` 실행
  - [x] `final_report_generator.py` 실행
  - [x] `economic_calendar.py` 실행
  - [x] Part 2 스크립트도 추가
  - [x] `--part` 옵션 추가 (특정 파트만 실행)

**검증:**

```bash
python pipeline/update_all.py  # 전체 파이프라인 실행
```

---

## 🌐 Phase 2: 웹 서버 및 프론트엔드

### Part 4: 웹 서버 (Web Server)

#### 4.1 Flask 애플리케이션 구조 설정

- [x] `web/` 디렉토리 구조 생성
  - [x] `web/app.py` - Flask 메인 애플리케이션
  - [x] `web/routes.py` - API 엔드포인트 정의
  - [x] `web/__init__.py` - 패키지 초기화
  - [x] `web/templates/` - HTML 템플릿 (이미 생성됨)
  - [x] `web/static/` - CSS, JS, Assets (이미 생성됨)

#### 4.2 핵심 유틸리티 함수 구현

- [x] 섹터 매핑 함수 (`get_sector`)
  - [x] SECTOR_MAP 정의 (주요 종목)
  - [x] yfinance를 통한 동적 섹터 조회
  - [x] 섹터 캐시 파일 (`sector_cache.json`) 구현
- [x] 기술적 지표 계산 함수
  - [x] `calculate_rsi()` 구현
  - [x] `analyze_trend()` 구현

#### 4.3 US Market API 엔드포인트 구현

- [x] `/api/us/portfolio` - 시장 지수 데이터
  - [x] Dow Jones, S&P 500, NASDAQ, VIX 등
  - [x] 실시간 가격 및 변동률 계산
- [x] `/api/us/smart-money` - Smart Money Picks
  - [x] `smart_money_current.json` 또는 CSV 로드
  - [x] 실시간 가격 업데이트
  - [x] Performance 계산 (추천 시점 대비 수익률)
- [x] `/api/us/etf-flows` - ETF 자금 흐름
  - [x] `us_etf_flows.csv` 로드
  - [x] AI 분석 텍스트 포함
- [x] `/api/us/stock-chart/<ticker>` - 차트 데이터
  - [x] yfinance를 통한 OHLC 데이터
  - [x] Lightweight Charts 형식으로 변환
- [x] `/api/us/macro-analysis` - 매크로 분석
  - [x] `macro_analysis.json` 로드
  - [x] 언어/모델 선택 지원 (`lang`, `model` 파라미터)
  - [x] 주요 지표 실시간 업데이트
- [x] `/api/us/sector-heatmap` - 섹터 히트맵
  - [x] `sector_heatmap.json` 로드
- [x] `/api/us/options-flow` - 옵션 플로우
  - [x] `options_flow.json` 로드
- [x] `/api/us/ai-summary/<ticker>` - AI 요약
  - [x] `ai_summaries.json`에서 특정 종목 요약 반환
  - [x] 언어 선택 지원
- [x] `/api/us/technical-indicators/<ticker>` - 기술적 지표
  - [x] RSI, MACD, Bollinger Bands 계산
  - [x] Support/Resistance 레벨 탐지
- [x] `/api/us/calendar` - 경제 캘린더
  - [x] `weekly_calendar.json` 로드
- [x] `/api/us/history-dates` - 과거 분석 날짜 목록
- [x] `/api/us/history/<date>` - 특정 날짜 분석 결과

#### 4.4 실시간 가격 업데이트 API

- [x] `/api/realtime-prices` (POST)
  - [x] 배치 티커 리스트 받기
  - [x] yfinance를 통한 실시간 가격 조회
  - [x] OHLC 데이터 반환

#### 4.5 서버 실행 설정

- [x] `web/app.py` 메인 실행 블록
  - [x] Port 3000 설정 (core/config.py에서 PORT 환경변수로 설정)
  - [x] Debug 모드 설정 (FLASK_ENV 환경변수로 제어)
- [x] `bin/run_server.sh` 생성 (Linux/Mac용)
- [x] `bin/run_server.bat` 생성 (Windows용)

**검증:**

```bash
python web/app.py
# 또는
bash bin/run_server.sh
```

---

### Part 5: 프론트엔드 UI (Frontend UI)

#### 5.1 HTML 템플릿 구조

- [x] `web/templates/index.html` 생성
  - [x] 기본 HTML5 구조
  - [x] Tailwind CSS CDN 연결
  - [x] Pretendard 폰트 적용 (globals.css)
  - [x] 메타 태그 설정 (반응형)

#### 5.2 대시보드 레이아웃 구성

- [x] 헤더 섹션 (GNB)
  - [x] 로고/제목
  - [x] 언어 전환 버튼 (KO/EN)
  - [x] AI 모델 선택 (Gemini/GPT) - Gemini 기본 선택
  - [x] 검색 바
  - [x] 설정 버튼
- [x] 사이드 네비게이션 (SNB)
  - [x] 메인 메뉴 (Dashboard, Smart Money, Macro, ETF Flows, Calendar, Portfolio)
  - [x] 아코디언 메뉴 (Advanced Features)
  - [x] 토글 기능
- [x] 로컬 네비게이션 (LNB)
  - [x] 탭 메뉴 (Market Overview, Analysis, Sectors, Calendar)
- [x] Market Indices 섹션
  - [x] 그리드 레이아웃 (반응형)
  - [x] 실시간 가격 및 변동률 표시 준비
  - [x] 색상 코딩 준비 (상승/하락)
- [x] Smart Money Picks 테이블
  - [x] 상위 10개 종목 리스트 구조
  - [x] 컬럼: Rank, Ticker, Name, Score, Price, Change, Sector
  - [x] 클릭 가능한 행 준비 (차트 로드)
- [x] 차트 뷰 섹션
  - [x] Lightweight Charts 컨테이너
  - [x] 차트 헤더 (Ticker, Name, Score)
  - [x] 기간 선택 버튼 (1M, 3M, 6M, 1Y, 2Y, 5Y)
  - [x] 기술적 지표 토글 버튼 (RSI, MACD, BB, S/R)
- [x] AI Summary 섹션
  - [x] 선택 종목의 AI 요약 표시 준비
  - [x] 언어 전환 지원
- [x] Macro Analysis 섹션 (아코디언)
  - [x] 매크로 지표 그리드 준비
  - [x] AI 분석 텍스트 블록 준비
- [x] ETF Flows 섹션 (아코디언)
  - [x] 섹터별 자금 흐름 표시 준비
- [x] 경제 캘린더 섹션 (아코디언)
  - [x] 주간 이벤트 리스트 준비
- [x] 하단 네비게이션 (FNB)
  - [x] 마지막 업데이트 시간
  - [x] 데이터 소스 정보
  - [x] AI 모델 및 언어 표시
- [x] 모달 (AI Model Selection)
  - [x] Gemini/GPT 선택 모달
- [x] 스테어 (Analysis Steps)
  - [x] 분석 단계 표시 컴포넌트

#### 5.3 CSS 스타일링

- [x] `web/static/css/globals.css` 생성
  - [x] Pretendard 폰트 로드 (CDN)
  - [x] 기본 스타일 리셋
  - [x] 커스텀 색상 팔레트 (다크 테마)
  - [x] 반응형 브레이크포인트 정의
  - [x] 네비게이션 스타일 (GNB, SNB, LNB, FNB)
  - [x] 아코디언 스타일
  - [x] 모달 스타일 (애니메이션 포함)
  - [x] 스테어 스타일
  - [x] 버튼, 입력, 테이블 스타일
  - [x] 유틸리티 클래스
  - [x] 스크롤바 커스터마이징
  - [x] 반응형 폰트 크기
  - [x] 프린트 스타일

#### 5.4 반응형 디자인

- [x] 모바일 레이아웃 최적화
  - [x] SNB 기본 숨김, 토글 가능
  - [x] 검색 바 숨김
  - [x] 그리드 1-2열 레이아웃
  - [x] 테이블 가로 스크롤
  - [x] 버튼 아이콘만 표시
  - [x] 모달 전체 화면
  - [x] FNB 세로 스택
- [x] 태블릿 레이아웃 최적화
  - [x] SNB 토글 가능
  - [x] 그리드 2-3열 레이아웃
  - [x] 검색 바 축소
  - [x] 테이블 최적화
- [x] 데스크톱 레이아웃 최적화
  - [x] SNB 항상 표시
  - [x] 그리드 4-6열 레이아웃
  - [x] 최대 너비 제한 (2xl)
  - [x] 전체 기능 표시
- [x] 추가 최적화
  - [x] 가로 모드 모바일 대응
  - [x] 터치 디바이스 최적화 (터치 타겟 크기)
  - [x] 고해상도 디스플레이 대응
  - [x] 프린트 스타일

---

### Part 6: 프론트엔드 로직 (Frontend Logic)

#### 6.1 전역 변수 및 상태 관리

- [x] `web/static/js/app.js` 생성
  - [x] `currentLang` (localStorage 기반, 기본값: 'ko')
  - [x] `currentModel` (localStorage 기반, 기본값: 'gemini')
  - [x] `usStockChart` (Lightweight Charts 인스턴스)
  - [x] `currentChartPick` (현재 선택 종목)
  - [x] `indicatorState` (기술적 지표 상태: rsi, macd, bb, sr)
  - [x] `currentChartPeriod` (차트 기간 상태)
  - [x] `realtimePriceInterval`, `macroAnalysisInterval` (인터벌 관리)
  - [x] `i18n` 객체 (한국어/영어 번역)
  - [x] 유틸리티 함수 (saveState, loadState, formatNumber, formatPercent, getColorClass, translateUI, fetchAPI)

#### 6.2 초기화 함수

- [x] `DOMContentLoaded` 이벤트 리스너
  - [x] `initApp()` 함수 구현
  - [x] `updateUSMarketDashboard()` 호출 (함수 존재 시)
  - [x] 언어/모델 설정 로드 (`loadState()`)
  - [x] UI 상태 업데이트 (`updateUIState()`)
  - [x] 이벤트 리스너 등록 (`registerEventListeners()`)
    - [x] SNB 토글
    - [x] 아코디언
    - [x] 모달 (열기/닫기)
    - [x] AI 모델 선택
    - [x] 탭 전환
    - [x] 언어 토글
    - [x] 차트 기간 버튼
    - [x] 기술적 지표 토글
    - [x] 윈도우 리사이즈
  - [x] 실시간 업데이트 인터벌 설정 (`setupUpdateIntervals()`)
    - [x] 실시간 가격 업데이트 (20초)
    - [x] 매크로 분석 갱신 (10분)
    - [x] 시간 표시 업데이트 (1초)
  - [x] 정리 함수 (`cleanupApp()`) - 페이지 언로드 시

#### 6.3 데이터 페칭 함수

- [x] `updateUSMarketDashboard()`
  - [x] Promise.all로 병렬 데이터 페칭
    - [x] `/api/us/portfolio` (Market Indices)
    - [x] `/api/us/smart-money` (Top Picks)
    - [x] `/api/us/etf-flows` (ETF Data)
    - [x] `/api/us/history-dates` (Historical Data)
  - [x] 각 섹션 렌더링 함수 호출 (함수 존재 시)
  - [x] 에러 핸들링 (개별 API 실패 시에도 계속 진행)
- [x] `reloadMacroAnalysis()`
  - [x] 매크로 분석만 별도 갱신
  - [x] 언어/모델 파라미터 전달
  - [x] 10분 주기 자동 갱신 (setupUpdateIntervals에서 설정)
- [x] `updateRealtimePrices()`
  - [x] 테이블에서 표시 중인 티커 수집
  - [x] `/api/realtime-prices` POST 요청
  - [x] 테이블 가격 셀 업데이트
  - [x] 가격 변경 시 플래시 애니메이션
  - [x] 색상 코딩 (상승/하락)
  - [x] 차트 마지막 캔들 업데이트 준비 (updateChartLastCandle 함수 호출)
  - [x] 20초 주기 자동 업데이트 (setupUpdateIntervals에서 설정)

#### 6.4 렌더링 함수

- [x] `renderUSMarketIndices(data)` (`web/static/js/render.js`)
  - [x] 지수 그리드 렌더링
  - [x] 가격 및 변동률 표시
  - [x] 색상 코딩 (상승/하락)
  - [x] 호버 효과
- [x] `renderUSSmartMoneyPicks(data)` (`web/static/js/render.js`)
  - [x] 테이블 행 생성
  - [x] Rank, Ticker, Name, Score, Price, Change, Sector 컬럼
  - [x] Score 색상 코딩 (80+: 파랑, 60+: 초록, 40+: 노랑)
  - [x] 클릭 이벤트 리스너 등록 (차트 로드)
  - [x] 행 선택 하이라이트
  - [x] data-ticker 속성 추가 (실시간 업데이트용)
- [x] `renderUSMacroAnalysis(data)` (`web/static/js/render.js`)
  - [x] 매크로 지표 그리드 렌더링
  - [x] 지표별 특수 스타일링 (VIX: 보라, Crypto: 노랑, Yield: 파랑)
  - [x] AI 분석 텍스트 표시 (언어별)
  - [x] 일일 변동률 표시
- [x] `renderUSETFFlows(data)` (`web/static/js/render.js`)
  - [x] Market Sentiment Score 표시
  - [x] Top Inflows 리스트 렌더링
  - [x] Top Outflows 리스트 렌더링
  - [x] AI 분석 텍스트 표시
- [x] `renderUSCalendar(data)` (`web/static/js/render.js`)
  - [x] 경제 캘린더 렌더링
  - [x] 날짜별 그룹화
  - [x] Impact 레벨 표시 (High/Medium/Low)
  - [x] 이벤트 설명 표시

#### 6.5 차트 관련 함수

- [x] `loadUSStockChart(pick, idx, period)`
  - [x] 차트 데이터 페칭
  - [x] Lightweight Charts 인스턴스 생성
  - [x] 캔들스틱 시리즈 추가
  - [x] AI 요약 로드
- [x] `toggleIndicator(type)`
  - [x] 기술적 지표 토글
  - [x] 지표 데이터 페칭
  - [x] 차트에 시리즈 추가/제거
- [x] `renderIndicator(type, data)`
  - [x] RSI, MACD, BB, S/R 렌더링

#### 6.6 유틸리티 함수

- [x] `translateUI()`
  - [x] i18n 딕셔너리 정의
  - [x] `data-i18n` 속성 기반 번역
- [x] `formatNumber(value)`
- [x] `formatPercent(value)`
- [x] `getColorForChange(change)` (구현: `getColorClass()`)

#### 6.7 이벤트 리스너

- [x] 언어 전환 버튼
- [x] 모델 선택 버튼
- [x] 차트 기간 선택 버튼
- [x] 기술적 지표 토글 버튼
- [x] 테이블 행 클릭

#### 6.8 에러 핸들링

- [ ] API 에러 처리
- [ ] 네트워크 에러 처리
- [ ] 사용자 친화적 에러 메시지

---

## 🔧 공통 작업

### 로깅 시스템

- [ ] `core/config.py` 구현
  - [ ] 로깅 설정
  - [ ] 경로 상수 정의
- [ ] 모든 스크립트에 로깅 적용
  - [ ] `logs/pipeline.log`
  - [ ] `logs/server.log`

### 에러 핸들링

- [ ] 전역 예외 핸들러
- [ ] Retry 로직 (Exponential Backoff)
- [ ] Rate Limiting 처리

### 테스트 및 검증

- [ ] 각 Part 완료 후 수동 테스트
- [ ] 데이터 파일 생성 확인
- [ ] API 엔드포인트 동작 확인
- [ ] 프론트엔드 UI 동작 확인

---

## 📝 참고 사항

### 실행 순서 요약

1. **Part 1 완료** → `data/raw/`, `data/processed/`에 CSV 파일 생성 확인
2. **Part 2 완료** → `smart_money_picks_v2.csv` 생성 확인
3. **Part 3 완료** → `ai_summaries.json`, `macro_analysis.json` 생성 확인
4. **Part 4 완료** → Flask 서버 실행, API 엔드포인트 테스트
5. **Part 5 완료** → HTML 템플릿 렌더링 확인
6. **Part 6 완료** → 대시보드 전체 동작 확인

### 필수 의존성

- Python 3.10+
- Google Gemini API Key
- (선택) OpenAI API Key
- (선택) FRED API Key

### 주요 출력 파일 체크리스트

- [ ] `us_daily_prices.csv`
- [ ] `us_volume_analysis.csv`
- [ ] `us_13f_holdings.csv`
- [ ] `us_etf_flows.csv`
- [ ] `smart_money_picks_v2.csv`
- [ ] `sector_heatmap.json`
- [ ] `options_flow.json`
- [ ] `macro_analysis.json`
- [ ] `ai_summaries.json`
- [ ] `final_top10_report.json`
- [ ] `smart_money_current.json`
- [ ] `weekly_calendar.json`

---

**작성일:** 2025-01-XX  
**버전:** 1.0.0  
**참조 문서:** DIR.md, MRD.md, PRD.md, TRD.md, PART1-6 문서들
