#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Insider Trading Tracker
Tracks insider transactions from SEC EDGAR via yfinance
"""

import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Import core config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import (
    setup_logging,
    INSIDER_MOVES_FILE,
    SMART_MONEY_PICKS_FILE
)

# Setup logging
logger = setup_logging('pipeline.log')


class InsiderTracker:
    """Track insider trading activity"""
    
    def __init__(self):
        self.output_file = INSIDER_MOVES_FILE
    
    def get_insider_activity(self, ticker: str) -> List[Dict]:
        """
        Get insider activity for a ticker
        
        Returns:
            List of recent insider transactions
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.insider_transactions
            
            if df is None or df.empty:
                return []
            
            # Filter transactions in last 6 months
            cutoff = pd.Timestamp.now() - pd.Timedelta(days=180)
            
            # Sort by date (most recent first)
            if isinstance(df.index, pd.DatetimeIndex):
                df = df.sort_index(ascending=False)
            else:
                # If index is not datetime, try to convert
                try:
                    df.index = pd.to_datetime(df.index)
                    df = df.sort_index(ascending=False)
                except:
                    logger.debug(f"Could not parse dates for {ticker}")
                    return []
            
            recent_transactions = []
            
            for date, row in df.iterrows():
                # Skip if before cutoff
                if isinstance(date, pd.Timestamp) and date < cutoff:
                    continue
                
                # Check transaction type
                transaction_text = str(row.get('Transaction', '') or row.get('Text', '') or '').lower()
                
                # Determine if it's a buy or sell
                is_buy = False
                is_sell = False
                
                if any(keyword in transaction_text for keyword in ['purchase', 'buy', 'acquisition', 'acquired']):
                    is_buy = True
                elif any(keyword in transaction_text for keyword in ['sale', 'sell', 'disposition', 'disposed']):
                    is_sell = True
                
                # Get transaction details
                value = float(row.get('Value', 0) or 0)
                shares = int(row.get('Shares', 0) or 0)
                insider_name = str(row.get('Insider', '') or row.get('Insider', 'N/A'))
                transaction_type = str(row.get('Transaction', '') or row.get('Text', 'N/A'))
                
                transaction = {
                    'date': str(date.date()) if isinstance(date, pd.Timestamp) else str(date),
                    'insider': insider_name,
                    'type': 'Buy' if is_buy else ('Sell' if is_sell else 'Unknown'),
                    'transaction': transaction_type,
                    'value': round(value, 2),
                    'shares': shares
                }
                
                recent_transactions.append(transaction)
            
            return recent_transactions
            
        except Exception as e:
            logger.debug(f"Error getting insider activity for {ticker}: {e}")
            return []
    
    def detect_cluster_buying(self, transactions: List[Dict]) -> Dict:
        """
        Detect cluster buying patterns
        
        Args:
            transactions: List of insider transactions
            
        Returns:
            Dictionary with cluster buying analysis
        """
        if not transactions:
            return {
                'has_cluster': False,
                'cluster_score': 0,
                'total_buy_value': 0,
                'buy_count': 0,
                'sell_count': 0
            }
        
        buys = [t for t in transactions if t.get('type') == 'Buy']
        sells = [t for t in transactions if t.get('type') == 'Sell']
        
        total_buy_value = sum(t.get('value', 0) for t in buys)
        buy_count = len(buys)
        sell_count = len(sells)
        
        # Cluster buying: Multiple buys in short period with significant value
        # Score based on:
        # 1. Number of buys (> 3 = cluster)
        # 2. Total value (> $1M = significant)
        # 3. Buy/Sell ratio
        
        cluster_score = 0
        
        if buy_count >= 3:
            cluster_score += 30
        elif buy_count >= 2:
            cluster_score += 15
        
        if total_buy_value > 1_000_000:
            cluster_score += 30
        elif total_buy_value > 500_000:
            cluster_score += 15
        elif total_buy_value > 100_000:
            cluster_score += 10
        
        if buy_count > 0 and sell_count == 0:
            cluster_score += 20  # Pure buying, no selling
        elif buy_count > sell_count * 2:
            cluster_score += 10  # Strong buy/sell ratio
        
        has_cluster = cluster_score >= 40
        
        return {
            'has_cluster': has_cluster,
            'cluster_score': cluster_score,
            'total_buy_value': round(total_buy_value, 2),
            'buy_count': buy_count,
            'sell_count': sell_count,
            'buy_sell_ratio': round(buy_count / sell_count, 2) if sell_count > 0 else float('inf')
        }
    
    def analyze_tickers(self, tickers: List[str]) -> Dict:
        """
        Analyze insider activity for multiple tickers
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"🚀 Starting Insider Tracking for {len(tickers)} tickers...")
        
        results = {}
        
        for ticker in tickers:
            logger.info(f"📊 Analyzing {ticker}...")
            
            transactions = self.get_insider_activity(ticker)
            
            if transactions:
                cluster_analysis = self.detect_cluster_buying(transactions)
                
                # Calculate insider score (0-100)
                insider_score = 50
                
                if cluster_analysis['has_cluster']:
                    insider_score += 30
                elif cluster_analysis['cluster_score'] >= 30:
                    insider_score += 15
                
                if cluster_analysis['buy_count'] > cluster_analysis['sell_count'] * 2:
                    insider_score += 15
                elif cluster_analysis['sell_count'] > cluster_analysis['buy_count'] * 2:
                    insider_score -= 15
                
                if cluster_analysis['total_buy_value'] > 1_000_000:
                    insider_score += 10
                
                insider_score = max(0, min(100, insider_score))
                
                results[ticker] = {
                    'insider_score': insider_score,
                    'cluster_analysis': cluster_analysis,
                    'recent_transactions': transactions[:10],  # Top 10 most recent
                    'total_transactions': len(transactions)
                }
                
                logger.info(f"   ✅ {ticker}: {cluster_analysis['buy_count']} buys, "
                          f"{cluster_analysis['sell_count']} sells, "
                          f"Score: {insider_score}")
            else:
                logger.debug(f"   ⚠️ No recent insider activity for {ticker}")
            
            # Rate limiting
            time.sleep(0.2)
        
        return results
    
    def get_tickers_from_smart_money_picks(self) -> List[str]:
        """Get tickers from smart money picks file"""
        try:
            if SMART_MONEY_PICKS_FILE.exists():
                df = pd.read_csv(SMART_MONEY_PICKS_FILE)
                if 'ticker' in df.columns:
                    # Get top 20 picks
                    return df['ticker'].head(20).tolist()
        except Exception as e:
            logger.debug(f"Error loading smart money picks: {e}")
        
        # Default watchlist
        return ['AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NFLX', 'INTC']
    
    def save_results(self, results: Dict) -> None:
        """Save analysis results to JSON file"""
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'total_tickers': len(results),
            'details': results
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Saved to {self.output_file}")
        
        # Print summary
        if results:
            cluster_stocks = [t for t, data in results.items() 
                            if data.get('cluster_analysis', {}).get('has_cluster', False)]
            
            logger.info("\n📊 Insider Activity Summary:")
            logger.info(f"   Total tickers analyzed: {len(results)}")
            logger.info(f"   Cluster buying detected: {len(cluster_stocks)}")
            
            if cluster_stocks:
                logger.info("\n🔥 Cluster Buying Detected:")
                for ticker in cluster_stocks[:5]:
                    data = results[ticker]
                    cluster = data['cluster_analysis']
                    logger.info(f"   {ticker}: {cluster['buy_count']} buys, "
                              f"${cluster['total_buy_value']:,.0f} value")
    
    def run(self, tickers: Optional[List[str]] = None) -> Dict:
        """Main execution"""
        if tickers is None:
            tickers = self.get_tickers_from_smart_money_picks()
        
        results = self.analyze_tickers(tickers)
        
        if results:
            self.save_results(results)
        else:
            logger.warning("No results to save")
        
        return results


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Insider Trading Tracker')
    parser.add_argument('--tickers', nargs='+', help='Specific tickers to analyze')
    args = parser.parse_args()
    
    tracker = InsiderTracker()
    
    tickers = args.tickers if args.tickers else None
    results = tracker.run(tickers=tickers)
    
    if results:
        print("\n📊 Insider Activity Analysis Complete")
        print(f"   Analyzed {len(results)} tickers")
        
        # Show top cluster buying
        cluster_stocks = sorted(
            [(t, data) for t, data in results.items() 
             if data.get('cluster_analysis', {}).get('has_cluster', False)],
            key=lambda x: x[1]['insider_score'],
            reverse=True
        )
        
        if cluster_stocks:
            print("\n🔥 Top Cluster Buying:")
            for ticker, data in cluster_stocks[:5]:
                cluster = data['cluster_analysis']
                print(f"   {ticker}: Score {data['insider_score']} | "
                      f"{cluster['buy_count']} buys, ${cluster['total_buy_value']:,.0f}")


if __name__ == "__main__":
    main()

