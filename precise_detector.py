#!/usr/bin/env python3
"""
2일과 6일의 정확한 HTML 구조 분석
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def analyze_specific_dates():
    options = Options()
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    
    try:
        url = "https://m.booking.naver.com/booking/13/bizes/635057/items/4867274?lang=ko&service-target=map-pc&startDate=2025-08-01&theme=place"
        print("🚀 예약 페이지 접속...")
        driver.get(url)
        time.sleep(10)
        
        print("🔍 2일과 6일의 정확한 구조 분석...")
        
        # 2일과 6일 요소 찾기
        target_dates = ["2", "6"]
        
        for date in target_dates:
            print(f"\n📅 {date}일 분석:")
            
            # 해당 날짜의 모든 요소 찾기
            date_elements = driver.find_elements(By.XPATH, f"//*[text()='{date}']")
            
            for i, elem in enumerate(date_elements):
                try:
                    print(f"  요소 {i+1}:")
                    print(f"    태그: {elem.tag_name}")
                    print(f"    클래스: {elem.get_attribute('class')}")
                    print(f"    ID: {elem.get_attribute('id')}")
                    print(f"    표시: {elem.is_displayed()}")
                    print(f"    활성화: {elem.is_enabled()}")
                    
                    # 부모 요소들 확인
                    try:
                        parent1 = elem.find_element(By.XPATH, "..")
                        print(f"    부모1 태그: {parent1.tag_name}")
                        print(f"    부모1 클래스: {parent1.get_attribute('class')}")
                        print(f"    부모1 활성화: {parent1.is_enabled()}")
                        
                        parent2 = parent1.find_element(By.XPATH, "..")
                        print(f"    부모2 태그: {parent2.tag_name}")
                        print(f"    부모2 클래스: {parent2.get_attribute('class')}")
                        print(f"    부모2 활성화: {parent2.is_enabled()}")
                        
                        # CSS 스타일 확인
                        color = elem.value_of_css_property("color")
                        bg_color = elem.value_of_css_property("background-color")
                        cursor = elem.value_of_css_property("cursor")
                        
                        print(f"    색상: {color}")
                        print(f"    배경색: {bg_color}")
                        print(f"    커서: {cursor}")
                        
                        # 클릭 가능성 테스트
                        if parent2.tag_name == 'button':
                            onclick = parent2.get_attribute('onclick')
                            data_attrs = [attr for attr in parent2.get_attribute('outerHTML').split() if 'data-' in attr]
                            print(f"    onclick: {onclick}")
                            print(f"    data 속성들: {data_attrs}")
                        
                    except Exception as e:
                        print(f"    부모 요소 분석 실패: {e}")
                    
                    print()
                    
                except Exception as e:
                    print(f"  요소 분석 실패: {e}")
        
        # 전체 달력 구조 확인
        print("\n🗓️ 전체 달력 구조 분석:")
        calendar_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'calendar')]")
        print(f"달력 버튼 총 {len(calendar_buttons)}개 발견")
        
        for i, btn in enumerate(calendar_buttons[:10]):  # 처음 10개만
            try:
                text = btn.text.strip()
                classes = btn.get_attribute('class')
                enabled = btn.is_enabled()
                print(f"  버튼 {i+1}: '{text}' | 클래스: {classes} | 활성화: {enabled}")
            except:
                continue
        
        print("\n💡 브라우저에서 2일과 6일을 직접 확인해보세요!")
        print("실제로 클릭 가능한지 테스트해보고 알려주세요!")
        input("확인 후 Enter를 누르세요...")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    analyze_specific_dates()
