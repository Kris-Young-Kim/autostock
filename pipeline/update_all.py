#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Pipeline Execution Script
Runs all Part 1 data collection and analysis scripts sequentially
"""

import sys
import subprocess
import time
import argparse
from pathlib import Path

# Import core config for logging
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.config import setup_logging

# Setup logging
logger = setup_logging('pipeline.log')

# Part 1 scripts (in execution order)
PART1_SCRIPTS = [
    ("01_collect_prices.py", "가격 데이터 수집", 600),
    ("02_analyze_volume.py", "거래량/수급 분석", 300),
    ("03_analyze_13f.py", "기관 보유 분석", 600),
    ("04_etf_flows.py", "ETF 자금 흐름 분석", 300),
]

# Scripts that include AI analysis (skipped in --quick mode)
AI_SCRIPTS = [
    "04_etf_flows.py",  # Has optional Gemini AI analysis
]


def run_script(script_name: str, description: str, timeout: int, skip_ai: bool = False) -> bool:
    """
    Run a single pipeline script
    
    Args:
        script_name: Name of the script file
        description: Human-readable description
        timeout: Maximum execution time in seconds
        skip_ai: Whether to skip AI analysis
        
    Returns:
        True if successful, False otherwise
    """
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        logger.error(f"❌ Script not found: {script_path}")
        return False
    
    logger.info(f"🚀 Running {description} ({script_name})...")
    start_time = time.time()
    
    try:
        # Build command
        cmd = [sys.executable, str(script_path)]
        
        # For ETF flows, we could add a --no-ai flag if needed
        # For now, AI is optional and controlled by API key presence
        
        # Run script
        result = subprocess.run(
            cmd,
            timeout=timeout,
            check=True,
            capture_output=False,  # Show output in real-time
            cwd=Path(__file__).parent.parent
        )
        
        elapsed = time.time() - start_time
        logger.info(f"✅ {description} completed in {elapsed:.1f} seconds")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"❌ {description} timed out after {timeout} seconds")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        logger.error(f"❌ {description} failed: {e}")
        return False


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description='Run all Part 1 data collection and analysis scripts'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Skip AI analysis (faster execution)'
    )
    parser.add_argument(
        '--script',
        type=str,
        help='Run only a specific script (e.g., 01_collect_prices.py)'
    )
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("🚀 Starting Part 1 Pipeline Execution")
    if args.quick:
        logger.info("⚡ Quick mode: AI analysis will be skipped")
    logger.info("=" * 60)
    
    overall_start = time.time()
    success_count = 0
    failed_scripts = []
    
    # Filter scripts if --script is specified
    scripts_to_run = PART1_SCRIPTS
    if args.script:
        scripts_to_run = [s for s in PART1_SCRIPTS if s[0] == args.script]
        if not scripts_to_run:
            logger.error(f"❌ Script not found: {args.script}")
            logger.info(f"Available scripts: {[s[0] for s in PART1_SCRIPTS]}")
            return 1
    
    # Run each script
    for script_name, description, timeout in scripts_to_run:
        # Skip AI scripts in quick mode
        if args.quick and script_name in AI_SCRIPTS:
            logger.info(f"⏭️  Skipping {description} (AI analysis in quick mode)")
            continue
        
        success = run_script(script_name, description, timeout, skip_ai=args.quick)
        
        if success:
            success_count += 1
        else:
            failed_scripts.append(script_name)
            # Continue with next script even if one fails
            logger.warning(f"⚠️  Continuing with next script...")
        
        # Small delay between scripts
        time.sleep(1)
    
    # Summary
    total_time = time.time() - overall_start
    logger.info("=" * 60)
    logger.info("📊 Pipeline Execution Summary")
    logger.info("=" * 60)
    logger.info(f"   Total scripts: {len(scripts_to_run)}")
    logger.info(f"   Successful: {success_count}")
    logger.info(f"   Failed: {len(failed_scripts)}")
    logger.info(f"   Total time: {total_time/60:.1f} minutes")
    
    if failed_scripts:
        logger.warning(f"   Failed scripts: {', '.join(failed_scripts)}")
        return 1
    
    logger.info("✅ All scripts completed successfully!")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

