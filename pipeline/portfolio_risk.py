#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portfolio Risk Analysis
Analyzes portfolio risk metrics including correlation, volatility, and diversification
"""

import json
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from typing import Dict, List, Optional
import warnings

warnings.filterwarnings('ignore')

# Import core config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import (
    setup_logging,
    PORTFOLIO_RISK_FILE,
    SMART_MONEY_PICKS_FILE
)

# Setup logging
logger = setup_logging('pipeline.log')


class PortfolioRiskAnalyzer:
    """Analyze portfolio risk metrics"""
    
    def __init__(self):
        self.output_file = PORTFOLIO_RISK_FILE
    
    def get_tickers_from_smart_money_picks(self, top_n: int = 20) -> List[str]:
        """Get tickers from smart money picks file"""
        try:
            if SMART_MONEY_PICKS_FILE.exists():
                df = pd.read_csv(SMART_MONEY_PICKS_FILE)
                if 'ticker' in df.columns:
                    return df['ticker'].head(top_n).tolist()
        except Exception as e:
            logger.debug(f"Error loading smart money picks: {e}")
        
        # Default portfolio
        return ['AAPL', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'AMD']
    
    def analyze_portfolio(self, tickers: List[str], period: str = '6mo') -> Dict:
        """
        Analyze portfolio risk metrics
        
        Args:
            tickers: List of ticker symbols
            period: Time period for analysis ('6mo', '1y', etc.)
            
        Returns:
            Dictionary with risk analysis results
        """
        logger.info(f"🚀 Starting Portfolio Risk Analysis for {len(tickers)} tickers...")
        
        try:
            # Download price data
            logger.info("📊 Downloading price data...")
            data = yf.download(tickers, period=period, progress=False)
            
            if data.empty:
                return {'error': 'No data available'}
            
            # Handle MultiIndex columns
            if isinstance(data.columns, pd.MultiIndex):
                close_prices = data['Close']
            else:
                # Single ticker case
                if len(tickers) == 1:
                    close_prices = pd.DataFrame({tickers[0]: data['Close']})
                else:
                    close_prices = data
            
            # Calculate returns
            returns = close_prices.pct_change().dropna()
            
            if returns.empty:
                return {'error': 'Insufficient data for returns calculation'}
            
            # Remove any tickers with insufficient data
            returns = returns.dropna(axis=1)
            valid_tickers = returns.columns.tolist()
            
            if len(valid_tickers) < 2:
                return {'error': 'Need at least 2 tickers for portfolio analysis'}
            
            logger.info(f"✅ Analyzing {len(valid_tickers)} valid tickers")
            
            # Correlation matrix
            corr = returns.corr()
            
            # Find high correlations (> 0.8)
            high_corr = []
            cols = corr.columns
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    corr_value = corr.iloc[i, j]
                    if not pd.isna(corr_value) and corr_value > 0.8:
                        high_corr.append({
                            'ticker1': cols[i],
                            'ticker2': cols[j],
                            'correlation': round(float(corr_value), 3)
                        })
            
            # Portfolio volatility calculation
            # Annualized covariance matrix
            cov = returns.cov() * 252  # 252 trading days per year
            
            # Equal weights
            weights = np.array([1.0 / len(valid_tickers)] * len(valid_tickers))
            
            # Portfolio variance
            portfolio_var = np.dot(weights.T, np.dot(cov, weights))
            portfolio_vol = np.sqrt(portfolio_var)
            
            # Individual stock volatilities
            individual_vols = {}
            for ticker in valid_tickers:
                ticker_returns = returns[ticker]
                ticker_vol = np.sqrt(ticker_returns.var() * 252)
                individual_vols[ticker] = round(float(ticker_vol * 100), 2)
            
            # Diversification ratio
            # Weighted average individual vol / portfolio vol
            avg_individual_vol = np.mean([np.sqrt(returns[t].var() * 252) for t in valid_tickers])
            diversification_ratio = avg_individual_vol / portfolio_vol if portfolio_vol > 0 else 1.0
            
            # Beta calculation (vs SPY)
            try:
                spy = yf.Ticker("SPY")
                spy_data = spy.history(period=period)['Close']
                spy_returns = spy_data.pct_change().dropna()
                
                # Align dates
                aligned_returns = returns.join(spy_returns, how='inner', rsuffix='_spy')
                aligned_returns = aligned_returns.dropna()
                
                if len(aligned_returns) > 0:
                    portfolio_returns = aligned_returns[valid_tickers].mean(axis=1)
                    spy_ret = aligned_returns['Close_spy']
                    
                    # Calculate beta
                    covariance = np.cov(portfolio_returns, spy_ret)[0, 1]
                    spy_variance = np.var(spy_ret)
                    beta = covariance / spy_variance if spy_variance > 0 else 1.0
                else:
                    beta = 1.0
            except Exception as e:
                logger.debug(f"Error calculating beta: {e}")
                beta = 1.0
            
            # Risk metrics summary
            risk_level = 'Low'
            if portfolio_vol > 0.30:
                risk_level = 'Very High'
            elif portfolio_vol > 0.25:
                risk_level = 'High'
            elif portfolio_vol > 0.20:
                risk_level = 'Medium-High'
            elif portfolio_vol > 0.15:
                risk_level = 'Medium'
            elif portfolio_vol > 0.10:
                risk_level = 'Low-Medium'
            
            # Correlation matrix as nested dict
            corr_dict = {}
            for ticker1 in valid_tickers:
                corr_dict[ticker1] = {}
                for ticker2 in valid_tickers:
                    corr_value = corr.loc[ticker1, ticker2]
                    corr_dict[ticker1][ticker2] = round(float(corr_value), 3) if not pd.isna(corr_value) else None
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'tickers': valid_tickers,
                'period': period,
                'metrics': {
                    'portfolio_volatility_pct': round(float(portfolio_vol * 100), 2),
                    'portfolio_volatility': round(float(portfolio_vol), 4),
                    'risk_level': risk_level,
                    'beta': round(float(beta), 3),
                    'diversification_ratio': round(float(diversification_ratio), 3),
                    'num_tickers': len(valid_tickers)
                },
                'individual_volatilities': individual_vols,
                'high_correlations': high_corr,
                'correlation_matrix': corr_dict,
                'warnings': []
            }
            
            # Add warnings
            if len(high_corr) > len(valid_tickers) / 2:
                result['warnings'].append('High concentration risk: Many stocks are highly correlated')
            
            if diversification_ratio < 1.2:
                result['warnings'].append('Low diversification: Portfolio volatility close to individual stock volatility')
            
            if portfolio_vol > 0.30:
                result['warnings'].append('Very high portfolio volatility: Consider reducing risk')
            
            logger.info(f"✅ Portfolio volatility: {portfolio_vol * 100:.2f}%")
            logger.info(f"✅ Beta: {beta:.3f}")
            logger.info(f"✅ Diversification ratio: {diversification_ratio:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in portfolio analysis: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'error': str(e)}
    
    def save_results(self, results: Dict) -> None:
        """Save analysis results to JSON file"""
        if 'error' in results:
            logger.error(f"Cannot save results: {results['error']}")
            return
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Saved to {self.output_file}")
    
    def run(self, tickers: Optional[List[str]] = None, top_n: int = 20) -> Dict:
        """Main execution"""
        if tickers is None:
            tickers = self.get_tickers_from_smart_money_picks(top_n)
        
        results = self.analyze_portfolio(tickers)
        
        if 'error' not in results:
            self.save_results(results)
        else:
            logger.warning(f"Analysis failed: {results.get('error')}")
        
        return results


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Portfolio Risk Analysis')
    parser.add_argument('--tickers', nargs='+', help='Specific tickers to analyze')
    parser.add_argument('--top', type=int, default=20, help='Number of top picks to analyze')
    args = parser.parse_args()
    
    analyzer = PortfolioRiskAnalyzer()
    
    tickers = args.tickers if args.tickers else None
    results = analyzer.run(tickers=tickers, top_n=args.top)
    
    if 'error' not in results:
        print("\n📊 Portfolio Risk Analysis Complete")
        metrics = results['metrics']
        print(f"   Portfolio Volatility: {metrics['portfolio_volatility_pct']:.2f}%")
        print(f"   Risk Level: {metrics['risk_level']}")
        print(f"   Beta: {metrics['beta']:.3f}")
        print(f"   Diversification Ratio: {metrics['diversification_ratio']:.3f}")
        
        if results.get('high_correlations'):
            print(f"\n⚠️ High Correlations ({len(results['high_correlations'])} pairs):")
            for corr in results['high_correlations'][:5]:
                print(f"   {corr['ticker1']} - {corr['ticker2']}: {corr['correlation']:.3f}")
        
        if results.get('warnings'):
            print("\n⚠️ Warnings:")
            for warning in results['warnings']:
                print(f"   - {warning}")


if __name__ == "__main__":
    main()

