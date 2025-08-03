#!/usr/bin/env python3
"""
최종 예약 체크 도구 - 수동 확인용
"""
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def send_alert(message):
    """즉시 알림"""
    try:
        # 시스템 알림
        script = f'display notification "{message}" with title "🏥 마일스톤 소아과" sound name "Sosumi"'
        subprocess.run(['osascript', '-e', script])
        
        # 팝업
        popup_script = f'display dialog "{message}" with title "🏥 예약 알림" buttons {{"확인"}} default button "확인"'
        subprocess.run(['osascript', '-e', popup_script])
        
        # 소리
        subprocess.run(['afplay', '/System/Library/Sounds/Sosumi.aiff'])
        subprocess.run(['say', '예약 가능합니다'])
        
        print(f"🔔 알림 전송: {message}")
    except Exception as e:
        print(f"📢 {message}")

def check_now():
    """지금 당장 예약 상태 확인"""
    options = Options()
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    
    try:
        url = "https://m.booking.naver.com/booking/13/bizes/635057/items/4867274?lang=ko&service-target=map-pc&startDate=2025-08-01&theme=place"
        print("🚀 예약 페이지 접속 중...")
        driver.get(url)
        time.sleep(10)
        
        # 정확한 calendar_date 버튼 기반 감지
        calendar_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'calendar_date')]")
        available_dates = []
        
        print("🔍 달력 버튼 분석:")
        for btn in calendar_buttons:
            try:
                text = btn.text.strip().split('\n')[0]  # 첫 번째 줄만 (날짜)
                classes = btn.get_attribute('class') or ""
                is_enabled = btn.is_enabled()
                
                if text.isdigit() and 1 <= int(text) <= 31:
                    print(f"  날짜: {text}")
                    print(f"    클래스: {classes}")
                    print(f"    활성화: {is_enabled}")
                    
                    # 핵심 로직: 글자 색상으로 활성화 상태 구분
                    # 검은 글씨만 예약 가능, 회색 글씨는 마감
                    
                    # span.num 요소의 색상 확인
                    try:
                        span_elem = btn.find_element(By.XPATH, ".//span[@class='num']")
                        text_color = span_elem.value_of_css_property("color")
                        
                        print(f"    글자 색상: {text_color}")
                        
                        # 검은 글씨 색상 범위 (RGB 값으로 판단)
                        # rgba(34, 34, 37, 1) 또는 비슷한 어두운 색상이 검은 글씨
                        if ('rgb(34, 34, 37)' in text_color or 
                            'rgba(34, 34, 37' in text_color or
                            'rgb(0, 0, 0)' in text_color or
                            'rgba(0, 0, 0' in text_color):
                            
                            # 추가 조건: unselectable이 없어야 함
                            if 'unselectable' not in classes:
                                available_dates.append(text)
                                print(f"    ✅ 예약 가능! (검은 글씨)")
                            else:
                                print(f"    ❌ 예약 불가 (unselectable)")
                        else:
                            print(f"    ❌ 예약 불가 (회색 글씨 - 마감)")
                            
                    except Exception as e:
                        print(f"    ❌ 색상 확인 실패: {e}")
                        # 색상 확인 실패시 기존 로직 사용
                        if ('calendar_date' in classes and 
                            'unselectable' not in classes and 
                            'dayoff' not in classes and
                            is_enabled):
                            available_dates.append(text)
                            print(f"    ✅ 예약 가능! (기본 로직)")
                        else:
                            print(f"    ❌ 예약 불가 (기본 로직)")
                    print()
            except Exception as e:
                continue
        
        print(f"\n📅 최종 예약 가능 날짜: {available_dates}")
        
        # 2일과 6일 특별 확인
        if "2" in available_dates or "6" in available_dates:
            message = f"심층상담 예약 가능! 날짜: {', '.join(available_dates)}"
            print(f"🎉 {message}")
            send_alert(message)
            return True
        else:
            print("⏳ 아직 예약 불가능")
            return False
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🏥 마일스톤 소아과 예약 상태 확인")
    print("=" * 40)
    
    result = check_now()
    
    if result:
        print("\n🎊 예약 가능한 날짜가 있습니다!")
        print("지금 바로 예약하세요!")
    else:
        print("\n⏳ 현재 예약 불가능")
        print("나중에 다시 확인해보세요.")
    
    print("\n✅ 확인 완료!")
