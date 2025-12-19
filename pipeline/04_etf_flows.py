#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETF Fund Flow Analysis
Analyzes fund flows for major ETFs using OBV and Volume Ratio
"""

import pandas as pd
import numpy as np
import yfinance as yf
import json
from datetime import datetime
from typing import Dict, List, Optional
from tqdm import tqdm
import time

# Import core config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import (
    setup_logging,
    ETF_FLOWS_FILE,
    ETF_FLOW_ANALYSIS_FILE,
    GOOGLE_API_KEY
)

# Setup logging
logger = setup_logging('pipeline.log')


class ETFFlowAnalyzer:
    """ETF Fund Flow Analyzer using OBV and Volume Ratio"""
    
    def __init__(self):
        self.output_file = ETF_FLOWS_FILE
        self.ai_output_file = ETF_FLOW_ANALYSIS_FILE
        
        # 24 Major ETFs to track
        self.etf_list = {
            # Broad Market
            'SPY': {'name': 'SPDR S&P 500', 'category': 'Broad Market'},
            'QQQ': {'name': 'Invesco QQQ Trust', 'category': 'Broad Market'},
            'IWM': {'name': 'iShares Russell 2000', 'category': 'Broad Market'},
            'DIA': {'name': 'SPDR Dow Jones', 'category': 'Broad Market'},
            'VTI': {'name': 'Vanguard Total Stock Market', 'category': 'Broad Market'},
            
            # Sector ETFs
            'XLK': {'name': 'Technology Select Sector', 'category': 'Sector'},
            'XLF': {'name': 'Financial Select Sector', 'category': 'Sector'},
            'XLV': {'name': 'Health Care Select Sector', 'category': 'Sector'},
            'XLE': {'name': 'Energy Select Sector', 'category': 'Sector'},
            'XLY': {'name': 'Consumer Discretionary', 'category': 'Sector'},
            'XLP': {'name': 'Consumer Staples', 'category': 'Sector'},
            'XLI': {'name': 'Industrials Select Sector', 'category': 'Sector'},
            'XLB': {'name': 'Materials Select Sector', 'category': 'Sector'},
            'XLU': {'name': 'Utilities Select Sector', 'category': 'Sector'},
            'XLRE': {'name': 'Real Estate Select Sector', 'category': 'Sector'},
            'XLC': {'name': 'Communication Services', 'category': 'Sector'},
            
            # Commodities & Alternatives
            'GLD': {'name': 'SPDR Gold Trust', 'category': 'Commodity'},
            'SLV': {'name': 'iShares Silver Trust', 'category': 'Commodity'},
            'USO': {'name': 'United States Oil Fund', 'category': 'Commodity'},
            'TLT': {'name': 'iShares 20+ Year Treasury', 'category': 'Fixed Income'},
            'HYG': {'name': 'iShares High Yield Corporate Bond', 'category': 'Fixed Income'},
            'EFA': {'name': 'iShares MSCI EAFE', 'category': 'International'},
            'EEM': {'name': 'iShares MSCI Emerging Markets', 'category': 'International'},
            'VEA': {'name': 'Vanguard FTSE Developed Markets', 'category': 'International'},
        }
    
    def calculate_obv(self, df: pd.DataFrame) -> pd.Series:
        """Calculate On-Balance Volume"""
        obv = [0]
        for i in range(1, len(df)):
            if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
                obv.append(obv[-1] + df['Volume'].iloc[i])
            elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
                obv.append(obv[-1] - df['Volume'].iloc[i])
            else:
                obv.append(obv[-1])
        return pd.Series(obv, index=df.index)
    
    def calculate_flow_proxy(self, ticker: str, df: pd.DataFrame) -> Optional[Dict]:
        """
        Calculate flow proxy using OBV, Volume Ratio, and Price Momentum
        Returns flow score (0-100)
        """
        if len(df) < 30:
            return None
        
        # yfinance returns date as index, so sort by index then reset
        df = df.sort_index().reset_index(drop=True)
        
        # Calculate OBV
        obv = self.calculate_obv(df)
        
        # OBV Trend (20-day change)
        if len(obv) >= 20:
            obv_change_20d = ((obv.iloc[-1] - obv.iloc[-20]) / abs(obv.iloc[-20]) * 100) if obv.iloc[-20] != 0 else 0
        else:
            obv_change_20d = 0
        
        # Volume Ratio (5-day avg vs 20-day avg)
        if len(df) >= 20:
            vol_5d = df['Volume'].tail(5).mean()
            vol_20d = df['Volume'].tail(20).mean()
            vol_ratio = vol_5d / vol_20d if vol_20d > 0 else 1
        else:
            vol_ratio = 1
        
        # Price Momentum (20-day return)
        if len(df) >= 20:
            price_return_20d = ((df['Close'].iloc[-1] / df['Close'].iloc[-20]) - 1) * 100
        else:
            price_return_20d = 0
        
        # Flow Score calculation (0-100)
        score = 50
        
        # OBV contribution (positive OBV change = inflow)
        if obv_change_20d > 10:
            score += 20
        elif obv_change_20d > 5:
            score += 10
        elif obv_change_20d < -10:
            score -= 20
        elif obv_change_20d < -5:
            score -= 10
        
        # Volume ratio contribution (high volume = active trading)
        if vol_ratio > 1.5:
            score += 10
        elif vol_ratio > 1.2:
            score += 5
        elif vol_ratio < 0.7:
            score -= 5
        
        # Price momentum contribution (price up with volume = inflow)
        if price_return_20d > 5 and obv_change_20d > 0:
            score += 10
        elif price_return_20d < -5 and obv_change_20d < 0:
            score -= 10
        
        score = max(0, min(100, score))
        
        # Determine flow direction
        if score >= 70:
            flow_direction = "Strong Inflow"
        elif score >= 55:
            flow_direction = "Inflow"
        elif score >= 45:
            flow_direction = "Neutral"
        elif score >= 30:
            flow_direction = "Outflow"
        else:
            flow_direction = "Strong Outflow"
        
        return {
            'ticker': ticker,
            'name': self.etf_list[ticker]['name'],
            'category': self.etf_list[ticker]['category'],
            'current_price': round(df['Close'].iloc[-1], 2),
            'price_change_20d': round(price_return_20d, 2),
            'obv_change_20d': round(obv_change_20d, 2),
            'vol_ratio_5d_20d': round(vol_ratio, 2),
            'flow_score': round(score, 1),
            'flow_direction': flow_direction
        }
    
    def run(self) -> pd.DataFrame:
        """Run ETF flow analysis"""
        logger.info("🚀 Starting ETF Flow Analysis...")
        logger.info(f"📊 Analyzing {len(self.etf_list)} ETFs")
        
        results = []
        
        for ticker, info in tqdm(self.etf_list.items(), desc="Analyzing ETFs"):
            try:
                # Download ETF data
                etf = yf.Ticker(ticker)
                hist = etf.history(period='3mo')
                
                if hist.empty or len(hist) < 30:
                    logger.debug(f"⚠️ Insufficient data for {ticker}")
                    continue
                
                # Calculate flow proxy
                flow_data = self.calculate_flow_proxy(ticker, hist)
                
                if flow_data:
                    results.append(flow_data)
                
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logger.debug(f"Error analyzing {ticker}: {e}")
                continue
        
        # Create DataFrame
        results_df = pd.DataFrame(results)
        
        if results_df.empty:
            logger.warning("No results to save")
            return results_df
        
        # Save results
        results_df.to_csv(self.output_file, index=False)
        logger.info(f"✅ Analysis complete! Saved to {self.output_file}")
        
        # Print summary
        logger.info("\n📊 Summary:")
        if 'flow_direction' in results_df.columns:
            flow_counts = results_df['flow_direction'].value_counts()
            for direction, count in flow_counts.items():
                logger.info(f"   {direction}: {count} ETFs")
        
        # Generate AI analysis (optional)
        if GOOGLE_API_KEY:
            try:
                self.generate_ai_analysis(results_df)
            except Exception as e:
                logger.warning(f"AI analysis generation failed: {e}")
        
        return results_df
    
    def generate_ai_analysis(self, results_df: pd.DataFrame) -> None:
        """Generate AI analysis using Gemini"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            # Prepare summary data
            top_inflows = results_df.nlargest(5, 'flow_score')
            top_outflows = results_df.nsmallest(5, 'flow_score')
            
            summary_text = f"""
ETF 자금 흐름 분석 결과:

상위 유입 ETF (Top 5):
"""
            for _, row in top_inflows.iterrows():
                summary_text += f"- {row['ticker']} ({row['name']}): Score {row['flow_score']}, {row['flow_direction']}\n"
            
            summary_text += "\n상위 유출 ETF (Top 5):\n"
            for _, row in top_outflows.iterrows():
                summary_text += f"- {row['ticker']} ({row['name']}): Score {row['flow_score']}, {row['flow_direction']}\n"
            
            prompt = f"""
다음은 주요 ETF의 자금 흐름 분석 결과입니다. 

{summary_text}

이 데이터를 바탕으로:
1. 시장 전체적인 자금 흐름 방향 분석
2. 섹터별 로테이션 패턴 파악
3. 투자자 심리 및 시장 전망
4. 구체적인 투자 전략 제안

위 4가지 관점에서 한국어로 분석 리포트를 작성해주세요. (3-4문장으로 간결하게)
"""
            
            response = model.generate_content(prompt)
            ai_analysis = response.text
            
            # Save AI analysis
            output_data = {
                'timestamp': datetime.now().isoformat(),
                'ai_analysis': ai_analysis,
                'summary': {
                    'total_etfs': len(results_df),
                    'avg_flow_score': round(results_df['flow_score'].mean(), 1),
                    'top_inflow': top_inflows[['ticker', 'name', 'flow_score']].to_dict('records'),
                    'top_outflow': top_outflows[['ticker', 'name', 'flow_score']].to_dict('records')
                }
            }
            
            with open(self.ai_output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ AI analysis saved to {self.ai_output_file}")
            
        except ImportError:
            logger.warning("google-generativeai not installed. Skipping AI analysis.")
        except Exception as e:
            logger.warning(f"AI analysis generation failed: {e}")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ETF Flow Analysis')
    args = parser.parse_args()
    
    analyzer = ETFFlowAnalyzer()
    results = analyzer.run()
    
    if not results.empty:
        print("\n💰 Top 5 ETF Inflows:")
        top_5 = results.nlargest(5, 'flow_score')
        for _, row in top_5.iterrows():
            print(f"   {row['ticker']}: Score {row['flow_score']} - {row['flow_direction']}")
        
        print("\n💸 Top 5 ETF Outflows:")
        bottom_5 = results.nsmallest(5, 'flow_score')
        for _, row in bottom_5.iterrows():
            print(f"   {row['ticker']}: Score {row['flow_score']} - {row['flow_direction']}")


if __name__ == "__main__":
    main()

