#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data File Verification Script
데이터 파일 생성 및 내용 검증
"""

import sys
from pathlib import Path
import json
import pandas as pd

# Import core config
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.config import (
    DATA_RAW_DIR,
    DATA_PROCESSED_DIR,
    PRICES_FILE,
    STOCKS_LIST_FILE,
    VOLUME_ANALYSIS_FILE,
    HOLDINGS_FILE,
    ETF_FLOWS_FILE,
    SMART_MONEY_PICKS_FILE,
    SECTOR_HEATMAP_FILE,
    OPTIONS_FLOW_FILE,
    INSIDER_MOVES_FILE,
    PORTFOLIO_RISK_FILE,
    MACRO_ANALYSIS_FILE,
    MACRO_ANALYSIS_EN_FILE,
    AI_SUMMARIES_FILE,
    FINAL_REPORT_FILE,
    SMART_MONEY_CURRENT_FILE,
    WEEKLY_CALENDAR_FILE,
    ETF_FLOW_ANALYSIS_FILE
)

def verify_file(file_path: Path, file_type: str = 'csv') -> tuple[bool, str]:
    """
    파일 존재 및 내용 검증
    
    Args:
        file_path: 파일 경로
        file_type: 파일 타입 ('csv', 'json')
    
    Returns:
        (성공 여부, 메시지)
    """
    if not file_path.exists():
        return False, f"❌ 파일 없음: {file_path.name}"
    
    try:
        if file_type == 'csv':
            df = pd.read_csv(file_path)
            if df.empty:
                return False, f"⚠️  파일 비어있음: {file_path.name}"
            return True, f"✅ {file_path.name} ({len(df)} 행)"
        elif file_type == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not data:
                return False, f"⚠️  파일 비어있음: {file_path.name}"
            return True, f"✅ {file_path.name} (유효한 JSON)"
    except Exception as e:
        return False, f"❌ 파일 읽기 오류: {file_path.name} - {str(e)}"

def verify_part1():
    """Part 1 데이터 파일 검증"""
    print("\n" + "="*60)
    print("Part 1: 데이터 수집 검증")
    print("="*60)
    
    files_to_check = [
        (PRICES_FILE, 'csv'),
        (STOCKS_LIST_FILE, 'csv'),
        (VOLUME_ANALYSIS_FILE, 'csv'),
        (HOLDINGS_FILE, 'csv'),
        (ETF_FLOWS_FILE, 'csv'),
    ]
    
    all_ok = True
    for file_path, file_type in files_to_check:
        success, message = verify_file(file_path, file_type)
        print(f"  {message}")
        if not success:
            all_ok = False
    
    return all_ok

def verify_part2():
    """Part 2 데이터 파일 검증"""
    print("\n" + "="*60)
    print("Part 2: 분석 및 스크리닝 검증")
    print("="*60)
    
    files_to_check = [
        (SMART_MONEY_PICKS_FILE, 'csv'),
        (SECTOR_HEATMAP_FILE, 'json'),
        (OPTIONS_FLOW_FILE, 'json'),
        (INSIDER_MOVES_FILE, 'json'),
        (PORTFOLIO_RISK_FILE, 'json'),
    ]
    
    all_ok = True
    for file_path, file_type in files_to_check:
        success, message = verify_file(file_path, file_type)
        print(f"  {message}")
        if not success:
            all_ok = False
    
    # Smart Money Picks 상세 검증
    if SMART_MONEY_PICKS_FILE.exists():
        try:
            df = pd.read_csv(SMART_MONEY_PICKS_FILE)
            required_columns = ['ticker', 'composite_score', 'grade']
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                print(f"  ⚠️  필수 컬럼 누락: {', '.join(missing_cols)}")
                all_ok = False
            else:
                print(f"  ✅ Smart Money Picks 구조 검증 완료")
                print(f"     - 총 {len(df)}개 종목")
                print(f"     - 평균 점수: {df['composite_score'].mean():.1f}")
        except Exception as e:
            print(f"  ❌ Smart Money Picks 검증 오류: {e}")
            all_ok = False
    
    return all_ok

def verify_part3():
    """Part 3 데이터 파일 검증"""
    print("\n" + "="*60)
    print("Part 3: AI 분석 검증")
    print("="*60)
    
    files_to_check = [
        (MACRO_ANALYSIS_FILE, 'json'),
        (MACRO_ANALYSIS_EN_FILE, 'json'),
        (AI_SUMMARIES_FILE, 'json'),
        (FINAL_REPORT_FILE, 'json'),
        (SMART_MONEY_CURRENT_FILE, 'json'),
        (WEEKLY_CALENDAR_FILE, 'json'),
        (ETF_FLOW_ANALYSIS_FILE, 'json'),
    ]
    
    all_ok = True
    for file_path, file_type in files_to_check:
        success, message = verify_file(file_path, file_type)
        print(f"  {message}")
        if not success:
            all_ok = False
    
    # AI Summaries 상세 검증
    if AI_SUMMARIES_FILE.exists():
        try:
            with open(AI_SUMMARIES_FILE, 'r', encoding='utf-8') as f:
                summaries = json.load(f)
            print(f"  ✅ AI 요약: {len(summaries)}개 종목")
            for ticker, data in list(summaries.items())[:3]:
                has_ko = 'summary_ko' in data and data['summary_ko']
                has_en = 'summary_en' in data and data['summary_en']
                print(f"     - {ticker}: KO={has_ko}, EN={has_en}")
        except Exception as e:
            print(f"  ❌ AI Summaries 검증 오류: {e}")
            all_ok = False
    
    return all_ok

def main():
    """메인 검증 실행"""
    print("="*60)
    print("데이터 파일 검증 스크립트")
    print("="*60)
    
    results = {
        'Part 1': verify_part1(),
        'Part 2': verify_part2(),
        'Part 3': verify_part3(),
    }
    
    print("\n" + "="*60)
    print("검증 결과 요약")
    print("="*60)
    
    all_passed = True
    for part, passed in results.items():
        status = "✅ 통과" if passed else "❌ 실패"
        print(f"  {part}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ 모든 검증 통과!")
        return 0
    else:
        print("❌ 일부 검증 실패. 위의 오류를 확인하세요.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

