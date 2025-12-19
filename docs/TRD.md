2. TRD (Technical Requirements Document)
시스템 아키텍처 및 기술 명세
2.1. System Architecture Diagram
code
Mermaid
graph TD
    A[Data Sources] -->|Yahoo Fin, SEC, News| B(ETL Pipeline / Python)
    B -->|Cleaned Data| C{Analysis Engine}
    C -->|Quant Algo| D[Smart Money Screener]
    C -->|Prompt Eng| E[Gemini 3.0 / GPT-4]
    D & E -->|JSON/CSV Storage| F[Flat-File Database]
    F -->|API Read| G[Flask Web Server :3000]
    G -->|JSON Response| H[Frontend / Dashboard]
2.2. Technology Stack (기술 스택 상세)
Core Runtime: Python 3.10+ (Type Hinting 적용)
Web Framework: Flask 3.0 (Production-ready configuration)
AI Integration:
google-generativeai: Gemini 3.0 Pro (High Reasoning)
openai: GPT-4-Turbo (Fallback Model)
Data Processing:
pandas & numpy: 벡터 연산 최적화
ta: Technical Analysis Library
Storage Strategy:
Tier 1 (Hot): In-Memory Caching (Python Dict) for Real-time prices.
Tier 2 (Warm): JSON/CSV Files for persistence (NoSQL DB 도입 전 단계, I/O 오버헤드 최소화).
Frontend:
Tailwind CSS (Utility-first styling)
Lightweight Charts (Canvas based high-performance charting)
2.3. Data Flow & Processing Strategy
Batch Processing (T-1 Analysis):
매일 장 마감 후 update_all.py 실행.
전 종목(500+)에 대한 6-Factor Scoring 및 AI 리포트 생성 → 정적 파일로 저장.
Real-time Processing (Intraday):
프론트엔드 요청 시 yfinance를 통해 1분/5분 봉 데이터 Fetching.
기존 분석된 스코어(Batch)에 실시간 등락률(Real-time)을 결합하여 대시보드 갱신.
2.4. Server Specification
Port: 3000 (User Defined)
Concurrency: Threaded execution supported (Flask default).
API Response Time Goal: < 200ms (Cached Data), < 1s (Real-time Fetch).
Error Handling: Global Exception Handler 적용, 실패한 API 호출에 대한 Retry Logic (Exponential Backoff).