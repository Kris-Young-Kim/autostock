#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask API Routes
API endpoint definitions for US Market Alpha Platform
"""

from flask import Flask, jsonify, request
from core.config import (
    SMART_MONEY_CURRENT_FILE,
    SMART_MONEY_PICKS_FILE,
    ETF_FLOWS_FILE,
    ETF_FLOW_ANALYSIS_FILE,
    SECTOR_HEATMAP_FILE,
    OPTIONS_FLOW_FILE,
    MACRO_ANALYSIS_FILE,
    MACRO_ANALYSIS_EN_FILE,
    WEEKLY_CALENDAR_FILE,
    PRICES_FILE,
    AI_SUMMARIES_FILE,
    DATA_PROCESSED_DIR
)
import json
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
import glob
import os

logger = logging.getLogger(__name__)


def register_routes(app: Flask, get_sector_func, calculate_rsi_func, analyze_trend_func):
    """
    Register all API routes to the Flask app
    
    Args:
        app: Flask application instance
        get_sector_func: Function to get sector for a ticker
        calculate_rsi_func: Function to calculate RSI
        analyze_trend_func: Function to analyze trend
    """
    
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
                pick['sector'] = get_sector_func(ticker)
            
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
        """Get Macro Economic Analysis (deprecated, use /api/us/macro-analysis)"""
        return get_us_macro_analysis()
    
    @app.route('/api/us/macro-analysis')
    def get_us_macro_analysis():
        """Get Macro Economic Analysis with language/model selection"""
        try:
            # Get query parameters
            lang = request.args.get('lang', 'ko').lower()
            model = request.args.get('model', 'gemini').lower()
            
            # Select file based on language
            if lang == 'en':
                analysis_file = MACRO_ANALYSIS_EN_FILE
            else:
                analysis_file = MACRO_ANALYSIS_FILE
            
            if not analysis_file.exists():
                return jsonify({'error': 'Macro analysis not found'}), 404
            
            with open(analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update real-time indicators if needed
            try:
                # Fetch current VIX, DXY, etc.
                vix = yf.Ticker('^VIX')
                vix_hist = vix.history(period='5d')
                if not vix_hist.empty:
                    data['indicators']['vix']['current'] = round(float(vix_hist['Close'].iloc[-1]), 2)
                    data['indicators']['vix']['change'] = round(
                        ((vix_hist['Close'].iloc[-1] / vix_hist['Close'].iloc[-2] - 1) * 100) if len(vix_hist) >= 2 else 0, 2
                    )
            except Exception as e:
                logger.debug(f"Error updating real-time indicators: {e}")
            
            return jsonify({
                **data,
                'lang': lang,
                'model': model
            })
        except Exception as e:
            logger.error(f"Error in /api/us/macro-analysis: {e}")
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
            rsi = calculate_rsi_func(hist['Close']) if not hist.empty else 50.0
            trend = analyze_trend_func(hist['Close']) if not hist.empty else {'trend': 'Unknown', 'strength': 0}
            
            return jsonify({
                'ticker': ticker,
                'name': info.get('longName', ticker),
                'sector': get_sector_func(ticker),
                'current_price': info.get('currentPrice', 0) or info.get('regularMarketPrice', 0) or 0,
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'rsi': rsi,
                'trend': trend
            })
        except Exception as e:
            logger.error(f"Error in /api/us/stock-info/{ticker}: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/us/ai-summary/<ticker>')
    def get_us_ai_summary(ticker):
        """Get AI summary for a specific ticker"""
        try:
            lang = request.args.get('lang', 'ko').lower()
            
            if not AI_SUMMARIES_FILE.exists():
                return jsonify({'error': 'AI summaries not found'}), 404
            
            with open(AI_SUMMARIES_FILE, 'r', encoding='utf-8') as f:
                summaries = json.load(f)
            
            if ticker not in summaries:
                return jsonify({'error': f'Summary not found for {ticker}'}), 404
            
            ticker_data = summaries[ticker]
            
            # Select language
            if lang == 'en' and 'summary_en' in ticker_data:
                summary_text = ticker_data['summary_en']
            else:
                summary_text = ticker_data.get('summary_ko', ticker_data.get('summary', ''))
            
            return jsonify({
                'ticker': ticker,
                'summary': summary_text,
                'lang': lang,
                'updated': ticker_data.get('updated', ''),
                'news_count': ticker_data.get('news_count', 0)
            })
        except Exception as e:
            logger.error(f"Error in /api/us/ai-summary/{ticker}: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/us/technical-indicators/<ticker>')
    def get_us_technical_indicators(ticker):
        """Get technical indicators (RSI, MACD, Bollinger Bands, Support/Resistance)"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1y')
            
            if hist.empty:
                return jsonify({'error': 'No data available'}), 404
            
            closes = hist['Close']
            highs = hist['High']
            lows = hist['Low']
            volumes = hist['Volume']
            
            # RSI
            rsi = calculate_rsi_func(closes)
            
            # MACD
            ema12 = closes.ewm(span=12, adjust=False).mean()
            ema26 = closes.ewm(span=26, adjust=False).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            histogram = macd_line - signal_line
            
            macd = {
                'macd': round(float(macd_line.iloc[-1]), 2),
                'signal': round(float(signal_line.iloc[-1]), 2),
                'histogram': round(float(histogram.iloc[-1]), 2),
                'trend': 'Bullish' if histogram.iloc[-1] > 0 else 'Bearish'
            }
            
            # Bollinger Bands
            bb_period = 20
            bb_std = 2
            sma = closes.rolling(bb_period).mean()
            std = closes.rolling(bb_period).std()
            upper_band = sma + (std * bb_std)
            lower_band = sma - (std * bb_std)
            
            current_price = closes.iloc[-1]
            bb_position = (current_price - lower_band.iloc[-1]) / (upper_band.iloc[-1] - lower_band.iloc[-1]) if upper_band.iloc[-1] != lower_band.iloc[-1] else 0.5
            
            bollinger = {
                'upper': round(float(upper_band.iloc[-1]), 2),
                'middle': round(float(sma.iloc[-1]), 2),
                'lower': round(float(lower_band.iloc[-1]), 2),
                'position': round(float(bb_position), 2),  # 0-1, where 0.5 is middle
                'signal': 'Overbought' if bb_position > 0.8 else 'Oversold' if bb_position < 0.2 else 'Neutral'
            }
            
            # Support and Resistance levels
            # Use pivot points and recent highs/lows
            recent_period = 20
            recent_highs = highs.tail(recent_period)
            recent_lows = lows.tail(recent_period)
            
            resistance_levels = []
            support_levels = []
            
            # Find resistance (local highs)
            for i in range(1, len(recent_highs) - 1):
                if recent_highs.iloc[i] > recent_highs.iloc[i-1] and recent_highs.iloc[i] > recent_highs.iloc[i+1]:
                    resistance_levels.append(float(recent_highs.iloc[i]))
            
            # Find support (local lows)
            for i in range(1, len(recent_lows) - 1):
                if recent_lows.iloc[i] < recent_lows.iloc[i-1] and recent_lows.iloc[i] < recent_lows.iloc[i+1]:
                    support_levels.append(float(recent_lows.iloc[i]))
            
            # Get top 3 resistance and support levels
            resistance_levels = sorted(set(resistance_levels), reverse=True)[:3]
            support_levels = sorted(set(support_levels))[:3]
            
            # Calculate distance to nearest levels
            nearest_resistance = min(resistance_levels) if resistance_levels else None
            nearest_support = max(support_levels) if support_levels else None
            
            support_resistance = {
                'resistance_levels': [round(r, 2) for r in resistance_levels],
                'support_levels': [round(s, 2) for s in support_levels],
                'nearest_resistance': round(nearest_resistance, 2) if nearest_resistance else None,
                'nearest_support': round(nearest_support, 2) if nearest_support else None,
                'distance_to_resistance': round(((nearest_resistance / current_price - 1) * 100), 2) if nearest_resistance else None,
                'distance_to_support': round(((current_price / nearest_support - 1) * 100), 2) if nearest_support else None
            }
            
            return jsonify({
                'ticker': ticker,
                'current_price': round(float(current_price), 2),
                'rsi': round(rsi, 2),
                'macd': macd,
                'bollinger_bands': bollinger,
                'support_resistance': support_resistance,
                'trend': analyze_trend_func(closes)
            })
        except Exception as e:
            logger.error(f"Error in /api/us/technical-indicators/{ticker}: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/us/history-dates')
    def get_us_history_dates():
        """Get list of available historical analysis dates"""
        try:
            dates = []
            
            # Check for historical smart_money_current.json files
            pattern = str(DATA_PROCESSED_DIR / 'smart_money_current_*.json')
            files = glob.glob(pattern)
            
            for file in files:
                # Extract date from filename (format: smart_money_current_YYYY-MM-DD.json)
                try:
                    filename = os.path.basename(file)
                    date_str = filename.replace('smart_money_current_', '').replace('.json', '')
                    # Validate date format
                    datetime.strptime(date_str, '%Y-%m-%d')
                    dates.append(date_str)
                except:
                    continue
            
            # Also check current file
            if SMART_MONEY_CURRENT_FILE.exists():
                try:
                    with open(SMART_MONEY_CURRENT_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'date' in data:
                            dates.append(data['date'])
                        elif 'updated' in data:
                            # Extract date from ISO format
                            updated = data['updated']
                            if 'T' in updated:
                                dates.append(updated.split('T')[0])
                except:
                    pass
            
            # Remove duplicates and sort
            dates = sorted(set(dates), reverse=True)
            
            return jsonify({
                'dates': dates,
                'count': len(dates)
            })
        except Exception as e:
            logger.error(f"Error in /api/us/history-dates: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/us/history/<date>')
    def get_us_history(date):
        """Get historical analysis results for a specific date"""
        try:
            # Validate date format
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            
            # Try to load historical file
            hist_file = DATA_PROCESSED_DIR / f'smart_money_current_{date}.json'
            
            if hist_file.exists():
                with open(hist_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return jsonify(data)
            
            # Fallback: check if date matches current file
            if SMART_MONEY_CURRENT_FILE.exists():
                with open(SMART_MONEY_CURRENT_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    file_date = None
                    if 'date' in data:
                        file_date = data['date']
                    elif 'updated' in data:
                        updated = data['updated']
                        if 'T' in updated:
                            file_date = updated.split('T')[0]
                    
                    if file_date == date:
                        return jsonify(data)
            
            return jsonify({'error': f'No data found for date {date}'}), 404
        except Exception as e:
            logger.error(f"Error in /api/us/history/{date}: {e}")
            return jsonify({'error': str(e)}), 500
