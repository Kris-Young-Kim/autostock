#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sector Performance Heatmap Data Collector
Collects sector ETF performance data for heatmap visualization
"""

import json
import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import Dict, List
import time

# Import core config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import (
    setup_logging,
    SECTOR_HEATMAP_FILE
)

# Setup logging
logger = setup_logging('pipeline.log')


class SectorHeatmapCollector:
    """Collect sector ETF performance data for heatmap visualization"""
    
    def __init__(self):
        # 11 S&P Sector ETFs with full names and colors
        self.sector_etfs = {
            'XLK': {'name': 'Technology', 'color': '#4A90A4'},
            'XLF': {'name': 'Financials', 'color': '#6B8E23'},
            'XLV': {'name': 'Healthcare', 'color': '#FF69B4'},
            'XLE': {'name': 'Energy', 'color': '#FF6347'},
            'XLY': {'name': 'Consumer Disc.', 'color': '#FFD700'},
            'XLP': {'name': 'Consumer Staples', 'color': '#98D8C8'},
            'XLI': {'name': 'Industrials', 'color': '#DDA0DD'},
            'XLB': {'name': 'Materials', 'color': '#F0E68C'},
            'XLU': {'name': 'Utilities', 'color': '#87CEEB'},
            'XLRE': {'name': 'Real Estate', 'color': '#CD853F'},
            'XLC': {'name': 'Comm. Services', 'color': '#9370DB'},
        }
        
        # Representative stocks for each sector (for detailed treemap)
        self.sector_stocks = {
            'Technology': ['AAPL', 'MSFT', 'NVDA', 'AVGO', 'ORCL', 'CRM', 'AMD', 'ADBE'],
            'Financials': ['BRK-B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'GS', 'MS'],
            'Healthcare': ['UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR'],
            'Energy': ['XOM', 'CVX', 'SLB', 'EOG', 'COP', 'MPC', 'VLO', 'PSX'],
            'Consumer Disc.': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'LOW', 'TJX'],
            'Consumer Staples': ['PG', 'KO', 'PEP', 'COST', 'WMT', 'PM', 'MO', 'CL'],
            'Industrials': ['BA', 'CAT', 'GE', 'HON', 'UPS', 'RTX', 'DE', 'LMT'],
            'Materials': ['LIN', 'APD', 'ECL', 'SHW', 'DD', 'FCX', 'NEM', 'PPG'],
            'Utilities': ['NEE', 'DUK', 'SO', 'AEP', 'SRE', 'EXC', 'XEL', 'WEC'],
            'Real Estate': ['PLD', 'AMT', 'EQIX', 'PSA', 'WELL', 'SPG', 'O', 'DLR'],
            'Comm. Services': ['META', 'GOOGL', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'CHTR'],
        }
    
    def get_sector_performance(self, period: str = '5d') -> Dict:
        """Get sector ETF performance data"""
        logger.info(f"📊 Fetching sector ETF performance ({period})...")
        
        results = []
        
        for ticker, info in self.sector_etfs.items():
            try:
                etf = yf.Ticker(ticker)
                hist = etf.history(period=period)
                
                if hist.empty or len(hist) < 2:
                    logger.debug(f"⚠️ Insufficient data for {ticker}")
                    continue
                
                # Sort by index (date)
                hist = hist.sort_index()
                
                # Calculate performance metrics
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change_pct = ((current_price / prev_price) - 1) * 100 if prev_price > 0 else 0
                
                # Calculate volume-weighted activity
                volume = hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
                weight = current_price * volume
                
                # Calculate 5-day return if available
                if len(hist) >= 5:
                    return_5d = ((current_price / hist['Close'].iloc[-5]) - 1) * 100 if hist['Close'].iloc[-5] > 0 else 0
                else:
                    return_5d = change_pct
                
                results.append({
                    'ticker': ticker,
                    'name': info['name'],
                    'color': info['color'],
                    'current_price': round(current_price, 2),
                    'change_pct': round(change_pct, 2),
                    'return_5d': round(return_5d, 2),
                    'volume': int(volume),
                    'weight': round(weight, 0),
                    'heat_color': self._get_color(change_pct)
                })
                
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logger.debug(f"Error fetching {ticker}: {e}")
                continue
        
        # Sort by weight (activity)
        results.sort(key=lambda x: x['weight'], reverse=True)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'period': period,
            'sectors': results
        }
    
    def get_full_market_map(self, period: str = '5d') -> Dict:
        """Get full market map data (Sectors -> Stocks) for Treemap"""
        logger.info(f"📊 Fetching full market map data ({period})...")
        
        all_tickers = []
        ticker_to_sector = {}
        
        for sector, stocks in self.sector_stocks.items():
            all_tickers.extend(stocks)
            for stock in stocks:
                ticker_to_sector[stock] = sector
        
        if not all_tickers:
            return {'error': 'No tickers defined'}
        
        try:
            # Download data for all tickers
            data = yf.download(all_tickers, period=period, progress=False, group_by='ticker')
            
            if data.empty:
                return {'error': 'No data'}
            
            # Initialize market map
            market_map = {sector: [] for sector in self.sector_stocks.keys()}
            
            # Process each ticker
            for ticker in all_tickers:
                try:
                    # Handle different data structures from yfinance
                    if isinstance(data.columns, pd.MultiIndex):
                        # Multi-index structure
                        if ticker not in data.columns.levels[1]:
                            continue
                        prices = data['Close'][ticker].dropna()
                        volumes = data['Volume'][ticker] if ('Volume', ticker) in data.columns else pd.Series()
                    else:
                        # Single ticker or flat structure
                        if ticker not in data.columns:
                            continue
                        prices = data[ticker]['Close'] if isinstance(data[ticker], pd.DataFrame) else data[ticker]
                        prices = prices.dropna()
                        volumes = data[ticker]['Volume'] if isinstance(data[ticker], pd.DataFrame) and 'Volume' in data[ticker].columns else pd.Series()
                    
                    if len(prices) < 2:
                        continue
                    
                    current = prices.iloc[-1]
                    prev = prices.iloc[-2]
                    change = ((current / prev) - 1) * 100 if prev > 0 else 0
                    
                    # Weight by Volume * Price (Activity proxy)
                    vol = volumes.iloc[-1] if len(volumes) > 0 else 100000
                    weight = current * vol
                    
                    sector = ticker_to_sector.get(ticker, 'Unknown')
                    if sector in market_map:
                        market_map[sector].append({
                            'x': ticker,
                            'y': round(weight, 0),
                            'price': round(current, 2),
                            'change': round(change, 2),
                            'color': self._get_color(change)
                        })
                except Exception as e:
                    logger.debug(f"Error processing {ticker}: {e}")
                    continue
            
            # Convert to series format for treemap
            series = []
            for sector_name, stocks in market_map.items():
                if stocks:
                    stocks.sort(key=lambda x: x['y'], reverse=True)
                    series.append({'name': sector_name, 'data': stocks})
            
            # Sort sectors by total weight
            series.sort(key=lambda s: sum(i['y'] for i in s['data']), reverse=True)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'period': period,
                'series': series
            }
            
        except Exception as e:
            logger.error(f"Error in get_full_market_map: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'error': str(e)}
    
    def _get_color(self, change: float) -> str:
        """Get color based on change percentage"""
        if change >= 3:
            return '#00C853'  # Dark green
        elif change >= 1:
            return '#4CAF50'  # Green
        elif change >= 0:
            return '#81C784'  # Light green
        elif change >= -1:
            return '#EF9A9A'  # Light red
        elif change >= -3:
            return '#F44336'  # Red
        else:
            return '#B71C1C'  # Dark red
    
    def save_data(self) -> Dict:
        """Save sector heatmap data"""
        logger.info("🚀 Starting Sector Heatmap Collection...")
        
        # Get sector performance
        sector_data = self.get_sector_performance('5d')
        
        # Get full market map (optional, can be skipped if it fails)
        try:
            market_map = self.get_full_market_map('5d')
            if 'error' not in market_map:
                sector_data['market_map'] = market_map
        except Exception as e:
            logger.warning(f"Could not generate market map: {e}")
        
        # Save to file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(sector_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Saved to {self.output_file}")
        logger.info(f"📊 Collected {len(sector_data.get('sectors', []))} sectors")
        
        return sector_data
    
    @property
    def output_file(self):
        return SECTOR_HEATMAP_FILE


def main():
    """Main execution"""
    collector = SectorHeatmapCollector()
    data = collector.save_data()
    
    if 'sectors' in data:
        print("\n📊 Sector Performance Summary:")
        for sector in data['sectors'][:5]:  # Top 5
            print(f"   {sector['ticker']} ({sector['name']}): {sector['change_pct']:+.2f}%")


if __name__ == "__main__":
    main()

