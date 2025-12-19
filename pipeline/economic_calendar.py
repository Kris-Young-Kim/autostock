#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Economic Calendar
Collects major economic events and provides AI impact analysis
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Import core config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import (
    setup_logging,
    WEEKLY_CALENDAR_FILE,
    GOOGLE_API_KEY
)

# Setup logging
logger = setup_logging('pipeline.log')


class EconomicCalendar:
    """Economic calendar collector and analyzer"""
    
    def __init__(self):
        self.output_file = WEEKLY_CALENDAR_FILE
        
        # Major economic events (can be expanded)
        self.major_events = [
            {
                'event': 'FOMC Interest Rate Decision',
                'impact': 'High',
                'description': 'Federal Reserve interest rate decision and policy statement',
                'typical_date': 'First Wednesday of month'  # Example pattern
            },
            {
                'event': 'Non-Farm Payrolls (NFP)',
                'impact': 'High',
                'description': 'US employment report - key labor market indicator',
                'typical_date': 'First Friday of month'
            },
            {
                'event': 'CPI (Consumer Price Index)',
                'impact': 'High',
                'description': 'Inflation data - key indicator for Fed policy',
                'typical_date': 'Around 10th-15th of month'
            },
            {
                'event': 'GDP Release',
                'impact': 'High',
                'description': 'Gross Domestic Product growth data',
                'typical_date': 'End of quarter'
            },
            {
                'event': 'PCE Price Index',
                'impact': 'Medium',
                'description': 'Personal Consumption Expenditures - Fed\'s preferred inflation measure',
                'typical_date': 'End of month'
            }
        ]
    
    def get_upcoming_events(self, days_ahead: int = 7) -> List[Dict]:
        """
        Get upcoming economic events
        
        Args:
            days_ahead: Number of days ahead to look for events
            
        Returns:
            List of economic events
        """
        logger.info(f"📅 Collecting economic events for next {days_ahead} days...")
        
        events = []
        today = datetime.now()
        end_date = today + timedelta(days=days_ahead)
        
        # Try to scrape from Yahoo Finance (simplified approach)
        # Note: Yahoo Finance scraping may be unreliable, so we use manual events as fallback
        try:
            url = "https://finance.yahoo.com/calendar/economic"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                try:
                    import pandas as pd
                    from io import StringIO
                    
                    # Try to parse HTML tables
                    dfs = pd.read_html(StringIO(resp.text))
                    if dfs:
                        for df in dfs:
                            # Look for US events
                            if 'Country' in df.columns or 'Event' in df.columns:
                                us_events = df[df.get('Country', df.get('Country/Region', '')) == 'US']
                                if not us_events.empty:
                                    for _, row in us_events.iterrows():
                                        event_name = row.get('Event', row.get('Name', ''))
                                        if event_name:
                                            events.append({
                                                'date': today.strftime('%Y-%m-%d'),  # Use today as placeholder
                                                'event': str(event_name),
                                                'impact': self._determine_impact(event_name),
                                                'description': f"Economic indicator release",
                                                'source': 'Yahoo Finance'
                                            })
                except Exception as e:
                    logger.debug(f"Error parsing Yahoo Finance calendar: {e}")
        except Exception as e:
            logger.debug(f"Error fetching Yahoo Finance calendar: {e}")
        
        # Add manual major events (fallback and important events)
        # Distribute events evenly across the time period
        num_manual_events = len(self.major_events)
        if num_manual_events > 0 and days_ahead > 0:
            # Calculate spacing between events
            spacing = max(1, days_ahead // num_manual_events)
            
            for idx, event_template in enumerate(self.major_events):
                # Distribute events evenly: first event on day 1, second on day 1+spacing, etc.
                event_day = min(idx * spacing + 1, days_ahead)
                event_date = today + timedelta(days=event_day)
                
                if event_date <= end_date:
                    events.append({
                        'date': event_date.strftime('%Y-%m-%d'),
                        'event': event_template['event'],
                        'impact': event_template['impact'],
                        'description': event_template['description'],
                        'source': 'Manual',
                        'note': 'Estimated date - verify actual schedule'
                    })
        
        # Remove duplicates
        seen_events = set()
        unique_events = []
        for event in events:
            event_key = (event['event'], event['date'])
            if event_key not in seen_events:
                seen_events.add(event_key)
                unique_events.append(event)
        
        logger.info(f"✅ Collected {len(unique_events)} economic events")
        return unique_events
    
    def _determine_impact(self, event_name: str) -> str:
        """Determine impact level based on event name"""
        event_lower = event_name.lower()
        
        high_impact_keywords = [
            'fomc', 'fed', 'interest rate', 'nfp', 'non-farm payroll',
            'cpi', 'gdp', 'unemployment', 'inflation'
        ]
        
        medium_impact_keywords = [
            'retail sales', 'pmi', 'consumer confidence', 'housing',
            'pce', 'durable goods', 'trade balance'
        ]
        
        if any(keyword in event_lower for keyword in high_impact_keywords):
            return 'High'
        elif any(keyword in event_lower for keyword in medium_impact_keywords):
            return 'Medium'
        else:
            return 'Low'
    
    def enrich_with_ai(self, events: List[Dict]) -> List[Dict]:
        """
        Enrich high-impact events with AI analysis
        
        Args:
            events: List of economic events
            
        Returns:
            List of events with AI analysis added
        """
        if not GOOGLE_API_KEY:
            logger.warning("Google API key not found. Skipping AI enrichment.")
            return events
        
        logger.info("🤖 Enriching high-impact events with AI analysis...")
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            for event in events:
                if event.get('impact') == 'High':
                    try:
                        prompt = f"""Explain the potential market impact of this economic event in 2-3 sentences:
Event: {event['event']}
Description: {event.get('description', '')}

Focus on:
1. How this event typically affects stock markets
2. Key indicators to watch
3. Potential market reaction

Be concise and practical."""
                        
                        response = model.generate_content(prompt)
                        
                        # Handle response safely
                        if hasattr(response, 'is_blocked') and response.is_blocked:
                            logger.warning(f"Content blocked for {event['event']}")
                            event['ai_analysis'] = "Analysis blocked by safety filters"
                        elif hasattr(response, 'text') and response.text:
                            event['ai_analysis'] = response.text.strip()
                        elif hasattr(response, 'candidates') and response.candidates:
                            candidate = response.candidates[0]
                            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                                text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                                if text_parts:
                                    event['ai_analysis'] = ''.join(text_parts).strip()
                                else:
                                    event['ai_analysis'] = "No analysis generated"
                            else:
                                event['ai_analysis'] = "Invalid response structure"
                        else:
                            event['ai_analysis'] = "No response generated"
                        
                        time.sleep(0.5)  # Rate limiting
                        
                    except Exception as e:
                        logger.debug(f"Error generating AI analysis for {event['event']}: {e}")
                        event['ai_analysis'] = f"Analysis failed: {str(e)}"
            
            logger.info("✅ AI enrichment complete")
            
        except ImportError:
            logger.warning("google-generativeai not installed. Skipping AI enrichment.")
        except Exception as e:
            logger.error(f"Error in AI enrichment: {e}")
        
        return events
    
    def run(self, days_ahead: int = 7) -> Dict:
        """Main execution"""
        logger.info("🚀 Starting Economic Calendar Collection...")
        
        # Get events
        events = self.get_upcoming_events(days_ahead)
        
        # Enrich with AI
        events = self.enrich_with_ai(events)
        
        # Prepare output
        output = {
            'timestamp': datetime.now().isoformat(),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'week_start': datetime.now().strftime('%Y-%m-%d'),
            'days_ahead': days_ahead,
            'total_events': len(events),
            'high_impact_count': sum(1 for e in events if e.get('impact') == 'High'),
            'events': events
        }
        
        # Save to file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Saved to {self.output_file}")
        logger.info(f"📊 Total events: {len(events)} (High impact: {output['high_impact_count']})")
        
        return output


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Economic Calendar')
    parser.add_argument('--days', type=int, default=7, help='Number of days ahead to look for events')
    args = parser.parse_args()
    
    calendar = EconomicCalendar()
    results = calendar.run(days_ahead=args.days)
    
    if results:
        print(f"\n📅 Economic Calendar Generated")
        print(f"   Total events: {results['total_events']}")
        print(f"   High impact: {results['high_impact_count']}")
        
        # Show high impact events
        high_impact = [e for e in results['events'] if e.get('impact') == 'High']
        if high_impact:
            print(f"\n🔥 High Impact Events:")
            for event in high_impact[:5]:
                print(f"   - {event['event']} ({event['date']})")


if __name__ == "__main__":
    main()

