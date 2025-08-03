#!/usr/bin/env python3
"""
정확한 URL에서 달력 요소 디버깅
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def debug_calendar():
    options = Options()
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    
    try:
        url = "https://m.booking.naver.com/booking/13/bizes/635057/items/4867274?lang=ko&service-target=map-pc&startDate=2025-08-01&theme=place"
        print(f"🚀 정확한 예약 URL 접속...")
        driver.get(url)
        
        print("⏳ 15초 대기 (충분한 로딩 시간)...")
        time.sleep(15)
        
        print(f"📍 현재 URL: {driver.current_url}")
        print(f"📄 페이지 제목: {driver.title}")
        
        # 페이지 소스에서 2, 6 검색
        page_source = driver.page_source
        if "2" in page_source and "6" in page_source:
            print("✅ 페이지 소스에 '2'와 '6' 발견!")
        
        # 모든 요소 타입별로 검색
        print("\n🔍 모든 요소에서 숫자 검색:")
        
        # 1. 모든 태그에서 검색
        all_elements = driver.find_elements(By.XPATH, "//*")
        found_dates = []
        
        for elem in all_elements:
            try:
                text = elem.text.strip()
                if text in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", 
                           "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                           "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"]:
                    
                    tag_name = elem.tag_name
                    classes = elem.get_attribute("class")
                    is_displayed = elem.is_displayed()
                    is_enabled = elem.is_enabled()
                    
                    print(f"  숫자 '{text}' | 태그: {tag_name} | 표시: {is_displayed} | 활성: {is_enabled}")
                    print(f"    클래스: {classes}")
                    
                    if text in ["2", "6"]:
                        print(f"    🎯 중요! {text}일 발견!")
                        found_dates.append(text)
                    print()
            except:
                continue
        
        print(f"\n📅 발견된 중요 날짜: {found_dates}")
        
        # 특별히 2일과 6일 클릭 가능한지 테스트
        if "2" in found_dates:
            try:
                date_2 = driver.find_element(By.XPATH, "//*[text()='2']")
                if date_2.is_enabled() and date_2.is_displayed():
                    print("✅ 2일 클릭 가능!")
                else:
                    print("⚠️ 2일 클릭 불가능")
            except:
                print("❌ 2일 요소 접근 실패")
        
        if "6" in found_dates:
            try:
                date_6 = driver.find_element(By.XPATH, "//*[text()='6']")
                if date_6.is_enabled() and date_6.is_displayed():
                    print("✅ 6일 클릭 가능!")
                else:
                    print("⚠️ 6일 클릭 불가능")
            except:
                print("❌ 6일 요소 접근 실패")
        
        print("\n💡 브라우저에서 실제 달력을 확인해보세요!")
        input("확인 후 Enter를 누르세요...")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_calendar()
