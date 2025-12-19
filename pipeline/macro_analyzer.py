#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Macro Market Analyzer
Collects macro indicators and uses Gemini AI to generate investment strategy
"""

import json
import requests
import pandas as pd
import yfinance as yf
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional
import time

# Import core config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import (
    setup_logging,
    MACRO_ANALYSIS_FILE,
    MACRO_ANALYSIS_EN_FILE,
    GOOGLE_API_KEY
)

# Setup logging
logger = setup_logging('pipeline.log')


class MacroDataCollector:
    """Collect macro market data from various sources"""
    
    def __init__(self):
        self.macro_tickers = {
            'VIX': '^VIX',
            'DXY': 'DX-Y.NYB',
            '2Y_Yield': '^IRX',
            '10Y_Yield': '^TNX',
            'GOLD': 'GC=F',
            'OIL': 'CL=F',
            'BTC': 'BTC-USD',
            'SPY': 'SPY',
            'QQQ': 'QQQ'
        }
    
    def get_current_macro_data(self) -> Dict:
        """Fetch current macro market data"""
        logger.info("📊 Fetching macro data...")
        macro_data = {}
        
        try:
            tickers = list(self.macro_tickers.values())
            data = yf.download(tickers, period='5d', progress=False)
            
            if data.empty:
                logger.warning("No macro data available")
                return macro_data
            
            # Handle MultiIndex columns
            if isinstance(data.columns, pd.MultiIndex):
                close_data = data['Close']
            else:
                # Single ticker or different structure
                if len(tickers) == 1:
                    close_data = pd.DataFrame({tickers[0]: data['Close']})
                else:
                    close_data = data
            
            for name, ticker in self.macro_tickers.items():
                try:
                    if ticker not in close_data.columns:
                        continue
                    
                    hist = close_data[ticker].dropna()
                    if len(hist) < 2:
                        continue
                    
                    val = hist.iloc[-1]
                    prev = hist.iloc[-2]
                    change = ((val / prev) - 1) * 100 if prev > 0 else 0
                    
                    # 52-week High/Low
                    try:
                        full_hist = yf.Ticker(ticker).history(period='1y')
                        if not full_hist.empty:
                            high = full_hist['High'].max()
                            low = full_hist['Low'].min()
                            pct_high = ((val / high) - 1) * 100 if high > 0 else 0
                            pct_low = ((val / low) - 1) * 100 if low > 0 else 0
                        else:
                            pct_high = 0
                            pct_low = 0
                    except:
                        pct_high = 0
                        pct_low = 0
                    
                    macro_data[name] = {
                        'value': round(float(val), 2),
                        'change_1d': round(change, 2),
                        'pct_from_high': round(pct_high, 1),
                        'pct_from_low': round(pct_low, 1)
                    }
                except Exception as e:
                    logger.debug(f"Error processing {name} ({ticker}): {e}")
                    continue
            
            # Yield Spread calculation
            if '2Y_Yield' in macro_data and '10Y_Yield' in macro_data:
                spread = macro_data['10Y_Yield']['value'] - macro_data['2Y_Yield']['value']
                macro_data['YieldSpread'] = {
                    'value': round(spread, 2),
                    'change_1d': 0,
                    'pct_from_high': 0,
                    'pct_from_low': 0
                }
                
                # Inversion warning
                if spread < 0:
                    macro_data['YieldSpread']['inverted'] = True
                    macro_data['YieldSpread']['warning'] = 'Yield curve inverted - recession signal'
                else:
                    macro_data['YieldSpread']['inverted'] = False
            
            # Fear & Greed Index (placeholder - can be replaced with actual API)
            macro_data['FearGreed'] = {
                'value': 65,
                'change_1d': 0,
                'pct_from_high': 0,
                'pct_from_low': 0,
                'note': 'Placeholder value'
            }
            
            logger.info(f"✅ Collected {len(macro_data)} macro indicators")
            
        except Exception as e:
            logger.error(f"Error fetching macro data: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return macro_data
    
    def get_macro_news(self, max_items: int = 5) -> List[Dict]:
        """Fetch macro news from Google RSS"""
        news = []
        try:
            from urllib.parse import quote
            
            # Search for Federal Reserve and Economy news
            query = quote("Federal Reserve Economy US Market")
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall('.//item')[:max_items]:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pub_date_elem = item.find('pubDate')
                    
                    if title_elem is not None:
                        news.append({
                            'title': title_elem.text or '',
                            'link': link_elem.text if link_elem is not None else '',
                            'pub_date': pub_date_elem.text if pub_date_elem is not None else '',
                            'source': 'Google News'
                        })
            
            logger.info(f"✅ Collected {len(news)} news items")
            
        except Exception as e:
            logger.debug(f"Error fetching news: {e}")
        
        return news
    
    def get_historical_patterns(self) -> List[Dict]:
        """Get historical market patterns for context"""
        return [
            {
                'event': 'Fed Pivot Signal (2023)',
                'conditions': 'VIX declining, Yields peaking',
                'outcome': {'SPY_3m': '+15%', 'best_sectors': ['Tech', 'Comm']}
            },
            {
                'event': 'Yield Curve Inversion',
                'conditions': '2Y > 10Y Yield',
                'outcome': {'warning': 'Recession signal typically 12-18 months ahead'}
            }
        ]


class MacroAIAnalyzer:
    """Gemini AI Analysis for macro market"""
    
    def __init__(self):
        self.api_key = GOOGLE_API_KEY
    
    def analyze(self, data: Dict, news: List[Dict], patterns: List[Dict], lang: str = 'ko') -> str:
        """Generate AI analysis using Gemini"""
        if not self.api_key:
            logger.warning("Google API key not found. Skipping AI analysis.")
            return "API Key Missing"
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            prompt = self._build_prompt(data, news, patterns, lang)
            
            response = model.generate_content(prompt)
            analysis = response.text
            
            return analysis
            
        except ImportError:
            logger.warning("google-generativeai not installed. Install with: pip install google-generativeai")
            return "Package not installed"
        except Exception as e:
            logger.error(f"Error generating AI analysis: {e}")
            return f"Error: {str(e)}"
    
    def _build_prompt(self, data: Dict, news: List[Dict], patterns: List[Dict], lang: str) -> str:
        """Build prompt for AI analysis"""
        # Format metrics
        metrics_lines = []
        for k, v in data.items():
            if isinstance(v, dict) and 'value' in v:
                metrics_lines.append(f"- {k}: {v['value']} (change: {v.get('change_1d', 0):+.2f}%)")
        
        metrics = "\n".join(metrics_lines)
        
        # Format news headlines
        headlines = "\n".join([f"- {n.get('title', '')}" for n in news[:5]])
        
        # Format patterns
        pattern_text = "\n".join([
            f"- {p.get('event', '')}: {p.get('conditions', '')}"
            for p in patterns
        ])
        
        if lang == 'en':
            return f"""Analyze current macro market conditions and provide investment strategy recommendations.

Current Macro Indicators:
{metrics}

Recent News Headlines:
{headlines}

Historical Patterns:
{pattern_text}

Please provide:
1. Market Summary (current conditions)
2. Key Opportunities (sectors/assets to focus on)
3. Major Risks (what to watch out for)
4. Specific Investment Strategy (actionable recommendations)

Be concise and data-driven. Focus on actionable insights."""
        else:
            return f"""현재 거시경제 시장 상황을 분석하고 투자 전략을 제안해주세요.

현재 거시 지표:
{metrics}

최근 뉴스 헤드라인:
{headlines}

역사적 패턴:
{pattern_text}

다음 항목을 포함해주세요:
1. 시장 요약 (현재 상황)
2. 주요 기회 (집중해야 할 섹터/자산)
3. 주요 리스크 (주의해야 할 사항)
4. 구체적 투자 전략 (실행 가능한 권장사항)

간결하고 데이터 기반으로 작성해주세요. 실행 가능한 인사이트에 집중해주세요."""


class MultiModelAnalyzer:
    """Multi-model macro analyzer"""
    
    def __init__(self):
        self.collector = MacroDataCollector()
        self.gemini = MacroAIAnalyzer()
        self.output_file_ko = MACRO_ANALYSIS_FILE
        self.output_file_en = MACRO_ANALYSIS_EN_FILE
    
    def run(self) -> Dict:
        """Main execution"""
        logger.info("🚀 Starting Macro Market Analysis...")
        
        # Collect data
        data = self.collector.get_current_macro_data()
        news = self.collector.get_macro_news()
        patterns = self.collector.get_historical_patterns()
        
        if not data:
            logger.error("No macro data collected")
            return {}
        
        # Generate AI analysis
        logger.info("🤖 Generating AI analysis (Korean)...")
        analysis_ko = self.gemini.analyze(data, news, patterns, 'ko')
        
        logger.info("🤖 Generating AI analysis (English)...")
        analysis_en = self.gemini.analyze(data, news, patterns, 'en')
        
        # Prepare output data
        output_ko = {
            'timestamp': datetime.now().isoformat(),
            'macro_data': data,
            'news': news,
            'historical_patterns': patterns,
            'ai_analysis': analysis_ko,
            'language': 'ko'
        }
        
        output_en = {
            'timestamp': datetime.now().isoformat(),
            'macro_data': data,
            'news': news,
            'historical_patterns': patterns,
            'ai_analysis': analysis_en,
            'language': 'en'
        }
        
        # Save Korean analysis
        with open(self.output_file_ko, 'w', encoding='utf-8') as f:
            json.dump(output_ko, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Saved Korean analysis to {self.output_file_ko}")
        
        # Save English analysis
        with open(self.output_file_en, 'w', encoding='utf-8') as f:
            json.dump(output_en, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Saved English analysis to {self.output_file_en}")
        
        return output_ko


def main():
    """Main execution"""
    analyzer = MultiModelAnalyzer()
    results = analyzer.run()
    
    if results:
        print("\n📊 Macro Market Analysis Complete")
        print(f"   Indicators collected: {len(results.get('macro_data', {}))}")
        print(f"   News items: {len(results.get('news', []))}")
        if results.get('ai_analysis'):
            print(f"   AI Analysis: Generated ({len(results['ai_analysis'])} chars)")


if __name__ == "__main__":
    main()

