#!/usr/bin/env python3
"""
심층상담 예약 알림 시스템
"""
import time
import subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

def send_notification(title, message):
    """macOS 알림"""
    try:
        script = f'display notification "{message}" with title "{title}" sound name "Glass"'
        subprocess.run(['osascript', '-e', script])
        print(f"🔔 알림: {message}")
    except:
        print(f"📢 {message}")

def check_booking():
    """예약 가능 여부 체크"""
    driver = setup_driver()
    try:
        url = "https://m.booking.naver.com/booking/13/bizes/635057?theme=place&service-target=map-pc&lang=ko"
        driver.get(url)
        time.sleep(5)
        
        # 날짜 요소 찾기
        dates = driver.find_elements(By.XPATH, "//button[string-length(text()) <= 2 and not(@disabled)]")
        available_dates = [d.text for d in dates if d.is_displayed() and d.text.isdigit()]
        
        # 시간 요소 찾기  
        times = driver.find_elements(By.XPATH, "//button[contains(text(), ':') and not(@disabled)]")
        available_times = [t.text for t in times if t.is_displayed()]
        
        return len(available_dates) > 0 or len(available_times) > 0
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False
    finally:
        driver.quit()

def monitor():
    """지속 모니터링"""
    print("🚀 심층상담 예약 알림 시스템 시작!")
    print("📍 마일스톤소아청소년과의원 모니터링 중...")
    
    last_status = False
    
    while True:
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"🔍 {current_time} - 예약 상태 체크 중...")
            
            is_available = check_booking()
            
            if is_available and not last_status:
                # 새로운 예약 슬롯 발견!
                message = "심층상담 예약 가능합니다!"
                send_notification("🏥 마일스톤 소아과", message)
                print(f"🎉 {current_time} - {message}")
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
