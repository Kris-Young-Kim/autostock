6. Mermaid Diagrams (System Architecture)
시스템의 구조와 데이터 흐름을 명확히 하기 위한 Mermaid Markdown 다이어그램입니다. 이를 ARCHITECTURE.md 등의 파일로 저장하여 관리할 수 있습니다.
6.1. System Context Diagram (C4 Level 1)
전체 시스템의 큰 그림을 보여줍니다.
code
Mermaid
graph TB
    subgraph "User Environment"
        User[👤 Active Investor]
        Browser[🌐 Web Browser]
    end

    subgraph "US Market Alpha Platform"
        WebServer[🚀 Flask Web Server :3000]
        AnalysisEngine[⚙️ Analysis Engine (Python)]
        DB[(🗄️ File System / JSON Storage)]
    end

    subgraph "External Data Providers"
        YFinance[Yahoo Finance API]
        SEC[SEC EDGAR (13F)]
        Google[Google Gemini API]
    end

    User -->|View Dashboard| Browser
    Browser -->|HTTP Request| WebServer
    WebServer -->|Read Analyzed Data| DB
    AnalysisEngine -->|Write Results| DB
    AnalysisEngine -->|Fetch Prices| YFinance
    AnalysisEngine -->|Scrape Filings| SEC
    AnalysisEngine -->|Generate Insights| Google
6.2. Data Pipeline Sequence (ETL & AI Flow)
데이터가 수집되어 AI 분석을 거쳐 저장되는 순서도입니다.
code
Mermaid
sequenceDiagram
    participant Scheduler as ⏰ Scheduler
    participant Collector as 📥 Data Collector
    participant Quant as 🧮 Quant Engine
    participant AI as 🤖 Gemini Agent
    participant Storage as 💾 JSON/CSV

    Note over Scheduler: Daily Market Close
    Scheduler->>Collector: Trigger update_all.py
    
    rect rgb(200, 220, 240)
        Note right of Collector: Phase 1: Data Collection
        Collector->>Collector: Fetch OHLCV (YFinance)
        Collector->>Collector: Fetch 13F/Insider Data
        Collector->>Collector: Fetch Options Flow
    end

    rect rgb(220, 240, 200)
        Note right of Quant: Phase 2: Factor Scoring
        Quant->>Collector: Load Raw Data
        Quant->>Quant: Calc Supply/Demand Score
        Quant->>Quant: Calc Technical Indicators (RSI, BB)
        Quant->>Quant: Calc Smart Money Score
    end

    rect rgb(240, 200, 200)
        Note right of AI: Phase 3: AI Analysis
        AI->>Quant: Get Top 20 Candidates
        AI->>AI: Analyze Macro Context
        AI->>AI: Generate Stock Summary (News + Quant)
    end

    AI->>Storage: Save 'smart_money_picks.csv'
    AI->>Storage: Save 'ai_summaries.json'
    AI->>Storage: Save 'macro_analysis.json'
    
    Note over Storage: Data Ready for Web Server
6.3. Entity Relationship (Data Model)
시스템에서 다루는 주요 데이터 객체 간의 관계입니다.
code
Mermaid
erDiagram
    STOCK ||--o{ PRICE_HISTORY : has
    STOCK ||--o{ INSTITUTIONAL_HOLDING : owned_by
    STOCK ||--o{ INSIDER_TRADE : has
    STOCK ||--|| QUANT_SCORE : calculated
    STOCK ||--|| AI_REPORT : analyzed

    STOCK {
        string ticker PK
        string name
        string sector
        string industry
    }

    QUANT_SCORE {
        float composite_score
        float supply_demand_score
        float institutional_score
        string grade "S, A, B, C, F"
    }

    AI_REPORT {
        string summary
        string sentiment "Bullish, Bearish"
        string risks
        timestamp updated_at
    }

    INSTITUTIONAL_HOLDING {
        string fund_name
        int shares
        float change_pct
        date report_date
    }
7. User Flow (UX Flowchart)
사용자가 플랫폼에 접속하여 투자 의사결정을 내리기까지의 여정(Journey)을 정의합니다.
7.1. User Journey Map
시장 파악 (Macro Check): 접속 직후 시장이 안전한지(Risk-On) 위험한지(Risk-Off) 확인.
종목 발굴 (Discovery): 스마트 머니가 매집 중인 Top 10 종목 스캔.
상세 분석 (Deep Dive): 관심 종목의 차트 확인 및 AI 리포트 정독.
검증 (Validation): 섹터 흐름(ETF) 및 옵션 포지션 확인으로 확신 강화.
실행 (Action): 실제 트레이딩 (외부 HTS/MTS 사용).
7.2. Flow Diagram
code
Mermaid
graph TD
    Start((🟢 Start)) --> Dashboard[Main Dashboard :3000]
    
    subgraph "1. Market Check"
        Dashboard --> Macro[Check Macro Analysis]
        Macro --> RiskCheck{Risk On?}
        RiskCheck -->|Yes| BullStrategy[Strategy: Aggressive Buy]
        RiskCheck -->|No| BearStrategy[Strategy: Cash / Hedge]
    end
    
    subgraph "2. Discovery"
        BullStrategy --> TopPicks[View Smart Money Top 10]
        BearStrategy --> TopPicks
        TopPicks --> Filter[Filter by Sector/Score]
        Filter --> SelectStock[Click Specific Stock]
    end
    
    subgraph "3. Deep Dive"
        SelectStock --> DetailView[Stock Detail Modal]
        DetailView --> Chart[View Tech Chart\n(RSI, Support/Resist)]
        DetailView --> AIRead[Read AI Summary Report]
        AIRead --> Conviction{High Conviction?}
    end
    
    subgraph "4. Validation"
        Conviction -->|Maybe| Options[Check Options Flow]
        Options -->|Bullish Flow| Confirm[Confirm Trade]
        Options -->|Bearish Flow| Discard[Discard Stock]
        Conviction -->|No| BackToPicks[Back to Top Picks]
    end
    
    Confirm --> Trade((🔴 Execute Trade))
    Discard --> BackToPicks
💡 문서 활용 가이드
MRD: 투자자나 이해관계자에게 "왜 이 시스템이 필요한가?"를 설득할 때 사용하십시오.
Mermaid Diagrams: ARCHITECTURE.md 파일에 저장하거나, GitHub/GitLab의 마크다운 뷰어에서 시스템 구조를 파악할 때 사용하십시오.
User Flow: 프론트엔드 개발 시 UI/UX 동선을 설계하는 기준점(Reference)으로 활용하십시오.
이로써 데이터 수집부터 사용자 경험 설계까지 완벽하게 갖춰진, 전문가 수준의 플랫폼 청사진이 완성되었습니다.