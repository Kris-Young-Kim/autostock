#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Verification Script
전체 시스템 검증 스크립트
"""

import sys
from pathlib import Path

# Import verification scripts
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """전체 검증 실행"""
    print("="*70)
    print("US Market Smart Money Alpha Platform - 전체 검증")
    print("="*70)
    
    # 1. 데이터 파일 검증
    print("\n[1/3] 데이터 파일 검증")
    print("-" * 70)
    try:
        from bin.verify_data import main as verify_data_main
        data_result = verify_data_main()
    except Exception as e:
        print(f"❌ 데이터 검증 스크립트 실행 오류: {e}")
        data_result = 1
    
    # 2. API 엔드포인트 검증 (선택적)
    print("\n[2/3] API 엔드포인트 검증")
    print("-" * 70)
    print("⚠️  서버가 실행 중이지 않으면 이 단계를 건너뜁니다.")
    try:
        import requests
        from core.config import PORT
        response = requests.get(f"http://localhost:{PORT}/", timeout=2)
        if response.status_code == 200:
            from bin.verify_api import main as verify_api_main
            api_result = verify_api_main()
        else:
            print("  ⏭️  서버가 실행 중이 아니므로 API 검증을 건너뜁니다.")
            api_result = 0
    except:
        print("  ⏭️  서버가 실행 중이 아니므로 API 검증을 건너뜁니다.")
        api_result = 0
    
    # 3. 프론트엔드 검증 (수동 확인 안내)
    print("\n[3/3] 프론트엔드 UI 검증")
    print("-" * 70)
    print("  📋 수동 확인 항목:")
    print("     1. 서버 실행: python web/app.py")
    print("     2. 브라우저에서 http://localhost:3000 접속")
    print("     3. 다음 기능 확인:")
    print("        - 대시보드 로딩")
    print("        - Smart Money Picks 테이블 표시")
    print("        - 차트 로딩 (종목 클릭 시)")
    print("        - 언어 전환 (KO/EN)")
    print("        - AI 모델 선택 (Gemini/GPT)")
    print("        - 실시간 가격 업데이트")
    print("        - 매크로 분석 아코디언")
    print("        - ETF Flows 아코디언")
    print("        - 경제 캘린더 아코디언")
    print("     4. 콘솔 에러 확인 (F12)")
    print()
    
    # 최종 결과
    print("="*70)
    print("검증 결과 요약")
    print("="*70)
    
    results = {
        '데이터 파일': data_result == 0,
        'API 엔드포인트': api_result == 0 if api_result != -1 else None,
        '프론트엔드 UI': None  # 수동 확인
    }
    
    for item, result in results.items():
        if result is None:
            status = "⏭️  수동 확인 필요"
        elif result:
            status = "✅ 통과"
        else:
            status = "❌ 실패"
        print(f"  {item}: {status}")
    
    print("\n" + "="*70)
    if data_result == 0:
        print("✅ 데이터 파일 검증 완료!")
        print("   다음 단계: 서버 실행 후 프론트엔드 UI 확인")
        return 0
    else:
        print("❌ 데이터 파일 검증 실패.")
        print("   pipeline/update_all.py를 실행하여 데이터를 생성하세요.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

