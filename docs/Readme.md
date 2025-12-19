4. README.md
🇺🇸 US Market Smart Money Alpha Platform
![alt text](https://img.shields.io/badge/version-2.1.0-blue)
![alt text](https://img.shields.io/badge/python-3.10%2B-green)
![alt text](https://img.shields.io/badge/license-Proprietary-red)
"Institutions leave footprints. AI finds them."
본 플랫폼은 30년 경력의 월스트리트 분석 로직과 최신 Generative AI 기술을 결합하여, 기관 투자자의 수급을 추적하고 최적의 매매 타이밍을 포착하는 전문가용 하이브리드 투자 시스템입니다.
🌟 Key Features (핵심 기능)
Smart Money Radar (기관 수급 포착)
단순 가격 변동이 아닌, OBV, MFI, 13F Holdings, Dark Pool Index를 융합하여 '매집(Accumulation)'과 '분산(Distribution)' 단계를 식별합니다.
AI-Powered Macro & Micro Analysis
Gemini 3.0 Pro가 실시간 매크로 지표(VIX, Yield Curve)를 분석하여 '시장 날씨'를 예보합니다.
개별 종목의 펀더멘털과 수급 데이터를 텍스트로 합성하여 "Actionable Insight"를 제공합니다.
Institutional Grade Dashboard
TradingView 스타일의 경량 차트와 실시간 섹터 히트맵.
반응형 웹 인터페이스 (Port: 3000) 제공.
6-Factor Scoring Model
Supply/Demand, Institutional, Technical, Fundamental, Analyst, Relative Strength 6가지 팩터를 가중 평균하여 S급 종목을 자동 필터링합니다.
🛠 Installation & Setup
Prerequisites
Python 3.10 이상
Google Cloud API Key (Gemini)
1. Repository Clone & Environment Setup
code
Bash
git clone https://github.com/your-org/us-market-alpha.git
cd us-market-alpha

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 의존성 패키지 설치
pip install -r requirements.txt
2. Configuration (.env)
프로젝트 루트에 .env 파일을 생성하고 아래 내용을 입력하세요.
code
Ini
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here # Optional (Fallback)
FLASK_ENV=development
DATA_DIR=./data
PORT=3000
🚀 Usage Guide
Step 1: Data Pipeline Execution (데이터 분석)
최초 실행 시, 과거 데이터를 포함한 대규모 분석이 필요합니다. (약 5~10분 소요)
code
Bash
# 전체 데이터 수집 및 AI 분석 파이프라인 실행
python pipeline/update_all.py

# (옵션) AI 분석을 건너뛰고 퀀트 데이터만 빠르게 업데이트
python pipeline/update_all.py --quick
Step 2: Launch Web Dashboard (서버 구동)
분석이 완료되면 웹 서버를 구동하여 결과를 확인합니다.
code
Bash
# Flask 웹 서버 실행 (Port 3000)
python web/app.py
Access: 브라우저를 열고 http://localhost:3000 으로 접속하세요.
📊 Dashboard Manual
Section	Description
Market Indices	S&P500, Nasdaq 등 주요 지수 및 VIX, 유가 실시간 현황
Top Picks Table	6-Factor 모델로 엄선된 상위 10개 종목 리스트 (AI 점수 포함)
Chart View	선택 종목의 상세 캔들 차트 (BB, RSI, MACD 보조지표 포함)
Macro AI	현재 시장 상황에 대한 AI의 종합 리포트 (Risk-On/Off 판단)
ETF Flows	섹터별 자금 유출입 현황 (Sector Rotation 포착용)
⚠️ Disclaimer
본 소프트웨어는 투자 판단을 보조하기 위한 도구이며, 최종 투자 결정에 대한 책임은 사용자에게 있습니다. 제공되는 'AI 추천' 및 'Score'는 과거 데이터와 확률적 모델에 기반한 추정치입니다.
Copyright © 2025 US Market Alpha Team. All Rights Reserved.