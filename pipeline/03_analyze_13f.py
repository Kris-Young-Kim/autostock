#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
US 13F Institutional Holdings Analysis
Fetches and analyzes institutional holdings using yfinance
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from typing import Dict, List, Optional
import time

# Import core config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import (
    setup_logging,
    STOCKS_LIST_FILE,
    HOLDINGS_FILE
)

from tqdm import tqdm

# Setup logging
logger = setup_logging('pipeline.log')


class SEC13FAnalyzer:
    """
    Analyze institutional holdings from yfinance
    Note: Uses yfinance as primary data source for institutional data
    """
    
    def __init__(self):
        self.output_file = HOLDINGS_FILE
        
    def analyze_institutional_changes(self, tickers: List[str]) -> pd.DataFrame:
        """
        Analyze institutional ownership and recent changes
        Uses yfinance as primary data source
        """
        results = []
        
        for ticker in tqdm(tickers, desc="Fetching institutional data"):
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Basic ownership info
                inst_pct = info.get('heldPercentInstitutions', 0) or 0
                insider_pct = info.get('heldPercentInsiders', 0) or 0
                
                # Float and shares
                float_shares = info.get('floatShares', 0) or 0
                shares_outstanding = info.get('sharesOutstanding', 0) or 0
                short_pct = info.get('shortPercentOfFloat', 0) or 0
                
                # Insider transactions
                try:
                    insider_txns = stock.insider_transactions
                    if insider_txns is not None and len(insider_txns) > 0:
                        recent = insider_txns.head(10)
                        # Handle different column names
                        transaction_col = None
                        for col in recent.columns:
                            if 'transaction' in col.lower() or 'type' in col.lower():
                                transaction_col = col
                                break
                        
                        if transaction_col:
                            buys = len(recent[recent[transaction_col].str.contains('Buy|Purchase', case=False, na=False)])
                            sells = len(recent[recent[transaction_col].str.contains('Sale|Sell', case=False, na=False)])
                        else:
                            # Fallback: check all string columns
                            buys = 0
                            sells = 0
                            for col in recent.select_dtypes(include=['object']).columns:
                                buys += recent[col].str.contains('Buy|Purchase', case=False, na=False).sum()
                                sells += recent[col].str.contains('Sale|Sell', case=False, na=False).sum()
                        
                        insider_sentiment = 'Buying' if buys > sells else ('Selling' if sells > buys else 'Neutral')
                    else:
                        insider_sentiment = 'Unknown'
                        buys = 0
                        sells = 0
                except Exception as e:
                    logger.debug(f"Error fetching insider transactions for {ticker}: {e}")
                    insider_sentiment = 'Unknown'
                    buys = 0
                    sells = 0
                
                # Institutional holders count
                try:
                    inst_holders = stock.institutional_holders
                    num_inst_holders = len(inst_holders) if inst_holders is not None and not inst_holders.empty else 0
                except Exception as e:
                    logger.debug(f"Error fetching institutional holders for {ticker}: {e}")
                    num_inst_holders = 0
                
                # Score calculation (0-100)
                score = 50
                
                # High institutional ownership is generally positive
                if inst_pct > 0.8:
                    score += 15
                elif inst_pct > 0.6:
                    score += 10
                elif inst_pct < 0.3:
                    score -= 10
                
                # Insider activity
                if buys > sells:
                    score += 15
                elif sells > buys:
                    score -= 10
                
                # Low short interest is positive
                if short_pct < 0.03:
                    score += 5
                elif short_pct > 0.1:
                    score -= 10
                elif short_pct > 0.2:
                    score -= 20
                
                score = max(0, min(100, score))
                
                # Determine stage
                if score >= 70:
                    stage = "Strong Institutional Support"
                elif score >= 55:
                    stage = "Institutional Support"
                elif score >= 45:
                    stage = "Neutral"
                elif score >= 30:
                    stage = "Institutional Concern"
                else:
                    stage = "Strong Institutional Selling"
                
                results.append({
                    'ticker': ticker,
                    'institutional_pct': round(inst_pct * 100, 2) if inst_pct else 0,
                    'insider_pct': round(insider_pct * 100, 2) if insider_pct else 0,
                    'short_pct': round(short_pct * 100, 2) if short_pct else 0,
                    'float_shares_m': round(float_shares / 1e6, 2) if float_shares else 0,
                    'num_inst_holders': num_inst_holders,
                    'insider_buys': buys,
                    'insider_sells': sells,
                    'insider_sentiment': insider_sentiment,
                    'institutional_score': score,
                    'institutional_stage': stage
                })
                
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logger.debug(f"Error analyzing {ticker}: {e}")
                continue
        
        return pd.DataFrame(results)
    
    def run(self) -> pd.DataFrame:
        """Run institutional analysis for stocks in the data directory"""
        logger.info("🚀 Starting 13F Institutional Analysis...")
        
        # Load stock list
        if STOCKS_LIST_FILE.exists():
            stocks_df = pd.read_csv(STOCKS_LIST_FILE)
            tickers = stocks_df['ticker'].tolist()
        else:
            logger.warning("Stock list not found. Using top 50 S&P 500 stocks.")
            tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
                      'UNH', 'JNJ', 'JPM', 'V', 'XOM', 'PG', 'MA', 'HD', 'CVX', 'MRK',
                      'ABBV', 'LLY', 'PEP', 'KO', 'COST', 'AVGO', 'WMT', 'MCD', 'TMO',
                      'CSCO', 'ABT', 'CRM', 'ACN', 'DHR', 'ORCL', 'NKE', 'TXN', 'PM',
                      'NEE', 'INTC', 'AMD', 'QCOM', 'IBM', 'GS', 'CAT', 'BA', 'DIS',
                      'NFLX', 'PYPL', 'ADBE', 'NOW', 'INTU']
        
        logger.info(f"📊 Analyzing {len(tickers)} stocks")
        
        # Run analysis
        results_df = self.analyze_institutional_changes(tickers)
        
        # Save results
        if not results_df.empty:
            results_df.to_csv(self.output_file, index=False)
            logger.info(f"✅ Analysis complete! Saved to {self.output_file}")
            
            # Summary
            logger.info("\n📊 Summary:")
            if 'institutional_stage' in results_df.columns:
                stage_counts = results_df['institutional_stage'].value_counts()
                for stage, count in stage_counts.items():
                    logger.info(f"   {stage}: {count} stocks")
        else:
            logger.warning("No results to save")
        
        return results_df


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='13F Institutional Analysis')
    parser.add_argument('--tickers', nargs='+', help='Specific tickers to analyze')
    args = parser.parse_args()
    
    analyzer = SEC13FAnalyzer()
    
    if args.tickers:
        results = analyzer.analyze_institutional_changes(args.tickers)
        if not results.empty:
            results.to_csv(HOLDINGS_FILE, index=False)
            logger.info(f"✅ Saved to {HOLDINGS_FILE}")
    else:
        results = analyzer.run()
    
    if not results.empty:
        # Show top institutional support
        print("\n🏦 Top 10 Institutional Support:")
        top_10 = results.nlargest(10, 'institutional_score')
        for _, row in top_10.iterrows():
            print(f"   {row['ticker']}: Score {row['institutional_score']} | "
                  f"Inst: {row['institutional_pct']:.1f}% | "
                  f"Insider: {row['insider_sentiment']}")
        
        # Show stocks with insider buying
        buying = results[results['insider_sentiment'] == 'Buying']
        if not buying.empty:
            print("\n📈 Insider Buying Activity:")
            for _, row in buying.head(10).iterrows():
                print(f"   {row['ticker']}: {row['insider_buys']} buys vs {row['insider_sells']} sells")


if __name__ == "__main__":
    main()
