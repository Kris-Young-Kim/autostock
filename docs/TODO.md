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

- [ ] `pipeline/update_all.py` 구현
  - [ ] Part 1의 모든 스크립트 순차 실행
  - [ ] `--quick` 옵션 (AI 분석 제외)
  - [ ] 에러 핸들링 및 로깅

**검증:**

```bash
python pipeline/update_all.py --quick  # 빠른 테스트
python pipeline/update_all.py           # 전체 실행
```

---

### Part 2: 분석 및 스크리닝 (Analysis & Screening)

#### 2.1 6-Factor 종합 스크리닝 (`smart_money_screener_v2.py`)

- [ ] `pipeline/smart_money_screener_v2.py` 구현
  - [ ] 데이터 로드 (Volume, 13F, ETF 데이터 병합)
  - [ ] Technical Analysis 함수 구현
    - [ ] RSI (14-day) 계산
    - [ ] MACD (12, 26, 9) 계산
    - [ ] Moving Averages (20, 50, 200) 계산
    - [ ] Golden/Death Cross 감지
    - [ ] Technical Score 계산 (0-100)
  - [ ] Fundamental Analysis 함수 구현
    - [ ] P/E, Forward P/E, P/B 수집
    - [ ] Revenue Growth, Earnings Growth 수집
    - [ ] ROE, Profit Margin 수집
    - [ ] Fundamental Score 계산 (0-100)
  - [ ] Analyst Ratings 함수 구현
    - [ ] Target Price, Upside Potential 계산
    - [ ] Recommendation Key 파싱
    - [ ] Analyst Score 계산 (0-100)
  - [ ] Relative Strength 함수 구현
    - [ ] SPY 대비 20일, 60일 수익률 비교
    - [ ] RS Score 계산 (0-100)
  - [ ] Composite Score 계산 (가중 평균)
    - [ ] Supply/Demand: 25%
    - [ ] Institutional: 20%
    - [ ] Technical: 20%
    - [ ] Fundamental: 15%
    - [ ] Analyst: 10%
    - [ ] Relative Strength: 10%
  - [ ] Grade 할당 (S, A, B, C, D, F)
  - [ ] `smart_money_picks_v2.csv` 저장

**출력 파일:**

- `data/processed/smart_money_picks_v2.csv`

#### 2.2 섹터 히트맵 (`sector_heatmap.py`)

- [ ] `pipeline/sector_heatmap.py` 구현
  - [ ] 11개 S&P 섹터 ETF 추적
    - [ ] XLK (Technology), XLF (Financials), XLV (Healthcare) 등
  - [ ] 섹터별 퍼포먼스 계산
  - [ ] Treemap 데이터 구조 생성
  - [ ] `sector_heatmap.json` 저장

**출력 파일:**

- `data/processed/sector_heatmap.json`

#### 2.3 옵션 플로우 분석 (`options_flow.py`)

- [ ] `pipeline/options_flow.py` 구현
  - [ ] 주요 종목 옵션 체인 데이터 수집
  - [ ] Put/Call Ratio 계산
  - [ ] Unusual Activity 감지
  - [ ] `options_flow.json` 저장

**출력 파일:**

- `data/processed/options_flow.json`

#### 2.4 인사이더 추적 (`insider_tracker.py`)

- [ ] `pipeline/insider_tracker.py` 구현
  - [ ] 최근 6개월 인사이더 매매 추적
  - [ ] Cluster Buying 감지
  - [ ] `insider_moves.json` 저장

**출력 파일:**

- `data/processed/insider_moves.json`

#### 2.5 포트폴리오 리스크 분석 (`portfolio_risk.py`)

- [ ] `pipeline/portfolio_risk.py` 구현
  - [ ] 상관관계 매트릭스 계산
  - [ ] 포트폴리오 변동성 계산
  - [ ] `portfolio_risk.json` 저장

**출력 파일:**

- `data/processed/portfolio_risk.json`

---

### Part 3: AI 분석 (AI Analysis)

#### 3.1 매크로 경제 분석 (`macro_analyzer.py`)

- [ ] `pipeline/macro_analyzer.py` 구현
  - [ ] 매크로 지표 수집
    - [ ] VIX, DXY, 2Y/10Y Yield, GOLD, OIL, BTC
    - [ ] SPY, QQQ
  - [ ] Yield Spread 계산
  - [ ] 뉴스 수집 (Google News RSS)
  - [ ] Gemini 3.0 AI 분석 통합
    - [ ] 한국어 분석 생성
    - [ ] 영어 분석 생성
  - [ ] `macro_analysis.json` 저장
  - [ ] `macro_analysis_en.json` 저장 (선택)

**출력 파일:**

- `data/processed/macro_analysis.json`
- `data/processed/macro_analysis_en.json`

#### 3.2 개별 종목 AI 요약 (`ai_summary_generator.py`)

- [ ] `pipeline/ai_summary_generator.py` 구현
  - [ ] Smart Money Picks 상위 20개 종목 선택
  - [ ] 각 종목별 뉴스 수집
  - [ ] Gemini AI로 투자 요약 생성
    - [ ] 한국어 요약
    - [ ] 영어 요약
  - [ ] `ai_summaries.json` 저장

**출력 파일:**

- `data/processed/ai_summaries.json`

#### 3.3 최종 Top 10 리포트 (`final_report_generator.py`)

- [ ] `pipeline/final_report_generator.py` 구현
  - [ ] Quant Score와 AI 분석 결합
  - [ ] Final Score 계산 (Quant 80% + AI 20%)
  - [ ] Top 10 종목 선정
  - [ ] `final_top10_report.json` 저장
  - [ ] `smart_money_current.json` 저장 (대시보드용)

**출력 파일:**

- `data/processed/final_top10_report.json`
- `data/processed/smart_money_current.json`

#### 3.4 경제 캘린더 (`economic_calendar.py`)

- [ ] `pipeline/economic_calendar.py` 구현
  - [ ] 주요 경제 이벤트 수집
  - [ ] AI 영향도 분석 (High Impact 이벤트)
  - [ ] `weekly_calendar.json` 저장

**출력 파일:**

- `data/processed/weekly_calendar.json`

#### 3.5 통합 업데이트 스크립트 업데이트

- [ ] `pipeline/update_all.py`에 Part 3 스크립트 추가
  - [ ] `macro_analyzer.py` 실행
  - [ ] `ai_summary_generator.py` 실행
  - [ ] `final_report_generator.py` 실행
  - [ ] `economic_calendar.py` 실행

**검증:**

```bash
python pipeline/update_all.py  # 전체 파이프라인 실행
```

---

## 🌐 Phase 2: 웹 서버 및 프론트엔드

### Part 4: 웹 서버 (Web Server)

#### 4.1 Flask 애플리케이션 구조 설정

- [ ] `web/` 디렉토리 구조 생성
  - [ ] `web/app.py` - Flask 메인 애플리케이션
  - [ ] `web/routes.py` - API 엔드포인트 정의 (선택)
  - [ ] `web/templates/` - HTML 템플릿
  - [ ] `web/static/` - CSS, JS, Assets

#### 4.2 핵심 유틸리티 함수 구현

- [ ] 섹터 매핑 함수 (`get_sector`)
  - [ ] SECTOR_MAP 정의 (주요 종목)
  - [ ] yfinance를 통한 동적 섹터 조회
  - [ ] 섹터 캐시 파일 (`sector_cache.json`) 구현
- [ ] 기술적 지표 계산 함수
  - [ ] `calculate_rsi()` 구현
  - [ ] `analyze_trend()` 구현

#### 4.3 US Market API 엔드포인트 구현

- [ ] `/api/us/portfolio` - 시장 지수 데이터
  - [ ] Dow Jones, S&P 500, NASDAQ, VIX 등
  - [ ] 실시간 가격 및 변동률 계산
- [ ] `/api/us/smart-money` - Smart Money Picks
  - [ ] `smart_money_current.json` 또는 CSV 로드
  - [ ] 실시간 가격 업데이트
  - [ ] Performance 계산 (추천 시점 대비 수익률)
- [ ] `/api/us/etf-flows` - ETF 자금 흐름
  - [ ] `us_etf_flows.csv` 로드
  - [ ] AI 분석 텍스트 포함
- [ ] `/api/us/stock-chart/<ticker>` - 차트 데이터
  - [ ] yfinance를 통한 OHLC 데이터
  - [ ] Lightweight Charts 형식으로 변환
- [ ] `/api/us/macro-analysis` - 매크로 분석
  - [ ] `macro_analysis.json` 로드
  - [ ] 언어/모델 선택 지원 (`lang`, `model` 파라미터)
  - [ ] 주요 지표 실시간 업데이트
- [ ] `/api/us/sector-heatmap` - 섹터 히트맵
  - [ ] `sector_heatmap.json` 로드
- [ ] `/api/us/options-flow` - 옵션 플로우
  - [ ] `options_flow.json` 로드
- [ ] `/api/us/ai-summary/<ticker>` - AI 요약
  - [ ] `ai_summaries.json`에서 특정 종목 요약 반환
  - [ ] 언어 선택 지원
- [ ] `/api/us/technical-indicators/<ticker>` - 기술적 지표
  - [ ] RSI, MACD, Bollinger Bands 계산
  - [ ] Support/Resistance 레벨 탐지
- [ ] `/api/us/calendar` - 경제 캘린더
  - [ ] `weekly_calendar.json` 로드
- [ ] `/api/us/history-dates` - 과거 분석 날짜 목록
- [ ] `/api/us/history/<date>` - 특정 날짜 분석 결과

#### 4.4 실시간 가격 업데이트 API

- [ ] `/api/realtime-prices` (POST)
  - [ ] 배치 티커 리스트 받기
  - [ ] yfinance를 통한 실시간 가격 조회
  - [ ] OHLC 데이터 반환

#### 4.5 서버 실행 설정

- [ ] `web/app.py` 메인 실행 블록
  - [ ] Port 3000 설정
  - [ ] Debug 모드 설정
- [ ] `bin/run_server.sh` 생성
  ```bash
  #!/bin/bash
  cd "$(dirname "$0")/.."
  python web/app.py
  ```

**검증:**

```bash
python web/app.py
# 또는
bash bin/run_server.sh
```

---

### Part 5: 프론트엔드 UI (Frontend UI)

#### 5.1 HTML 템플릿 구조

- [ ] `web/templates/index.html` 생성
  - [ ] 기본 HTML5 구조
  - [ ] Tailwind CSS CDN 연결
  - [ ] Pretendard 폰트 적용 (globals.css)
  - [ ] 메타 태그 설정 (반응형)

#### 5.2 대시보드 레이아웃 구성

- [ ] 헤더 섹션
  - [ ] 로고/제목
  - [ ] 언어 전환 버튼 (KO/EN)
  - [ ] AI 모델 선택 (Gemini/GPT)
- [ ] Market Indices 섹션
  - [ ] 그리드 레이아웃 (11개 지수)
  - [ ] 실시간 가격 및 변동률 표시
  - [ ] 색상 코딩 (상승/하락)
- [ ] Smart Money Picks 테이블
  - [ ] 상위 10개 종목 리스트
  - [ ] 컬럼: Rank, Ticker, Name, Score, Price, Change, Sector
  - [ ] 클릭 가능한 행 (차트 로드)
- [ ] 차트 뷰 섹션
  - [ ] Lightweight Charts 컨테이너
  - [ ] 차트 헤더 (Ticker, Name, Score)
  - [ ] 기간 선택 버튼 (1M, 3M, 6M, 1Y, 2Y, 5Y)
  - [ ] 기술적 지표 토글 버튼 (RSI, MACD, BB, S/R)
- [ ] AI Summary 섹션
  - [ ] 선택 종목의 AI 요약 표시
  - [ ] 언어 전환 지원
- [ ] Macro Analysis 섹션
  - [ ] 매크로 지표 그리드
  - [ ] AI 분석 텍스트 블록
- [ ] ETF Flows 섹션
  - [ ] 섹터별 자금 흐름 표시
- [ ] 경제 캘린더 섹션
  - [ ] 주간 이벤트 리스트

#### 5.3 CSS 스타일링

- [ ] `web/static/css/globals.css` 생성
  - [ ] Pretendard 폰트 로드 (CDN)
  - [ ] 기본 스타일 리셋
  - [ ] 커스텀 색상 팔레트
  - [ ] 반응형 브레이크포인트

#### 5.4 반응형 디자인

- [ ] 모바일 레이아웃 최적화
- [ ] 태블릿 레이아웃 최적화
- [ ] 데스크톱 레이아웃 최적화

---

### Part 6: 프론트엔드 로직 (Frontend Logic)

#### 6.1 전역 변수 및 상태 관리

- [ ] `web/templates/index.html`에 `<script>` 섹션 추가
  - [ ] `currentLang` (localStorage 기반)
  - [ ] `currentModel` (localStorage 기반)
  - [ ] `usStockChart` (Lightweight Charts 인스턴스)
  - [ ] `currentChartPick` (현재 선택 종목)
  - [ ] `indicatorState` (기술적 지표 상태)

#### 6.2 초기화 함수

- [ ] `DOMContentLoaded` 이벤트 리스너
  - [ ] `updateUSMarketDashboard()` 호출
  - [ ] 언어/모델 설정 로드
  - [ ] 이벤트 리스너 등록
  - [ ] 실시간 업데이트 인터벌 설정

#### 6.3 데이터 페칭 함수

- [ ] `updateUSMarketDashboard()`
  - [ ] Promise.all로 병렬 데이터 페칭
  - [ ] 각 섹션 렌더링 함수 호출
- [ ] `reloadMacroAnalysis()`
  - [ ] 매크로 분석만 별도 갱신
  - [ ] 10분 주기 자동 갱신
- [ ] `updateRealtimePrices()`
  - [ ] 20초 주기 가격 업데이트
  - [ ] 테이블 가격 셀 업데이트
  - [ ] 차트 마지막 캔들 업데이트

#### 6.4 렌더링 함수

- [ ] `renderUSMarketIndices(data)`
  - [ ] 지수 그리드 렌더링
- [ ] `renderUSSmartMoneyPicks(data)`
  - [ ] 테이블 행 생성
  - [ ] 클릭 이벤트 리스너 등록
- [ ] `renderUSMacroAnalysis(data)`
  - [ ] 매크로 지표 그리드 렌더링
  - [ ] AI 분석 텍스트 표시
- [ ] `renderUSETFFlows(data)`
  - [ ] ETF 플로우 리스트 렌더링
- [ ] `renderUSCalendar(data)`
  - [ ] 경제 캘린더 렌더링

#### 6.5 차트 관련 함수

- [ ] `loadUSStockChart(pick, idx, period)`
  - [ ] 차트 데이터 페칭
  - [ ] Lightweight Charts 인스턴스 생성
  - [ ] 캔들스틱 시리즈 추가
  - [ ] AI 요약 로드
- [ ] `toggleIndicator(type)`
  - [ ] 기술적 지표 토글
  - [ ] 지표 데이터 페칭
  - [ ] 차트에 시리즈 추가/제거
- [ ] `renderIndicator(type, data)`
  - [ ] RSI, MACD, BB, S/R 렌더링

#### 6.6 유틸리티 함수

- [ ] `translateUI()`
  - [ ] i18n 딕셔너리 정의
  - [ ] `data-i18n` 속성 기반 번역
- [ ] `formatNumber(value)`
- [ ] `formatPercent(value)`
- [ ] `getColorForChange(change)`

#### 6.7 이벤트 리스너

- [ ] 언어 전환 버튼
- [ ] 모델 선택 버튼
- [ ] 차트 기간 선택 버튼
- [ ] 기술적 지표 토글 버튼
- [ ] 테이블 행 클릭

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
