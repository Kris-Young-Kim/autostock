1. PRD (Product Requirements Document)
프로젝트명: US Market Smart Money Alpha Platform (Ver 2.0)
작성자: Chief Quant Analyst & AI Lead
문서 등급: Confidential (Internal Use)
1.1. Executive Summary
본 플랫폼은 일반적인 기술적 분석을 넘어, 시장을 움직이는 **'스마트 머니(Smart Money: 기관, 헤지펀드, 내부자)'**의 흔적을 추적하여 초과 수익(Alpha)을 창출하는 것을 목표로 합니다.
SEC 13F 공시, Dark Pool 거래량 추정, 옵션 시장의 Gamma Exposure(GEX) 등 파편화된 고급 데이터를 ETL(Extract, Transform, Load) 파이프라인으로 통합하고, Gemini 3.0 Pro 기반의 AI 에이전트가 이를 해석하여 '매수/매도' 액션 아이템을 도출합니다.
1.2. Strategic Objectives (핵심 목표)
Information Asymmetry 해소: 기관 투자자만이 접근 가능했던 수급 및 파생상품 데이터를 개인 투자자에게 직관적으로 시각화.
Process Automation: 데이터 수집 → 팩터 스코어링 → 리포트 작성의 전 과정을 Zero-Touch 자동화.
Alpha Generation: 벤치마크(S&P 500) 대비 연평균 +15% 이상의 초과 수익률 달성 가능한 포트폴리오 제안.
1.3. Detailed Features (상세 기능 명세)
A. Smart Money Tracking Engine (수급 추적 엔진)
Institutional Accumulation:
13F 분기 보고서와 일별 거래량 패턴을 결합하여, 보고서 발표 전 '선취매' 패턴 탐지.
VWAP(거래량 가중 평균가) 대비 주가 괴리율을 통한 기관 평단가 추정.
Insider Activity Decoder:
단순 매수가 아닌 'Cluster Buying(복수 임원의 동시 매수)' 및 'Non-Open Market 매수' 필터링.
Options Flow Analysis:
비정상적인 Call/Put 볼륨 비율(PCR) 및 OTM(Out of The Money) 대량 베팅 감지.
Market Maker의 델타 헤징 방향성 예측.
B. Multi-Factor Quant Model (6-Factor Scoring)
각 종목에 대해 0~100점의 Composite Score를 산출하며, 가중치는 시장 국면에 따라 동적으로 조정됨 (Dynamic Asset Allocation).
Factor	Description	Key Metrics	Weight (Base)
Supply/Demand	수급 강도	OBV, MFI, Volume Surge, Dark Pool Index	25%
Institutional	기관/내부자	Inst. Ownership %, Insider Buy/Sell Ratio	20%
Technical	추세/모멘텀	MA Alignment, RSI Divergence, MACD Histogram	20%
Fundamental	내재 가치	Forward P/E, PEG Ratio, FCF Yield	15%
Analyst	시장 기대치	Consensus Target, Earnings Surprise History	10%
Relative Strength	상대 강도	vs SPY, vs Sector ETF (RS Rating)	10%
C. AI Financial Analyst (Generative AI)
Macro Sentinel: VIX, 금리, 유가, 달러 인덱스를 종합하여 시장의 'Risk Regime(Risk-On/Off)'을 정의.
Narrative Generator: 정량적 스코어(Quant)의 Why를 설명. 뉴스 헤드라인과 재무제표를 결합하여 "왜 지금 사야 하는가?"에 대한 스토리텔링 생성.
D. Interactive Dashboard (Web UI)
Real-time WebSocket Simulation: 20초 주기 폴링으로 장중 실시간 시세 및 변동성 반영.
Dynamic Sector Heatmap: S&P 11개 섹터의 자금 흐름을 트리맵(Treemap)으로 시각화.