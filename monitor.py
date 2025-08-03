#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 병원 예약 모니터링 도구 - 간단 버전
"""

import time
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class SimpleMonitor:
    def __init__(self):
        self.url = "https://map.naver.com/p/entry/place/1473484582"
        
    def setup_driver(self):
        """간단한 드라이버 설정"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=options)
        return True
        
    def check_availability(self):
        """예약 가능 여부 체크"""
        try:
            self.setup_driver()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 병원 페이지 확인 중...")
            
            self.driver.get(self.url)
            time.sleep(3)
            
            page_source = self.driver.page_source
            
            # 예약 관련 키워드 체크
            keywords = ["예약하기", "예약", "booking", "온라인예약"]
            found_keywords = [k for k in keywords if k in page_source]
            
            # 네이버 예약 링크 체크
            has_booking_link = "booking.naver.com" in page_source
            
            result = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "accessible": True,
                "keywords_found": found_keywords,
                "has_booking_system": has_booking_link,
                "status": "✅ 접근 가능" if found_keywords or has_booking_link else "⚠️ 예약 시스템 없음"
            }
            
            return result
            
        except Exception as e:
            return {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "accessible": False,
                "error": str(e),
                "status": "❌ 접근 실패"
            }
        finally:
            if hasattr(self, 'driver'):
                self.driver.quit()
    
    def monitor_continuously(self, interval_minutes=5):
        """지속적 모니터링"""
        print("=== 네이버 병원 예약 모니터링 시작 ===")
        print(f"체크 간격: {interval_minutes}분")
        print("종료하려면 Ctrl+C를 누르세요\n")
        
        try:
            while True:
                result = self.check_availability()
                
                print(f"[{result['time']}] {result['status']}")
                if result['accessible']:
                    if result.get('keywords_found'):
                        print(f"  📋 발견된 키워드: {', '.join(result['keywords_found'])}")
                    if result.get('has_booking_system'):
                        print("  🔗 네이버 예약 시스템 발견!")
                else:
                    print(f"  ❌ 오류: {result.get('error', '알 수 없는 오류')}")
                
                print("-" * 50)
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n모니터링을 종료합니다.")

if __name__ == "__main__":
    monitor = SimpleMonitor()
    
    print("1. 한 번만 체크")
    print("2. 지속적 모니터링")
    choice = input("선택하세요 (1/2): ").strip()
    
    if choice == "1":
        result = monitor.check_availability()
        print(f"\n{result['status']}")
        if result['accessible']:
            print(f"키워드: {result.get('keywords_found', [])}")
            print(f"예약 시스템: {'있음' if result.get('has_booking_system') else '없음'}")
    else:
        interval = input("체크 간격(분, 기본값 5): ").strip()
        interval = int(interval) if interval.isdigit() else 5
        monitor.monitor_continuously(interval)
