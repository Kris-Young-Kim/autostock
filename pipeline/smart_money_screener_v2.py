#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Smart Money Screener v2.0
Comprehensive analysis combining:
- Volume/Accumulation Analysis
- Technical Analysis (RSI, MACD, MA)
- Fundamental Analysis (P/E, P/B, Growth)
- Analyst Ratings
- Relative Strength vs S&P 500
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm
import warnings
import time

warnings.filterwarnings('ignore')

# Import core config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import (
    setup_logging,
    VOLUME_ANALYSIS_FILE,
    HOLDINGS_FILE,
    ETF_FLOWS_FILE,
    SMART_MONEY_PICKS_FILE
)

# Setup logging
logger = setup_logging('pipeline.log')


class EnhancedSmartMoneyScreener:
    """
    Enhanced screener with comprehensive analysis:
    1. Supply/Demand (volume analysis)
    2. Technical Analysis (RSI, MACD, MA)
    3. Fundamentals (valuation, growth)
    4. Analyst Ratings
    5. Relative Strength
    """
    
    def __init__(self):
        self.output_file = SMART_MONEY_PICKS_FILE
        
        # Load analysis data
        self.volume_df = None
        self.holdings_df = None
        self.etf_df = None
        
        # S&P 500 benchmark data
        self.spy_data = None
        
    def load_data(self) -> bool:
        """Load all analysis results"""
        try:
            # Volume Analysis
            if VOLUME_ANALYSIS_FILE.exists():
                self.volume_df = pd.read_csv(VOLUME_ANALYSIS_FILE)
                logger.info(f"✅ Loaded volume analysis: {len(self.volume_df)} stocks")
            else:
                logger.warning("⚠️ Volume analysis not found")
                return False
            
            # 13F Holdings
            if HOLDINGS_FILE.exists():
                self.holdings_df = pd.read_csv(HOLDINGS_FILE)
                logger.info(f"✅ Loaded 13F holdings: {len(self.holdings_df)} stocks")
            else:
                logger.warning("⚠️ 13F holdings not found")
                return False
            
            # ETF Flows (optional)
            if ETF_FLOWS_FILE.exists():
                self.etf_df = pd.read_csv(ETF_FLOWS_FILE)
            
            # Load SPY for relative strength
            logger.info("📈 Loading SPY benchmark data...")
            spy = yf.Ticker("SPY")
            self.spy_data = spy.history(period="3mo")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def get_technical_analysis(self, ticker: str) -> Dict:
        """Calculate technical indicators"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")
            
            if len(hist) < 50:
                return self._default_technical()
            
            close = hist['Close']
            
            # RSI (14-day)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss.replace(0, 0.0001)
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            
            # MACD
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9, adjust=False).mean()
            macd_histogram = macd - signal
            
            macd_current = macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0
            signal_current = signal.iloc[-1] if not pd.isna(signal.iloc[-1]) else 0
            macd_hist_current = macd_histogram.iloc[-1] if not pd.isna(macd_histogram.iloc[-1]) else 0
            
            # Moving Averages
            ma20 = close.rolling(20).mean().iloc[-1] if len(close) >= 20 else close.iloc[-1]
            ma50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else ma20
            ma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else ma50
            current_price = close.iloc[-1]
            
            # MA Arrangement
            if current_price > ma20 > ma50:
                ma_signal = "Bullish"
            elif current_price < ma20 < ma50:
                ma_signal = "Bearish"
            else:
                ma_signal = "Neutral"
            
            # Golden/Death Cross
            if len(close) >= 200:
                ma50_prev = close.rolling(50).mean().iloc[-5] if len(close) >= 55 else ma50
                ma200_prev = close.rolling(200).mean().iloc[-5] if len(close) >= 205 else ma200
            else:
                ma50_prev = ma50
                ma200_prev = ma200
            
            if ma50 > ma200 and ma50_prev <= ma200_prev:
                cross_signal = "Golden Cross"
            elif ma50 < ma200 and ma50_prev >= ma200_prev:
                cross_signal = "Death Cross"
            else:
                cross_signal = "None"
            
            # Technical Score (0-100)
            tech_score = 50
            
            # RSI contribution
            if 40 <= current_rsi <= 60:
                tech_score += 10  # Neutral zone - room to move
            elif current_rsi < 30:
                tech_score += 15  # Oversold - potential bounce
            elif current_rsi > 70:
                tech_score -= 5   # Overbought
            
            # MACD contribution
            if len(macd_histogram) >= 2:
                if macd_hist_current > 0 and macd_histogram.iloc[-2] < 0:
                    tech_score += 15  # Bullish crossover
                elif macd_hist_current > 0:
                    tech_score += 8
                elif macd_hist_current < 0:
                    tech_score -= 5
            
            # MA contribution
            if ma_signal == "Bullish":
                tech_score += 15
            elif ma_signal == "Bearish":
                tech_score -= 10
            
            if cross_signal == "Golden Cross":
                tech_score += 10
            elif cross_signal == "Death Cross":
                tech_score -= 15
            
            tech_score = max(0, min(100, tech_score))
            
            return {
                'rsi': round(current_rsi, 1),
                'macd': round(macd_current, 3),
                'macd_signal': round(signal_current, 3),
                'macd_histogram': round(macd_hist_current, 3),
                'ma20': round(ma20, 2),
                'ma50': round(ma50, 2),
                'ma200': round(ma200, 2),
                'ma_signal': ma_signal,
                'cross_signal': cross_signal,
                'technical_score': tech_score
            }
            
        except Exception as e:
            logger.debug(f"Error in technical analysis for {ticker}: {e}")
            return self._default_technical()
    
    def _default_technical(self) -> Dict:
        return {
            'rsi': 50, 'macd': 0, 'macd_signal': 0, 'macd_histogram': 0,
            'ma20': 0, 'ma50': 0, 'ma200': 0, 'ma_signal': 'Unknown', 'cross_signal': 'None',
            'technical_score': 50
        }
    
    def get_fundamental_analysis(self, ticker: str) -> Dict:
        """Get fundamental/valuation metrics"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Valuation
            pe_ratio = info.get('trailingPE', 0) or 0
            forward_pe = info.get('forwardPE', 0) or 0
            pb_ratio = info.get('priceToBook', 0) or 0
            
            # Growth
            revenue_growth = info.get('revenueGrowth', 0) or 0
            earnings_growth = info.get('earningsGrowth', 0) or 0
            
            # Profitability
            profit_margin = info.get('profitMargins', 0) or 0
            roe = info.get('returnOnEquity', 0) or 0
            
            # Market Cap
            market_cap = info.get('marketCap', 0) or 0
            
            # Dividend
            dividend_yield = info.get('dividendYield', 0) or 0
            
            # Fundamental Score (0-100)
            fund_score = 50
            
            # P/E contribution (lower is better, but not too low)
            if 0 < pe_ratio < 15:
                fund_score += 15
            elif 15 <= pe_ratio < 25:
                fund_score += 10
            elif pe_ratio > 40:
                fund_score -= 10
            elif pe_ratio < 0:  # Negative earnings
                fund_score -= 15
            
            # Growth contribution
            if revenue_growth > 0.2:
                fund_score += 15
            elif revenue_growth > 0.1:
                fund_score += 10
            elif revenue_growth > 0:
                fund_score += 5
            elif revenue_growth < 0:
                fund_score -= 10
            
            # ROE contribution
            if roe > 0.2:
                fund_score += 10
            elif roe > 0.1:
                fund_score += 5
            elif roe < 0:
                fund_score -= 10
            
            fund_score = max(0, min(100, fund_score))
            
            # Size category
            if market_cap > 200e9:
                size = "Mega Cap"
            elif market_cap > 10e9:
                size = "Large Cap"
            elif market_cap > 2e9:
                size = "Mid Cap"
            elif market_cap > 300e6:
                size = "Small Cap"
            else:
                size = "Micro Cap"
            
            return {
                'pe_ratio': round(pe_ratio, 2) if pe_ratio else 'N/A',
                'forward_pe': round(forward_pe, 2) if forward_pe else 'N/A',
                'pb_ratio': round(pb_ratio, 2) if pb_ratio else 'N/A',
                'revenue_growth': round(revenue_growth * 100, 1) if revenue_growth else 0,
                'earnings_growth': round(earnings_growth * 100, 1) if earnings_growth else 0,
                'profit_margin': round(profit_margin * 100, 1) if profit_margin else 0,
                'roe': round(roe * 100, 1) if roe else 0,
                'market_cap_b': round(market_cap / 1e9, 1),
                'size': size,
                'dividend_yield': round(dividend_yield * 100, 2) if dividend_yield else 0,
                'fundamental_score': fund_score
            }
            
        except Exception as e:
            logger.debug(f"Error in fundamental analysis for {ticker}: {e}")
            return self._default_fundamental()
    
    def _default_fundamental(self) -> Dict:
        return {
            'pe_ratio': 'N/A', 'forward_pe': 'N/A', 'pb_ratio': 'N/A',
            'revenue_growth': 0, 'earnings_growth': 0, 'profit_margin': 0,
            'roe': 0, 'market_cap_b': 0, 'size': 'Unknown', 'dividend_yield': 0,
            'fundamental_score': 50
        }
    
    def get_analyst_ratings(self, ticker: str) -> Dict:
        """Get analyst consensus and target price"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get company name
            company_name = info.get('longName', '') or info.get('shortName', '') or ticker
            
            current_price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0) or 0
            target_price = info.get('targetMeanPrice', 0) or 0
            
            # Recommendation
            recommendation = info.get('recommendationKey', 'none')
            num_analysts = info.get('numberOfAnalystOpinions', 0) or 0
            
            # Upside potential
            if current_price > 0 and target_price > 0:
                upside = ((target_price / current_price) - 1) * 100
            else:
                upside = 0
            
            # Analyst Score (0-100)
            analyst_score = 50
            
            # Recommendation contribution
            rec_map = {
                'strongBuy': 25, 'buy': 20, 'hold': 0,
                'sell': -15, 'strongSell': -25
            }
            analyst_score += rec_map.get(recommendation, 0)
            
            # Upside contribution
            if upside > 30:
                analyst_score += 20
            elif upside > 20:
                analyst_score += 15
            elif upside > 10:
                analyst_score += 10
            elif upside > 0:
                analyst_score += 5
            elif upside < -10:
                analyst_score -= 15
            
            analyst_score = max(0, min(100, analyst_score))
            
            return {
                'company_name': company_name,
                'current_price': round(current_price, 2),
                'target_price': round(target_price, 2) if target_price else 'N/A',
                'upside_pct': round(upside, 1),
                'recommendation': recommendation,
                'num_analysts': num_analysts,
                'analyst_score': analyst_score
            }
            
        except Exception as e:
            logger.debug(f"Error in analyst ratings for {ticker}: {e}")
            return self._default_analyst()
            
    def _default_analyst(self) -> Dict:
        return {
            'company_name': '', 'current_price': 0, 'target_price': 'N/A',
            'upside_pct': 0, 'recommendation': 'none', 'num_analysts': 0,
            'analyst_score': 50
        }
    
    def get_relative_strength(self, ticker: str) -> Dict:
        """Calculate relative strength vs S&P 500"""
        try:
            if self.spy_data is None or len(self.spy_data) < 20:
                return {'rs_20d': 0, 'rs_60d': 0, 'rs_score': 50}
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period="3mo")
            
            if len(hist) < 20:
                return {'rs_20d': 0, 'rs_60d': 0, 'rs_score': 50}
            
            # Sort by index (date)
            hist = hist.sort_index()
            spy_sorted = self.spy_data.sort_index()
            
            # Calculate returns
            stock_return_20d = (hist['Close'].iloc[-1] / hist['Close'].iloc[-21] - 1) * 100 if len(hist) >= 21 else 0
            stock_return_60d = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
            
            spy_return_20d = (spy_sorted['Close'].iloc[-1] / spy_sorted['Close'].iloc[-21] - 1) * 100 if len(spy_sorted) >= 21 else 0
            spy_return_60d = (spy_sorted['Close'].iloc[-1] / spy_sorted['Close'].iloc[0] - 1) * 100
            
            rs_20d = stock_return_20d - spy_return_20d
            rs_60d = stock_return_60d - spy_return_60d
            
            # RS Score (0-100)
            rs_score = 50
            if rs_20d > 10:
                rs_score += 25
            elif rs_20d > 5:
                rs_score += 15
            elif rs_20d > 0:
                rs_score += 8
            elif rs_20d < -10:
                rs_score -= 20
            elif rs_20d < -5:
                rs_score -= 10
            
            if rs_60d > 15:
                rs_score += 15
            elif rs_60d > 5:
                rs_score += 8
            elif rs_60d < -15:
                rs_score -= 15
            
            rs_score = max(0, min(100, rs_score))
            
            return {
                'rs_20d': round(rs_20d, 1),
                'rs_60d': round(rs_60d, 1),
                'rs_score': rs_score
            }
            
        except Exception as e:
            logger.debug(f"Error in relative strength for {ticker}: {e}")
            return {'rs_20d': 0, 'rs_60d': 0, 'rs_score': 50}
    
    def calculate_composite_score(self, row: pd.Series, tech: Dict, fund: Dict, analyst: Dict, rs: Dict) -> Tuple[float, str]:
        """Calculate final composite score"""
        # Weighted composite
        composite = (
            row.get('supply_demand_score', 50) * 0.25 +
            row.get('institutional_score', 50) * 0.20 +
            tech.get('technical_score', 50) * 0.20 +
            fund.get('fundamental_score', 50) * 0.15 +
            analyst.get('analyst_score', 50) * 0.10 +
            rs.get('rs_score', 50) * 0.10
        )
        
        # Determine grade
        if composite >= 80:
            grade = "S급 (즉시 매수)"
        elif composite >= 70:
            grade = "A급 (적극 매수)"
        elif composite >= 60:
            grade = "B급 (매수 고려)"
        elif composite >= 50:
            grade = "C급 (관망)"
        elif composite >= 40:
            grade = "D급 (주의)"
        else:
            grade = "F급 (회피)"
        
        return round(composite, 1), grade
    
    def run_screening(self, top_n: int = 50) -> pd.DataFrame:
        """Run enhanced screening"""
        logger.info("🔍 Running Enhanced Smart Money Screening...")
        
        # Merge volume and holdings data
        merged_df = pd.merge(
            self.volume_df,
            self.holdings_df,
            on='ticker',
            how='inner',
            suffixes=('_vol', '_inst')
        )
        
        # Pre-filter: Focus on accumulation candidates
        filtered = merged_df[merged_df['supply_demand_score'] >= 50]
        
        logger.info(f"📊 Pre-filtered to {len(filtered)} candidates")
        
        results = []
        
        for idx, row in tqdm(filtered.iterrows(), total=len(filtered), desc="Enhanced Screening"):
            ticker = row['ticker']
            
            # Get all analyses
            tech = self.get_technical_analysis(ticker)
            fund = self.get_fundamental_analysis(ticker)
            analyst = self.get_analyst_ratings(ticker)
            rs = self.get_relative_strength(ticker)
            
            # Calculate composite score
            composite_score, grade = self.calculate_composite_score(row, tech, fund, analyst, rs)
            
            result = {
                'ticker': ticker,
                'name': analyst.get('company_name', row.get('name', ticker)),
                'composite_score': composite_score,
                'grade': grade,
                'sd_score': row.get('supply_demand_score', 50),
                'inst_score': row.get('institutional_score', 50),
                'tech_score': tech['technical_score'],
                'fund_score': fund['fundamental_score'],
                'analyst_score': analyst['analyst_score'],
                'rs_score': rs['rs_score'],
                'current_price': analyst['current_price'],
                'target_price': analyst['target_price'],
                'target_upside': analyst['upside_pct'],
                'recommendation': analyst['recommendation'],
                'rsi': tech['rsi'],
                'macd_histogram': tech['macd_histogram'],
                'ma_signal': tech['ma_signal'],
                'cross_signal': tech['cross_signal'],
                'pe_ratio': fund['pe_ratio'],
                'revenue_growth': fund['revenue_growth'],
                'roe': fund['roe'],
                'size': fund['size'],
                'rs_20d': rs['rs_20d'],
                'rs_60d': rs['rs_60d']
            }
            results.append(result)
            
            # Rate limiting
            time.sleep(0.1)
        
        # Create DataFrame and sort
        results_df = pd.DataFrame(results)
        if not results_df.empty:
            results_df = results_df.sort_values('composite_score', ascending=False)
            results_df['rank'] = range(1, len(results_df) + 1)
        
        return results_df
    
    def run(self, top_n: int = 50) -> pd.DataFrame:
        """Main execution"""
        logger.info("🚀 Starting Enhanced Smart Money Screener v2.0...")
        
        if not self.load_data():
            logger.error("❌ Failed to load data")
            return pd.DataFrame()
        
        results_df = self.run_screening(top_n)
        
        # Save results
        if not results_df.empty:
            results_df.to_csv(self.output_file, index=False)
            logger.info(f"✅ Saved to {self.output_file}")
            logger.info(f"📊 Total stocks analyzed: {len(results_df)}")
            
            # Print summary by grade
            if 'grade' in results_df.columns:
                grade_counts = results_df['grade'].value_counts()
                logger.info("\n📊 Summary by Grade:")
                for grade, count in grade_counts.items():
                    logger.info(f"   {grade}: {count} stocks")
        else:
            logger.warning("No results to save")
        
        return results_df


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Smart Money Screener v2.0')
    parser.add_argument('--top', type=int, default=20, help='Number of top picks to display')
    args = parser.parse_args()
    
    screener = EnhancedSmartMoneyScreener()
    results = screener.run(top_n=args.top)
    
    if not results.empty:
        print(f"\n🔥 TOP {args.top} ENHANCED SMART MONEY PICKS")
        display_cols = ['rank', 'ticker', 'name', 'grade', 'composite_score', 'current_price', 'target_upside']
        available_cols = [col for col in display_cols if col in results.columns]
        print(results[available_cols].head(args.top).to_string(index=False))


if __name__ == "__main__":
    main()
