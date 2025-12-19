#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Options Flow Analysis
Analyzes options trading volume to track large investor directional bets
"""

import json
import yfinance as yf
from datetime import datetime
from typing import Dict, List, Optional
import time
import pandas as pd
import numpy as np

# Import core config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import (
    setup_logging,
    OPTIONS_FLOW_FILE
)

# Setup logging
logger = setup_logging('pipeline.log')


class OptionsFlowAnalyzer:
    """Analyze options flow for major stocks"""
    
    def __init__(self):
        # Watchlist of major stocks and ETFs
        self.watchlist = [
            'AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 
            'SPY', 'QQQ', 'AMD', 'NFLX', 'INTC', 'PYPL', 'CRM', 'ORCL'
        ]
        self.output_file = OPTIONS_FLOW_FILE
    
    def get_options_summary(self, ticker: str) -> Dict:
        """
        Get options summary for a ticker
        
        Returns:
            Dictionary with options metrics or error
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Get available expiration dates
            exps = stock.options
            if not exps:
                return {'ticker': ticker, 'error': 'No options available'}
            
            # Use nearest expiration date
            nearest_exp = exps[0]
            
            # Get option chain
            opt_chain = stock.option_chain(nearest_exp)
            calls = opt_chain.calls
            puts = opt_chain.puts
            
            # Calculate volume metrics
            call_vol = calls['volume'].sum() if 'volume' in calls.columns else 0
            put_vol = puts['volume'].sum() if 'volume' in puts.columns else 0
            
            # Calculate open interest
            call_oi = calls['openInterest'].sum() if 'openInterest' in calls.columns else 0
            put_oi = puts['openInterest'].sum() if 'openInterest' in puts.columns else 0
            
            # Put/Call Ratio
            pc_ratio = put_vol / call_vol if call_vol > 0 else 0
            
            # Put/Call Ratio by Open Interest
            pc_oi_ratio = put_oi / call_oi if call_oi > 0 else 0
            
            # Unusual activity detection
            unusual_calls = 0
            unusual_puts = 0
            
            if 'volume' in calls.columns and len(calls) > 0:
                avg_call_vol = calls['volume'].mean()
                if avg_call_vol > 0:
                    unusual_calls = len(calls[calls['volume'] > avg_call_vol * 3])
            
            if 'volume' in puts.columns and len(puts) > 0:
                avg_put_vol = puts['volume'].mean()
                if avg_put_vol > 0:
                    unusual_puts = len(puts[puts['volume'] > avg_put_vol * 3])
            
            # Calculate total volume and OI
            total_vol = call_vol + put_vol
            total_oi = call_oi + put_oi
            
            # Sentiment analysis
            # High PC ratio (> 1.0) suggests bearish sentiment
            # Low PC ratio (< 0.7) suggests bullish sentiment
            if pc_ratio > 1.2:
                sentiment = 'Bearish'
            elif pc_ratio > 0.8:
                sentiment = 'Neutral-Bearish'
            elif pc_ratio < 0.6:
                sentiment = 'Bullish'
            elif pc_ratio < 0.8:
                sentiment = 'Neutral-Bullish'
            else:
                sentiment = 'Neutral'
            
            return {
                'ticker': ticker,
                'expiration': nearest_exp,
                'metrics': {
                    'pc_ratio': round(pc_ratio, 3),
                    'pc_oi_ratio': round(pc_oi_ratio, 3),
                    'call_vol': int(call_vol),
                    'put_vol': int(put_vol),
                    'call_oi': int(call_oi),
                    'put_oi': int(put_oi),
                    'total_vol': int(total_vol),
                    'total_oi': int(total_oi)
                },
                'unusual': {
                    'calls': int(unusual_calls),
                    'puts': int(unusual_puts),
                    'total': int(unusual_calls + unusual_puts)
                },
                'sentiment': sentiment
            }
            
        except Exception as e:
            logger.debug(f"Error analyzing options for {ticker}: {e}")
            return {'ticker': ticker, 'error': str(e)}
    
    def analyze_watchlist(self) -> List[Dict]:
        """Analyze options flow for all tickers in watchlist"""
        logger.info(f"🚀 Starting Options Flow Analysis for {len(self.watchlist)} tickers...")
        
        results = []
        
        for ticker in self.watchlist:
            logger.info(f"📊 Analyzing {ticker}...")
            result = self.get_options_summary(ticker)
            
            if 'error' not in result:
                results.append(result)
                logger.info(f"   ✅ {ticker}: PC Ratio {result['metrics']['pc_ratio']:.2f}, Sentiment: {result['sentiment']}")
            else:
                logger.warning(f"   ⚠️ {ticker}: {result.get('error', 'Unknown error')}")
            
            # Rate limiting
            time.sleep(0.2)
        
        return results
    
    def save_results(self, results: List[Dict]) -> None:
        """Save analysis results to JSON file"""
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'total_tickers': len(results),
            'options_flow': results
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Saved to {self.output_file}")
        
        # Print summary
        if results:
            logger.info("\n📊 Options Flow Summary:")
            bullish = sum(1 for r in results if r.get('sentiment') == 'Bullish')
            bearish = sum(1 for r in results if r.get('sentiment') == 'Bearish')
            neutral = len(results) - bullish - bearish
            
            logger.info(f"   Bullish: {bullish}")
            logger.info(f"   Bearish: {bearish}")
            logger.info(f"   Neutral: {neutral}")
            
            # Top unusual activity
            unusual_sorted = sorted(
                [r for r in results if r.get('unusual', {}).get('total', 0) > 0],
                key=lambda x: x.get('unusual', {}).get('total', 0),
                reverse=True
            )
            
            if unusual_sorted:
                logger.info("\n🔥 Top Unusual Activity:")
                for r in unusual_sorted[:5]:
                    logger.info(f"   {r['ticker']}: {r['unusual']['total']} unusual contracts")
    
    def run(self) -> List[Dict]:
        """Main execution"""
        results = self.analyze_watchlist()
        
        if results:
            self.save_results(results)
        else:
            logger.warning("No results to save")
        
        return results


def main():
    """Main execution"""
    analyzer = OptionsFlowAnalyzer()
    results = analyzer.run()
    
    if results:
        print("\n📊 Options Flow Analysis Complete")
        print(f"   Analyzed {len(results)} tickers")
        
        # Show top PC ratios
        sorted_by_pc = sorted(
            results,
            key=lambda x: x['metrics']['pc_ratio'],
            reverse=True
        )
        
        print("\n🔴 Highest Put/Call Ratios (Bearish):")
        for r in sorted_by_pc[:5]:
            print(f"   {r['ticker']}: {r['metrics']['pc_ratio']:.2f} ({r['sentiment']})")
        
        print("\n🟢 Lowest Put/Call Ratios (Bullish):")
        for r in sorted_by_pc[-5:]:
            print(f"   {r['ticker']}: {r['metrics']['pc_ratio']:.2f} ({r['sentiment']})")


if __name__ == "__main__":
    main()

