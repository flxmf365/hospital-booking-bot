#!/usr/bin/env python3
"""
안정적인 예약 알림 시스템 (GUI 오류 해결)
"""
import time
import subprocess
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """안정적인 드라이버 설정 (헤드리스 모드)"""
    options = Options()
    # 헤드리스 모드 - 브라우저 창이 보이지 않음
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    options.add_argument("--silent")
    return webdriver.Chrome(options=options)

def send_notification(title, message):
    """macOS 시스템 알림"""
    try:
        script = f'display notification "{message}" with title "{title}" sound name "Sosumi"'
        subprocess.run(['osascript', '-e', script])
        print(f"🔔 알림 전송: {message}")
    except Exception as e:
        print(f"📢 {message}")

def send_popup_notification(title, message):
    """AppleScript로 팝업 대화상자"""
    try:
        script = f'''
        display dialog "{message}" with title "{title}" buttons {{"확인"}} default button "확인" with icon note
        '''
        subprocess.run(['osascript', '-e', script])
        print(f"💬 팝업 전송: {message}")
    except Exception as e:
        print(f"❌ 팝업 실패: {e}")

def play_alert_sound():
    """알림음 재생"""
    try:
        subprocess.run(['afplay', '/System/Library/Sounds/Sosumi.aiff'])
        subprocess.run(['say', '예약 가능합니다! 지금 확인하세요!'])
    except:
        pass

def check_booking():
    """예약 가능 여부 체크"""
    driver = setup_driver()
    try:
        url = "https://m.booking.naver.com/booking/13/bizes/635057/items/4867274?lang=ko&service-target=map-pc&startDate=2025-08-01&theme=place"
        driver.get(url)
        time.sleep(8)  # 충분한 로딩 시간
        
        print(f"📍 페이지 접속: {driver.current_url}")
        
        # 정확한 날짜 요소 찾기 - span.num 클래스 사용
        date_elements = driver.find_elements(By.XPATH, "//span[@class='num']")
        available_dates = []
        
        for elem in date_elements:
            try:
                text = elem.text.strip()
                if text.isdigit() and 1 <= int(text) <= 31:
                    # 부모 버튼이 클릭 가능한지 확인
                    try:
                        parent_button = elem.find_element(By.XPATH, "../..")
                        if (parent_button.tag_name == 'button' and 
                            parent_button.is_enabled() and 
                            parent_button.is_displayed() and
                            'unselectable' not in parent_button.get_attribute('class')):
                            available_dates.append(text)
                    except:
                        # 부모 확인 실패시 기본적으로 포함
                        if elem.is_displayed():
                            available_dates.append(text)
            except:
                continue
        
        # 중복 제거
        available_dates = list(set(available_dates))
        
        # 시간 요소 찾기
        time_elements = driver.find_elements(By.XPATH, "//button[contains(text(), ':')]")
        available_times = []
        for elem in time_elements:
            if elem.is_displayed() and elem.is_enabled():
                available_times.append(elem.text.strip())
        
        return {
            'available': len(available_dates) > 0,
            'dates': available_dates,
            'times': available_times
        }
        
    except Exception as e:
        print(f"❌ 체크 오류: {e}")
        return {'available': False, 'dates': [], 'times': []}
    finally:
        driver.quit()

def monitor():
    """안정적인 모니터링"""
    print("🚀 마일스톤 소아과 예약 알림 시스템 시작!")
    print("📍 정확한 예약 페이지 모니터링 중...")
    print("🔔 예약 가능시 시스템 알림 + 팝업 + 소리!")
    
    last_status = False
    
    while True:
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"\n🔍 {current_time} - 예약 상태 체크 중...")
            
            result = check_booking()
            is_available = result['available']
            
            print(f"📅 발견된 날짜: {result['dates']}")
            print(f"⏰ 발견된 시간: {result['times']}")
            
            if is_available and not last_status:
                # 새로운 예약 슬롯 발견!
                dates_str = ', '.join(result['dates'][:5])
                message = f"심층상담 예약 가능! 날짜: {dates_str}"
                
                print(f"🎉 {current_time} - 예약 가능 발견!")
                
                # 다중 알림
                send_notification("🏥 마일스톤 소아과", message)
                send_popup_notification("🏥 예약 알림", f"{message}\n\n지금 바로 예약하세요!")
                play_alert_sound()
                
                last_status = True
                
            elif not is_available and last_status:
                print(f"⚠️ {current_time} - 예약 슬롯 없어짐")
                last_status = False
                
            elif is_available:
                print(f"✅ {current_time} - 예약 계속 가능")
                
            else:
                print(f"⏳ {current_time} - 예약 대기 중...")
            
            time.sleep(60)  # 1분마다 체크
            
        except KeyboardInterrupt:
            print("\n👋 모니터링 종료")
            break
        except Exception as e:
            print(f"❌ 모니터링 오류: {e}")
            time.sleep(30)

if __name__ == "__main__":
    monitor()
