#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration and Logging Setup
핵심 설정 관리 및 로깅 초기화
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = Path(os.getenv('DATA_DIR', PROJECT_ROOT / 'data'))
DATA_RAW_DIR = DATA_DIR / 'raw'
DATA_PROCESSED_DIR = DATA_DIR / 'processed'
US_MARKET_DIR = PROJECT_ROOT / 'us_market'

# Log directory
LOG_DIR = PROJECT_ROOT / 'logs'

# Ensure directories exist
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
US_MARKET_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Logging configuration
def setup_logging(log_file: str = 'pipeline.log', level: int = logging.INFO):
    """
    로깅 설정 초기화
    
    Args:
        log_file: 로그 파일명
        level: 로깅 레벨
    """
    log_path = LOG_DIR / log_file
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

# API Keys
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
FRED_API_KEY = os.getenv('FRED_API_KEY', '')

# Server configuration
PORT = int(os.getenv('PORT', 3000))
FLASK_ENV = os.getenv('FLASK_ENV', 'development')

# File paths
PRICES_FILE = DATA_RAW_DIR / 'us_daily_prices.csv'
STOCKS_LIST_FILE = DATA_RAW_DIR / 'us_stocks_list.csv'
VOLUME_ANALYSIS_FILE = DATA_PROCESSED_DIR / 'us_volume_analysis.csv'
HOLDINGS_FILE = DATA_PROCESSED_DIR / 'us_13f_holdings.csv'
ETF_FLOWS_FILE = DATA_PROCESSED_DIR / 'us_etf_flows.csv'
SMART_MONEY_PICKS_FILE = DATA_PROCESSED_DIR / 'smart_money_picks_v2.csv'
SECTOR_HEATMAP_FILE = DATA_PROCESSED_DIR / 'sector_heatmap.json'
OPTIONS_FLOW_FILE = DATA_PROCESSED_DIR / 'options_flow.json'
INSIDER_MOVES_FILE = DATA_PROCESSED_DIR / 'insider_moves.json'
PORTFOLIO_RISK_FILE = DATA_PROCESSED_DIR / 'portfolio_risk.json'
MACRO_ANALYSIS_FILE = DATA_PROCESSED_DIR / 'macro_analysis.json'
MACRO_ANALYSIS_EN_FILE = DATA_PROCESSED_DIR / 'macro_analysis_en.json'
AI_SUMMARIES_FILE = DATA_PROCESSED_DIR / 'ai_summaries.json'
FINAL_REPORT_FILE = DATA_PROCESSED_DIR / 'final_top10_report.json'
SMART_MONEY_CURRENT_FILE = DATA_PROCESSED_DIR / 'smart_money_current.json'
WEEKLY_CALENDAR_FILE = DATA_PROCESSED_DIR / 'weekly_calendar.json'
ETF_FLOW_ANALYSIS_FILE = DATA_PROCESSED_DIR / 'etf_flow_analysis.json'
