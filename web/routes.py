#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask API Routes
API endpoint definitions for US Market Alpha Platform
"""

from flask import jsonify, request
from web.app import app
from web.app import get_sector, calculate_rsi, analyze_trend
from core.config import (
    SMART_MONEY_CURRENT_FILE,
    SMART_MONEY_PICKS_FILE,
    ETF_FLOWS_FILE,
    ETF_FLOW_ANALYSIS_FILE,
    SECTOR_HEATMAP_FILE,
    OPTIONS_FLOW_FILE,
    MACRO_ANALYSIS_FILE,
    WEEKLY_CALENDAR_FILE,
    PRICES_FILE
)
import json
import pandas as pd
import yfinance as yf
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@app.route('/api/us/portfolio')
def get_us_portfolio():
    """Get market index data (Dow, S&P 500, NASDAQ, VIX)"""
    try:
        indices = {
            'DIA': 'Dow Jones',
            'SPY': 'S&P 500',
            'QQQ': 'NASDAQ',
            '^VIX': 'VIX'
        }
        
        results = []
        for ticker, name in indices.items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='5d')
                
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) >= 2 else current
                    change = ((current / prev) - 1) * 100 if prev > 0 else 0
                    
                    results.append({
                        'ticker': ticker,
                        'name': name,
                        'price': round(float(current), 2),
                        'change': round(change, 2)
                    })
            except Exception as e:
                logger.debug(f"Error fetching {ticker}: {e}")
                continue
        
        return jsonify({'indices': results})
    except Exception as e:
        logger.error(f"Error in /api/us/portfolio: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/us/smart-money')
def get_us_smart_money():
    """Get Smart Money Picks with real-time prices"""
    try:
        # Try to load from current file first
        if SMART_MONEY_CURRENT_FILE.exists():
            with open(SMART_MONEY_CURRENT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                picks = data.get('picks', [])
        elif SMART_MONEY_PICKS_FILE.exists():
            df = pd.read_csv(SMART_MONEY_PICKS_FILE)
            picks = df.head(20).to_dict('records')
        else:
            return jsonify({'error': 'Smart Money data not found'}), 404
        
        # Update with real-time prices
        tickers = [p['ticker'] for p in picks]
        current_prices = {}
        
        try:
            for ticker in tickers[:10]:  # Limit to avoid rate limiting
                stock = yf.Ticker(ticker)
                info = stock.info
                current_prices[ticker] = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0) or 0
        except:
            pass
        
        # Update picks with current prices
        for pick in picks:
            ticker = pick['ticker']
            rec_price = pick.get('current_price', 0) or pick.get('price_at_rec', 0) or 0
            cur_price = current_prices.get(ticker, rec_price) or rec_price
            
            if rec_price > 0:
                change_pct = ((cur_price / rec_price) - 1) * 100
            else:
                change_pct = 0
            
            pick['current_price'] = round(cur_price, 2)
            pick['change_since_rec'] = round(change_pct, 2)
            pick['sector'] = get_sector(ticker)
        
        return jsonify({
            'top_picks': picks,
            'summary': {
                'total_analyzed': len(picks),
                'avg_score': round(sum(p.get('final_score', p.get('composite_score', 0)) for p in picks) / len(picks), 1) if picks else 0
            }
        })
    except Exception as e:
        logger.error(f"Error in /api/us/smart-money: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/us/etf-flows')
def get_us_etf_flows():
    """Get ETF Fund Flow Analysis"""
    try:
        if not ETF_FLOWS_FILE.exists():
            return jsonify({'error': 'ETF flows not found. Run analyze_etf_flows.py first.'}), 404
        
        df = pd.read_csv(ETF_FLOWS_FILE)
        
        # Calculate market sentiment
        broad_market = df[df['category'] == 'Broad Market']
        broad_score = round(broad_market['flow_score'].mean(), 1) if not broad_market.empty else 50
        
        # Sector summary
        sector_flows = df[df['category'] == 'Sector'].to_dict(orient='records')
        
        # Top inflows and outflows
        top_inflows = df.nlargest(5, 'flow_score').to_dict(orient='records')
        top_outflows = df.nsmallest(5, 'flow_score').to_dict(orient='records')
        
        # Load AI analysis
        ai_analysis_text = ""
        if ETF_FLOW_ANALYSIS_FILE.exists():
            try:
                with open(ETF_FLOW_ANALYSIS_FILE, 'r', encoding='utf-8') as f:
                    ai_data = json.load(f)
                    ai_analysis_text = ai_data.get('ai_analysis', '')
            except Exception as e:
                logger.debug(f"Error loading ETF AI analysis: {e}")
        
        return jsonify({
            'market_sentiment_score': broad_score,
            'sector_flows': sector_flows,
            'top_inflows': top_inflows,
            'top_outflows': top_outflows,
            'all_etfs': df.to_dict(orient='records'),
            'ai_analysis': ai_analysis_text
        })
    except Exception as e:
        logger.error(f"Error in /api/us/etf-flows: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/us/sector-heatmap')
def get_us_sector_heatmap():
    """Get Sector Heatmap Data"""
    try:
        if not SECTOR_HEATMAP_FILE.exists():
            return jsonify({'error': 'Sector heatmap not found'}), 404
        
        with open(SECTOR_HEATMAP_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/us/sector-heatmap: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/us/options-flow')
def get_us_options_flow():
    """Get Options Flow Data"""
    try:
        if not OPTIONS_FLOW_FILE.exists():
            return jsonify({'error': 'Options flow not found'}), 404
        
        with open(OPTIONS_FLOW_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/us/options-flow: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/us/macro')
def get_us_macro():
    """Get Macro Economic Analysis"""
    try:
        if not MACRO_ANALYSIS_FILE.exists():
            return jsonify({'error': 'Macro analysis not found'}), 404
        
        with open(MACRO_ANALYSIS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/us/macro: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/us/calendar')
def get_us_calendar():
    """Get Economic Calendar"""
    try:
        if not WEEKLY_CALENDAR_FILE.exists():
            return jsonify({'error': 'Economic calendar not found'}), 404
        
        with open(WEEKLY_CALENDAR_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/us/calendar: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/us/stock-chart/<ticker>')
def get_us_stock_chart(ticker):
    """Get US stock chart data (OHLC) for candlestick chart"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='3mo')
        
        if hist.empty:
            return jsonify({'error': 'No data available'}), 404
        
        # Format for chart
        chart_data = []
        for date, row in hist.iterrows():
            chart_data.append({
                'time': date.strftime('%Y-%m-%d'),
                'open': round(float(row['Open']), 2),
                'high': round(float(row['High']), 2),
                'low': round(float(row['Low']), 2),
                'close': round(float(row['Close']), 2),
                'volume': int(row['Volume'])
            })
        
        return jsonify({
            'ticker': ticker,
            'data': chart_data
        })
    except Exception as e:
        logger.error(f"Error in /api/us/stock-chart/{ticker}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/us/stock-info/<ticker>')
def get_us_stock_info(ticker):
    """Get detailed stock information"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period='6mo')
        
        # Calculate technical indicators
        rsi = calculate_rsi(hist['Close']) if not hist.empty else 50.0
        trend = analyze_trend(hist['Close']) if not hist.empty else {'trend': 'Unknown', 'strength': 0}
        
        return jsonify({
            'ticker': ticker,
            'name': info.get('longName', ticker),
            'sector': get_sector(ticker),
            'current_price': info.get('currentPrice', 0) or info.get('regularMarketPrice', 0) or 0,
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'rsi': rsi,
            'trend': trend
        })
    except Exception as e:
        logger.error(f"Error in /api/us/stock-info/{ticker}: {e}")
        return jsonify({'error': str(e)}), 500

