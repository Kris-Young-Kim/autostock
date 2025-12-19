#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Top 10 Report Generator
Combines Quant Score and AI Analysis to generate final investment recommendations
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

# Import core config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import (
    setup_logging,
    SMART_MONEY_PICKS_FILE,
    AI_SUMMARIES_FILE,
    FINAL_REPORT_FILE,
    SMART_MONEY_CURRENT_FILE
)

# Setup logging
logger = setup_logging('pipeline.log')


class FinalReportGenerator:
    """Generate final top 10 investment report"""
    
    def __init__(self):
        self.output_file = FINAL_REPORT_FILE
        self.dashboard_file = SMART_MONEY_CURRENT_FILE
    
    def load_quant_data(self) -> pd.DataFrame:
        """Load quantitative screening results"""
        if not SMART_MONEY_PICKS_FILE.exists():
            logger.error(f"Smart Money Picks file not found: {SMART_MONEY_PICKS_FILE}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(SMART_MONEY_PICKS_FILE)
            # Sort by composite_score descending
            if 'composite_score' in df.columns:
                df = df.sort_values('composite_score', ascending=False)
            return df
        except Exception as e:
            logger.error(f"Error loading quant data: {e}")
            return pd.DataFrame()
    
    def load_ai_data(self) -> Dict:
        """Load AI summaries"""
        if not AI_SUMMARIES_FILE.exists():
            logger.warning(f"AI summaries file not found: {AI_SUMMARIES_FILE}")
            return {}
        
        try:
            with open(AI_SUMMARIES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading AI data: {e}")
            return {}
    
    def calculate_ai_score(self, summary: str) -> tuple:
        """
        Calculate AI bonus score based on summary content
        
        Returns:
            Tuple of (ai_score, recommendation)
        """
        if not summary or summary == "API Key Missing" or summary == "Analysis Failed":
            return 0, "Hold"
        
        summary_lower = summary.lower()
        
        # Initialize
        ai_score = 0
        rec = "Hold"
        
        # Check for buy signals
        buy_keywords = ['buy', '매수', 'purchase', 'acquisition']
        strong_buy_keywords = ['strong buy', '적극 매수', 'aggressive', 'high conviction']
        sell_keywords = ['sell', '매도', 'avoid', 'caution', 'risk']
        
        # Strong buy signals
        if any(keyword in summary_lower for keyword in strong_buy_keywords):
            ai_score = 20
            rec = "Strong Buy"
        # Regular buy signals
        elif any(keyword in summary_lower for keyword in buy_keywords):
            ai_score = 10
            rec = "Buy"
        # Sell signals
        elif any(keyword in summary_lower for keyword in sell_keywords):
            ai_score = -10
            rec = "Sell"
        
        # Additional scoring based on positive/negative sentiment
        positive_words = ['opportunity', 'growth', 'upside', 'potential', '기회', '성장', '상승', '잠재력']
        negative_words = ['risk', 'concern', 'decline', 'downside', '리스크', '우려', '하락', '약세']
        
        positive_count = sum(1 for word in positive_words if word in summary_lower)
        negative_count = sum(1 for word in negative_words if word in summary_lower)
        
        # Adjust score based on sentiment
        if positive_count > negative_count:
            ai_score += 5
        elif negative_count > positive_count:
            ai_score -= 5
        
        # Clamp score to reasonable range
        ai_score = max(-20, min(25, ai_score))
        
        return ai_score, rec
    
    def generate_report(self, top_n: int = 10) -> List[Dict]:
        """
        Generate final report combining quant and AI analysis
        
        Args:
            top_n: Number of top picks to include
            
        Returns:
            List of final picks
        """
        logger.info(f"🚀 Generating Final Top {top_n} Report...")
        
        # Load data
        df = self.load_quant_data()
        if df.empty:
            logger.error("No quant data available")
            return []
        
        ai_data = self.load_ai_data()
        
        logger.info(f"📊 Loaded {len(df)} quant picks, {len(ai_data)} AI summaries")
        
        results = []
        
        for idx, row in df.iterrows():
            ticker = row['ticker']
            
            # Get AI summary
            summary = ""
            if ticker in ai_data:
                summary = ai_data[ticker].get('summary', '') or ai_data[ticker].get('summary_ko', '')
            
            # Calculate AI score
            ai_score, ai_recommendation = self.calculate_ai_score(summary)
            
            # Get quant score
            quant_score = row.get('composite_score', 0)
            
            # Calculate final score (Quant 80% + AI 20%)
            # AI score is added as bonus (0-25), so we scale it to 0-20 for 20% weight
            ai_weighted = (ai_score / 25) * 20 if ai_score > 0 else (ai_score / 20) * 20
            final_score = quant_score * 0.8 + ai_weighted
            
            # Ensure final score is within 0-100 range
            final_score = max(0, min(100, final_score))
            
            result = {
                'ticker': ticker,
                'name': row.get('name', ticker),
                'final_score': round(final_score, 1),
                'quant_score': round(quant_score, 1),
                'ai_score': ai_score,
                'ai_recommendation': ai_recommendation,
                'current_price': row.get('current_price', 0),
                'target_price': row.get('target_price', 'N/A'),
                'target_upside': row.get('target_upside', 0),
                'grade': row.get('grade', 'N/A'),
                'ai_summary': summary,
                'sector': row.get('size', 'N/A'),  # Using size as sector proxy if sector not available
                'rsi': row.get('rsi', 'N/A'),
                'pe_ratio': row.get('pe_ratio', 'N/A'),
                'revenue_growth': row.get('revenue_growth', 'N/A'),
                'rs_20d': row.get('rs_20d', 'N/A')
            }
            
            results.append(result)
        
        # Sort by final score
        results.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Assign ranks
        top_picks = results[:top_n]
        for i, pick in enumerate(top_picks, 1):
            pick['rank'] = i
        
        logger.info(f"✅ Generated report for {len(top_picks)} picks")
        
        return top_picks
    
    def save_report(self, top_picks: List[Dict]) -> None:
        """Save final report to JSON files"""
        if not top_picks:
            logger.warning("No picks to save")
            return
        
        # Prepare report data
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_picks': len(top_picks),
            'top_picks': top_picks,
            'summary': {
                'avg_final_score': round(sum(p['final_score'] for p in top_picks) / len(top_picks), 1),
                'avg_quant_score': round(sum(p['quant_score'] for p in top_picks) / len(top_picks), 1),
                'avg_ai_score': round(sum(p['ai_score'] for p in top_picks) / len(top_picks), 1)
            }
        }
        
        # Save final report
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Saved final report to {self.output_file}")
        
        # Save dashboard file (simplified format)
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'picks': top_picks
        }
        
        with open(self.dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Saved dashboard file to {self.dashboard_file}")
    
    def run(self, top_n: int = 10) -> List[Dict]:
        """Main execution"""
        top_picks = self.generate_report(top_n)
        
        if top_picks:
            self.save_report(top_picks)
        else:
            logger.warning("No picks generated")
        
        return top_picks


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Final Top 10 Report Generator')
    parser.add_argument('--top', type=int, default=10, help='Number of top picks')
    args = parser.parse_args()
    
    generator = FinalReportGenerator()
    top_picks = generator.run(top_n=args.top)
    
    if top_picks:
        print(f"\n📊 Final Top {args.top} Report Generated")
        print(f"   Average Final Score: {sum(p['final_score'] for p in top_picks) / len(top_picks):.1f}")
        print(f"\n🏆 Top 5 Picks:")
        for pick in top_picks[:5]:
            print(f"   {pick['rank']}. {pick['ticker']} ({pick['name']}) - "
                  f"Final: {pick['final_score']:.1f} | "
                  f"Quant: {pick['quant_score']:.1f} | "
                  f"AI: {pick['ai_recommendation']}")


if __name__ == "__main__":
    main()

