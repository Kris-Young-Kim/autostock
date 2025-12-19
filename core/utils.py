#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common Utilities for Error Handling
전역 예외 핸들러, Retry 로직, Rate Limiting 등 공통 유틸리티
"""

import time
import random
import logging
from functools import wraps
from typing import Callable, TypeVar, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RateLimiter:
    """Rate Limiting을 위한 클래스"""
    
    def __init__(self, max_calls: int, period: float):
        """
        Args:
            max_calls: 기간 내 최대 호출 횟수
            period: 기간 (초)
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []
    
    def wait_if_needed(self):
        """필요시 대기"""
        now = time.time()
        
        # 기간이 지난 호출 기록 제거
        self.calls = [call_time for call_time in self.calls if now - call_time < self.period]
        
        # 최대 호출 횟수 초과 시 대기
        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            if sleep_time > 0:
                logger.debug(f"Rate limit reached, waiting {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
                # 대기 후 다시 정리
                self.calls = [call_time for call_time in self.calls if time.time() - call_time < self.period]
        
        # 현재 호출 기록
        self.calls.append(time.time())


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Exception, ...] = (Exception,)
):
    """
    Exponential Backoff를 사용한 Retry 데코레이터
    
    Args:
        max_retries: 최대 재시도 횟수
        base_delay: 기본 대기 시간 (초)
        max_delay: 최대 대기 시간 (초)
        exponential_base: 지수 증가 베이스
        jitter: 랜덤 지터 추가 여부
        exceptions: 재시도할 예외 타입들
    
    Example:
        @retry_with_backoff(max_retries=3, base_delay=1.0)
        def fetch_data():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise
                    
                    # Exponential backoff 계산
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    # Jitter 추가 (랜덤성으로 동시 재시도 방지)
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    time.sleep(delay)
            
            # 이론적으로 도달하지 않지만 타입 체커를 위해
            raise last_exception
        
        return wrapper
    return decorator


def safe_execute(
    func: Callable[..., T],
    default: Optional[T] = None,
    log_error: bool = True,
    *args,
    **kwargs
) -> Optional[T]:
    """
    안전하게 함수 실행 (예외 발생 시 기본값 반환)
    
    Args:
        func: 실행할 함수
        default: 예외 발생 시 반환할 기본값
        log_error: 에러 로깅 여부
        *args, **kwargs: 함수에 전달할 인자들
    
    Returns:
        함수 실행 결과 또는 기본값
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_error:
            logger.error(f"Error executing {func.__name__}: {e}", exc_info=True)
        return default


class GlobalExceptionHandler:
    """전역 예외 핸들러"""
    
    @staticmethod
    def handle_api_error(error: Exception, context: str = "") -> dict:
        """
        API 에러 처리
        
        Args:
            error: 발생한 예외
            context: 에러 컨텍스트
        
        Returns:
            에러 정보 딕셔너리
        """
        error_info = {
            'error': str(error),
            'type': type(error).__name__,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.error(f"API Error [{context}]: {error}", exc_info=True)
        
        return error_info
    
    @staticmethod
    def handle_network_error(error: Exception, context: str = "") -> dict:
        """
        네트워크 에러 처리
        
        Args:
            error: 발생한 예외
            context: 에러 컨텍스트
        
        Returns:
            에러 정보 딕셔너리
        """
        error_info = {
            'error': 'Network error occurred',
            'type': type(error).__name__,
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'details': str(error)
        }
        
        logger.error(f"Network Error [{context}]: {error}", exc_info=True)
        
        return error_info
    
    @staticmethod
    def handle_data_error(error: Exception, context: str = "") -> dict:
        """
        데이터 처리 에러 처리
        
        Args:
            error: 발생한 예외
            context: 에러 컨텍스트
        
        Returns:
            에러 정보 딕셔너리
        """
        error_info = {
            'error': 'Data processing error occurred',
            'type': type(error).__name__,
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'details': str(error)
        }
        
        logger.error(f"Data Error [{context}]: {error}", exc_info=True)
        
        return error_info


# 전역 Rate Limiter 인스턴스들
yfinance_rate_limiter = RateLimiter(max_calls=10, period=1.0)  # 1초에 10회
api_rate_limiter = RateLimiter(max_calls=5, period=1.0)  # 1초에 5회
ai_api_rate_limiter = RateLimiter(max_calls=2, period=1.0)  # 1초에 2회 (AI API는 더 제한적)

