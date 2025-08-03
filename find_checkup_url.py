#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
국가 영유아검진 예약 URL 찾기 스크립트
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_checkup_booking_url():
    """국가 영유아검진 예약 URL 찾기"""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # 병원 페이지로 이동
        hospital_url = "https://map.naver.com/p/entry/place/1473484582"
        driver.get(hospital_url)
        time.sleep(5)
        
        print(f"현재 URL: {driver.current_url}")
        print(f"페이지 제목: {driver.title}")
        
        # 예약 관련 버튼들 찾기
        booking_keywords = [
            "영유아검진", "국가검진", "건강검진", "예약하기", "예약", 
            "진료예약", "검진예약", "온라인예약"
        ]
        
        found_elements = []
        
        for keyword in booking_keywords:
            try:
                # 텍스트로 요소 찾기
                elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
                for element in elements:
                    if element.is_displayed():
                        text = element.text.strip()
                        tag = element.tag_name
                        href = element.get_attribute('href')
                        onclick = element.get_attribute('onclick')
                        
                        found_elements.append({
                            'keyword': keyword,
                            'text': text,
                            'tag': tag,
                            'href': href,
                            'onclick': onclick
                        })
                        
                        print(f"\n✅ 발견: '{keyword}'")
                        print(f"   텍스트: {text}")
                        print(f"   태그: {tag}")
                        if href:
                            print(f"   링크: {href}")
                        if onclick:
                            print(f"   클릭이벤트: {onclick}")
                            
            except Exception as e:
                continue
        
        # 네이버 예약 시스템 링크 패턴 찾기
        print("\n=== 네이버 예약 링크 패턴 검색 ===")
        
        # 페이지 소스에서 booking.naver.com 링크 찾기
        page_source = driver.page_source
        
        import re
        booking_urls = re.findall(r'https://[^"]*booking\.naver\.com[^"]*', page_source)
        
        if booking_urls:
            print(f"\n📍 발견된 예약 URL들:")
            for i, url in enumerate(set(booking_urls), 1):
                # URL 디코딩
                import urllib.parse
                decoded_url = urllib.parse.unquote(url)
                print(f"{i}. {decoded_url}")
                
                # 영유아검진 관련 키워드가 있는지 확인
                checkup_keywords = ['checkup', 'examination', 'health', '검진', '영유아']
                for ck in checkup_keywords:
                    if ck.lower() in decoded_url.lower():
                        print(f"   ⭐ 검진 관련 키워드 '{ck}' 포함!")
        else:
            print("❌ 네이버 예약 링크를 찾을 수 없습니다.")
            
        # 직접 클릭해서 예약 페이지 접근 시도
        print("\n=== 예약 버튼 클릭 시도 ===")
        
        reservation_selectors = [
            "//button[contains(text(), '예약')]",
            "//a[contains(text(), '예약')]",
            "//*[contains(@class, 'booking')]",
            "//*[contains(@class, 'reservation')]"
        ]
        
        for selector in reservation_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"예약 버튼 발견: {element.text}")
                        
                        # 클릭해보기
                        try:
                            driver.execute_script("arguments[0].click();", element)
                            time.sleep(3)
                            
                            # 새 창이나 페이지 변화 확인
                            if len(driver.window_handles) > 1:
                                driver.switch_to.window(driver.window_handles[-1])
                                print(f"새 창 URL: {driver.current_url}")
                                
                                # 영유아검진 관련 요소 찾기
                                checkup_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '영유아') or contains(text(), '검진')]")
                                if checkup_elements:
                                    print("✅ 영유아검진 관련 페이지 발견!")
                                    for ce in checkup_elements[:5]:
                                        if ce.is_displayed():
                                            print(f"   - {ce.text}")
                                
                                return driver.current_url
                            elif "booking" in driver.current_url:
                                print(f"예약 페이지로 이동: {driver.current_url}")
                                return driver.current_url
                                
                        except Exception as e:
                            print(f"클릭 실패: {e}")
                            continue
                            
            except Exception as e:
                continue
        
        return None
        
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        return None
    finally:
        input("브라우저를 닫으려면 Enter를 눌러주세요...")
        driver.quit()

if __name__ == "__main__":
    print("=== 국가 영유아검진 예약 URL 찾기 ===")
    url = find_checkup_booking_url()
    
    if url:
        print(f"\n🎯 발견된 예약 URL: {url}")
    else:
        print("\n❌ 예약 URL을 찾을 수 없습니다.")
