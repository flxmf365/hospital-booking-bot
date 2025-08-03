#!/usr/bin/env python3
"""
즉시 예약 상태 확인 (브라우저 보이게)
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def instant_check():
    # 브라우저 보이게 설정
    options = Options()
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    
    try:
        url = "https://m.booking.naver.com/booking/13/bizes/635057?theme=place&service-target=map-pc&lang=ko"
        print(f"🚀 예약 페이지 접속...")
        driver.get(url)
        
        print("⏳ 페이지 로딩 대기 (10초)...")
        time.sleep(10)
        
        print(f"📍 현재 URL: {driver.current_url}")
        
        # 모든 텍스트 요소에서 숫자 찾기
        all_elements = driver.find_elements(By.XPATH, "//*[text()]")
        
        print("\n🔍 페이지에서 발견된 숫자들:")
        found_numbers = []
        for elem in all_elements:
            try:
                text = elem.text.strip()
                if text.isdigit() and 1 <= int(text) <= 31:
                    color = elem.value_of_css_property("color")
                    display = elem.is_displayed()
                    tag = elem.tag_name
                    classes = elem.get_attribute("class")
                    
                    print(f"  숫자 '{text}' | 태그: {tag} | 표시: {display}")
                    print(f"    색상: {color}")
                    print(f"    클래스: {classes}")
                    
                    # 휴무가 아닌 숫자들
                    parent_text = elem.find_element(By.XPATH, "..").text
                    if "휴무" not in parent_text and display:
                        found_numbers.append(text)
                        print(f"    ✅ 예약 가능 후보!")
                    print()
            except:
                continue
        
        print(f"\n📅 예약 가능한 날짜 후보: {list(set(found_numbers))}")
        
        # 2일과 6일 특별 확인
        if "2" in found_numbers:
            print("✅ 2일 발견!")
        if "6" in found_numbers:
            print("✅ 6일 발견!")
        
        print("\n💡 브라우저에서 직접 확인해보세요!")
        print("   2일과 6일이 실제로 클릭 가능한지 확인해주세요!")
        
        input("확인 후 Enter를 누르세요...")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    instant_check()
