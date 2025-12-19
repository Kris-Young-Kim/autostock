#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Stock Summary Generator
Generates investment summaries using Gemini AI for top Smart Money picks
"""

import json
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional
from tqdm import tqdm
import time
from urllib.parse import quote

# Import core config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import (
    setup_logging,
    SMART_MONEY_PICKS_FILE,
    AI_SUMMARIES_FILE,
    GOOGLE_API_KEY
)

# Setup logging
logger = setup_logging('pipeline.log')


class NewsCollector:
    """Collect news for individual stocks"""
    
    def get_news(self, ticker: str, max_items: int = 3) -> List[Dict]:
        """
        Get news for a ticker from Google News RSS
        
        Args:
            ticker: Stock ticker symbol
            max_items: Maximum number of news items to return
            
        Returns:
            List of news items
        """
        news = []
        try:
            # Search for ticker + stock news
            query = quote(f"{ticker} stock")
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
                            'published': pub_date_elem.text if pub_date_elem is not None else '',
                            'source': 'Google News'
                        })
        except Exception as e:
            logger.debug(f"Error fetching news for {ticker}: {e}")
        
        return news


class GeminiGenerator:
    """Generate AI summaries using Gemini"""
    
    def __init__(self):
        self.api_key = GOOGLE_API_KEY
    
    def generate(self, ticker: str, data: Dict, news: List[Dict], lang: str = 'ko') -> str:
        """
        Generate AI summary for a stock
        
        Args:
            ticker: Stock ticker symbol
            data: Stock data dictionary (from smart_money_picks_v2.csv)
            news: List of news items
            lang: Language ('ko' or 'en')
            
        Returns:
            Generated summary text
        """
        if not self.api_key:
            logger.warning("Google API key not found. Skipping AI generation.")
            return "API Key Missing"
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            prompt = self._build_prompt(ticker, data, news, lang)
            
            response = model.generate_content(prompt)
            
            # Check if content was blocked by safety filters
            if hasattr(response, 'is_blocked') and response.is_blocked:
                logger.warning(f"Content blocked by safety filters for {ticker}")
                return "Content blocked by safety filters"
            
            # Check if response has text attribute
            if not hasattr(response, 'text') or not response.text:
                # Try to get text from candidates
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                        if text_parts:
                            summary = ''.join(text_parts)
                        else:
                            logger.warning(f"No text content in response for {ticker}")
                            return "No content generated"
                    else:
                        logger.warning(f"Unexpected response structure for {ticker}")
                        return "Invalid response structure"
                else:
                    logger.warning(f"No candidates in response for {ticker}")
                    return "No response generated"
            else:
                summary = response.text
            
            return summary.strip()
            
        except ImportError:
            logger.warning("google-generativeai not installed. Install with: pip install google-generativeai")
            return "Package not installed"
        except Exception as e:
            logger.error(f"Error generating summary for {ticker}: {e}")
            return f"Analysis Failed: {str(e)}"
    
    def _build_prompt(self, ticker: str, data: Dict, news: List[Dict], lang: str) -> str:
        """Build prompt for AI generation"""
        # Extract key information
        composite_score = data.get('composite_score', 'N/A')
        grade = data.get('grade', 'N/A')
        current_price = data.get('current_price', 'N/A')
        target_upside = data.get('target_upside', 'N/A')
        
        # Build score info
        score_info = f"Composite Score: {composite_score}/100, Grade: {grade}"
        if current_price != 'N/A':
            score_info += f", Current Price: ${current_price}"
        if target_upside != 'N/A':
            score_info += f", Target Upside: {target_upside}%"
        
        # Build news text
        news_txt = "\n".join([f"- {n.get('title', '')}" for n in news]) if news else "No recent news available"
        
        if lang == 'ko':
            return f"""종목: {ticker}
정보: {score_info}
최근 뉴스:
{news_txt}

위 정보를 바탕으로 3-4문장으로 투자 의견을 요약해주세요. 다음 항목을 포함해주세요:
1. 수급/기술적 분석 요약
2. 펀더멘털/가치 평가
3. 투자 전략 및 권장사항

이모지나 과도한 수식어는 사용하지 말고, 객관적이고 실용적인 내용으로 작성해주세요."""
        else:
            return f"""Stock: {ticker}
Info: {score_info}
Recent News:
{news_txt}

Based on the above information, provide a 3-4 sentence investment summary. Include:
1. Supply/demand and technical analysis summary
2. Fundamental/value assessment
3. Investment strategy and recommendations

Be objective and practical. Avoid emojis and excessive adjectives."""


class AIStockAnalyzer:
    """Main analyzer for generating AI summaries"""
    
    def __init__(self):
        self.output_file = AI_SUMMARIES_FILE
        self.generator = GeminiGenerator()
        self.news_collector = NewsCollector()
    
    def load_smart_money_picks(self, top_n: int = 20) -> pd.DataFrame:
        """Load top N picks from smart money screener"""
        if not SMART_MONEY_PICKS_FILE.exists():
            logger.error(f"Smart Money Picks file not found: {SMART_MONEY_PICKS_FILE}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(SMART_MONEY_PICKS_FILE)
            # Sort by composite_score descending and take top N
            if 'composite_score' in df.columns:
                df = df.sort_values('composite_score', ascending=False)
            return df.head(top_n)
        except Exception as e:
            logger.error(f"Error loading smart money picks: {e}")
            return pd.DataFrame()
    
    def load_existing_summaries(self) -> Dict:
        """Load existing summaries if file exists"""
        if self.output_file.exists():
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading existing summaries: {e}")
        return {}
    
    def run(self, top_n: int = 20, skip_existing: bool = True) -> Dict:
        """
        Generate AI summaries for top picks
        
        Args:
            top_n: Number of top picks to analyze
            skip_existing: Skip tickers that already have summaries
            
        Returns:
            Dictionary of summaries
        """
        logger.info(f"🚀 Starting AI Summary Generation for top {top_n} picks...")
        
        # Load smart money picks
        df = self.load_smart_money_picks(top_n)
        
        if df.empty:
            logger.error("No smart money picks found")
            return {}
        
        logger.info(f"📊 Loaded {len(df)} picks")
        
        # Load existing summaries
        results = self.load_existing_summaries()
        
        # Process each ticker
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Generating summaries"):
            ticker = row['ticker']
            
            # Skip if already exists
            if skip_existing and ticker in results:
                logger.debug(f"⏭️  Skipping {ticker} (already exists)")
                continue
            
            logger.info(f"📊 Processing {ticker}...")
            
            # Collect news
            news = self.news_collector.get_news(ticker)
            logger.debug(f"   Collected {len(news)} news items")
            
            # Generate summaries
            summary_ko = self.generator.generate(ticker, row.to_dict(), news, 'ko')
            time.sleep(0.5)  # Rate limiting
            
            summary_en = self.generator.generate(ticker, row.to_dict(), news, 'en')
            time.sleep(0.5)  # Rate limiting
            
            # Store results
            results[ticker] = {
                'summary': summary_ko,  # Default to Korean
                'summary_ko': summary_ko,
                'summary_en': summary_en,
                'news_count': len(news),
                'updated': datetime.now().isoformat()
            }
            
            logger.info(f"   ✅ Generated summaries for {ticker}")
        
        # Save results
        if results:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Saved {len(results)} summaries to {self.output_file}")
        else:
            logger.warning("No summaries to save")
        
        return results


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Stock Summary Generator')
    parser.add_argument('--top', type=int, default=20, help='Number of top picks to analyze')
    parser.add_argument('--refresh', action='store_true', help='Refresh all summaries (ignore existing)')
    args = parser.parse_args()
    
    analyzer = AIStockAnalyzer()
    results = analyzer.run(top_n=args.top, skip_existing=not args.refresh)
    
    if results:
        print(f"\n✅ Generated {len(results)} AI summaries")
        print(f"   Saved to: {analyzer.output_file}")
        
        # Show sample
        if results:
            sample_ticker = list(results.keys())[0]
            sample = results[sample_ticker]
            print(f"\n📝 Sample summary for {sample_ticker}:")
            print(f"   {sample['summary_ko'][:200]}...")


if __name__ == "__main__":
    main()

