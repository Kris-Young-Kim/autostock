#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Endpoint Verification Script
API 엔드포인트 동작 검증
"""

import sys
import requests
import json
from pathlib import Path
from typing import Dict, List

# Import core config
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.config import PORT

BASE_URL = f"http://localhost:{PORT}"

def test_endpoint(endpoint: str, method: str = 'GET', data: Dict = None) -> tuple[bool, str]:
    """
    API 엔드포인트 테스트
    
    Args:
        endpoint: API 엔드포인트 경로
        method: HTTP 메서드
        data: POST 데이터
    
    Returns:
        (성공 여부, 메시지)
    """
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        else:
            return False, f"지원하지 않는 메서드: {method}"
        
        if response.status_code == 200:
            try:
                data = response.json()
                return True, f"✅ {endpoint} (상태: {response.status_code})"
            except:
                return True, f"✅ {endpoint} (상태: {response.status_code}, 비JSON 응답)"
        else:
            return False, f"❌ {endpoint} (상태: {response.status_code})"
    
    except requests.exceptions.ConnectionError:
        return False, f"❌ {endpoint} (서버 연결 실패 - 서버가 실행 중인지 확인하세요)"
    except requests.exceptions.Timeout:
        return False, f"❌ {endpoint} (타임아웃)"
    except Exception as e:
        return False, f"❌ {endpoint} (오류: {str(e)})"

def verify_api_endpoints():
    """모든 API 엔드포인트 검증"""
    print("\n" + "="*60)
    print("API 엔드포인트 검증")
    print("="*60)
    print(f"서버 URL: {BASE_URL}")
    print()
    
    endpoints = [
        # 기본 엔드포인트
        ('/', 'GET'),
        ('/api/us/portfolio', 'GET'),
        ('/api/us/smart-money', 'GET'),
        ('/api/us/etf-flows', 'GET'),
        ('/api/us/sector-heatmap', 'GET'),
        ('/api/us/options-flow', 'GET'),
        ('/api/us/macro', 'GET'),
        ('/api/us/calendar', 'GET'),
        ('/api/us/history-dates', 'GET'),
        
        # 파라미터가 필요한 엔드포인트
        ('/api/us/stock-chart/AAPL?period=6mo', 'GET'),
        ('/api/us/stock-info/AAPL', 'GET'),
        ('/api/us/technical-indicators/AAPL', 'GET'),
        ('/api/us/ai-summary/AAPL?lang=ko', 'GET'),
        ('/api/us/macro-analysis?lang=ko&model=gemini', 'GET'),
        
        # POST 엔드포인트
        ('/api/realtime-prices', 'POST', {'tickers': ['AAPL', 'MSFT', 'GOOGL']}),
    ]
    
    results = []
    for endpoint_info in endpoints:
        if len(endpoint_info) == 2:
            endpoint, method = endpoint_info
            data = None
        else:
            endpoint, method, data = endpoint_info
        
        success, message = test_endpoint(endpoint, method, data)
        print(f"  {message}")
        results.append(success)
    
    return all(results)

def main():
    """메인 검증 실행"""
    print("="*60)
    print("API 엔드포인트 검증 스크립트")
    print("="*60)
    print("\n⚠️  주의: Flask 서버가 실행 중이어야 합니다.")
    print(f"   서버 시작: python web/app.py")
    print()
    
    try:
        passed = verify_api_endpoints()
        
        print("\n" + "="*60)
        if passed:
            print("✅ 모든 API 엔드포인트 검증 통과!")
            return 0
        else:
            print("❌ 일부 API 엔드포인트 검증 실패.")
            print("   서버 로그를 확인하거나 서버가 실행 중인지 확인하세요.")
            return 1
    except KeyboardInterrupt:
        print("\n\n검증 중단됨")
        return 1

if __name__ == '__main__':
    sys.exit(main())

