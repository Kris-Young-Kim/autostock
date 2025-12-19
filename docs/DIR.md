3. Directory Structure (DIR.md)
엔터프라이즈급 유지보수성을 고려하여 모듈화된 구조로 재설계하였습니다.
code
Text
US-Market-Alpha-Platform/
├── .env                        # [Security] API Keys & Config Secrets
├── .gitignore                  # Git Exclusion Rules
├── requirements.txt            # Dependency Definitions
├── README.md                   # Project Documentation
│
├── bin/                        # [Executable] 실행 스크립트 모음
│   ├── run_server.sh           # 서버 실행 쉘 스크립트
│   └── run_pipeline.sh         # 데이터 파이프라인 실행 쉘 스크립트
│
├── core/                       # [Core Logic] 핵심 비즈니스 로직
│   ├── __init__.py
│   ├── config.py               # 설정 관리 (상수, 경로 등)
│   ├── data_loader.py          # 데이터 수집/로드 추상화 클래스
│   ├── screener.py             # 6-Factor 알고리즘 엔진
│   └── ai_agent.py             # LLM 연동 및 프롬프트 엔지니어링 모듈
│
├── web/                        # [Web Application] Flask 서버
│   ├── app.py                  # Flask App Entry Point (Port 3000)
│   ├── routes.py               # API Endpoint 정의
│   ├── templates/              # HTML Frontend
│   │   └── index.html          # Main Dashboard
│   └── static/                 # CSS, JS, Assets
│
├── pipeline/                   # [Data Pipeline] 배치 작업 스크립트
│   ├── 01_collect_prices.py    # 가격 데이터 수집
│   ├── 02_analyze_volume.py    # 수급/거래량 분석
│   ├── 03_analyze_13f.py       # 기관 보유량 분석
│   ├── 04_etf_flows.py         # ETF 자금 흐름
│   ├── 05_macro_view.py        # 매크로 시황 분석
│   └── update_all.py           # 전체 파이프라인 오케스트레이션
│
├── data/                       # [Data Storage] 데이터 저장소
│   ├── raw/                    # 원본 수집 데이터
│   │   ├── daily_prices.csv
│   │   └── stocks_list.csv
│   └── processed/              # 분석 완료된 데이터
│       ├── smart_money_picks.csv
│       ├── ai_summaries.json
│       ├── macro_analysis.json
│       └── options_flow.json
│
└── logs/                       # [Logging] 시스템 로그
    ├── pipeline.log
    └── server.log