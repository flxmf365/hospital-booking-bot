#!/usr/bin/env python3
"""
국가 영유아 검진 예약 모니터링 시스템
마일스톤소아청소년과의원 - 생후 4개월 이상
"""

import time
import subprocess
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# 텔레그램 설정 가져오기
try:
    from telegram_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, is_telegram_configured
except ImportError:
    TELEGRAM_BOT_TOKEN = None
    TELEGRAM_CHAT_ID = None
    def is_telegram_configured():
        return False

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

def send_telegram_message(message):
    """텔레그램 메시지 전송"""
    if not is_telegram_configured():
        print("⚠️ 텔레그램이 설정되지 않았습니다.")
        return False
        
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("📱 텔레그램 메시지 전송 성공")
            return True
        else:
            print(f"❌ 텔레그램 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 텔레그램 전송 오류: {e}")
        return False

def send_notification(title, message):
    """macOS 시스템 알림 전송"""
    try:
        script = f'''
        display notification "{message}" with title "{title}" sound name "Sosumi"
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        print(f"🔔 시스템 알림 전송: {message}")
    except Exception as e:
        print(f"❌ 알림 전송 실패: {e}")

def send_popup_alert(message):
    """팝업 대화상자 표시"""
    try:
        script = f'''
        display dialog "{message}" with title "🏥 마일스톤 소아과 - 영유아 검진" buttons {{"확인"}} default button "확인" with icon note
        '''
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, check=True)
        print(f"💬 팝업 표시: {message}")
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ 팝업 표시 실패: {e}")
        return None

def play_alert_sound():
    """알림음 재생"""
    try:
        subprocess.run(['afplay', '/System/Library/Sounds/Sosumi.aiff'], check=False)
        subprocess.run(['say', '영유아 검진 예약 가능합니다'], check=False)
        print("🔊 알림음 재생 완료")
    except Exception as e:
        print(f"❌ 알림음 재생 실패: {e}")

def check_booking():
    """영유아 검진 예약 가능 여부 확인"""
    driver = None
    try:
        print("🌐 브라우저 시작...")
        driver = setup_driver()
        
        # 단축 URL을 통해 실제 예약 페이지로 이동
        print("📍 예약 페이지 접속 중...")
        driver.get("https://naver.me/5TQg0RuJ")
        
        # 페이지 로딩 대기
        time.sleep(5)
        
        # 실제 예약 URL로 리다이렉트되었는지 확인
        current_url = driver.current_url
        print(f"🔗 현재 URL: {current_url}")
        
        # booking.naver.com으로 리다이렉트되었는지 확인
        if "booking.naver.com" not in current_url:
            print("⚠️ 예약 페이지로 리다이렉트되지 않음")
            return {'available': False, 'dates': [], 'times': []}
        
        # 달력 날짜 버튼들 찾기
        print("📅 예약 날짜 확인 중...")
        wait = WebDriverWait(driver, 10)
        
        # 달력이 로드될 때까지 대기
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "calendar_date")))
        
        # 모든 달력 날짜 버튼 찾기
        date_buttons = driver.find_elements(By.CLASS_NAME, "calendar_date")
        
        available_dates = []
        
        print(f"📊 총 {len(date_buttons)}개의 날짜 버튼 발견")
        
        for button in date_buttons:
            try:
                # 날짜 텍스트 추출
                date_span = button.find_element(By.CLASS_NAME, "num")
                date_text = date_span.text.strip()
                
                # 버튼 클래스 확인
                button_classes = button.get_attribute("class")
                
                # 글자 색상 확인 (중요!)
                color = driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).color;", 
                    date_span
                )
                
                print(f"  날짜: {date_text}")
                print(f"    클래스: {button_classes}")
                print(f"    활성화: {button.is_enabled()}")
                print(f"    글자 색상: {color}")
                
                # 예약 가능 조건 확인
                is_selectable = (
                    "calendar_date" in button_classes and
                    "unselectable" not in button_classes and
                    "dayoff" not in button_classes
                )
                
                # 글자 색상이 검은색인지 확인 (활성화된 날짜)
                is_active_color = (
                    "rgba(34, 34, 37" in color or  # 네이버 기본 검은색
                    "rgb(0, 0, 0)" in color or     # 순수 검은색
                    color == "rgb(34, 34, 37)"     # 정확한 매치
                )
                
                if is_selectable and is_active_color:
                    available_dates.append(date_text)
                    print(f"    ✅ 예약 가능 (검은 글씨)")
                else:
                    if not is_active_color:
                        print(f"    ❌ 예약 불가 (회색 글씨 - 마감)")
                    else:
                        print(f"    ❌ 예약 불가 (비활성화)")
                        
            except Exception as e:
                print(f"    ❌ 날짜 분석 오류: {e}")
                continue
        
        print(f"\n📅 최종 예약 가능 날짜: {available_dates}")
        
        # 예약 가능한 시간대도 확인 (있다면)
        available_times = []
        try:
            time_buttons = driver.find_elements(By.CLASS_NAME, "time_item")
            for time_btn in time_buttons:
                if time_btn.is_enabled() and "disabled" not in time_btn.get_attribute("class"):
                    time_text = time_btn.text.strip()
                    if time_text:
                        available_times.append(time_text)
        except:
            pass  # 시간 선택이 없을 수도 있음
        
        return {
            'available': len(available_dates) > 0,
            'dates': available_dates,
            'times': available_times
        }
        
    except Exception as e:
        print(f"❌ 예약 확인 오류: {e}")
        return {'available': False, 'dates': [], 'times': []}
    
    finally:
        if driver:
            driver.quit()

def main():
    """메인 모니터링 루프"""
    print("🚀 국가 영유아 검진 예약 모니터링 시작!")
    print("📍 마일스톤소아청소년과의원 - 생후 4개월 이상")
    print("🔄 1분마다 자동 체크합니다...")
    print("🔔 예약 가능시 알림을 받으실 수 있습니다.")
    print("=" * 50)
    
    last_status = False
    
    while True:
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"\n🔍 {current_time} - 영유아 검진 예약 상태 체크 중...")
            
            result = check_booking()
            is_available = result['available']
            
            print(f"📅 발견된 날짜: {result['dates']}")
            print(f"⏰ 발견된 시간: {result['times']}")
            
            if is_available and not last_status:
                # 새로운 예약 슬롯 발견!
                dates_str = ', '.join(result['dates'][:5])
                message = f"영유아 검진 예약 가능! 날짜: {dates_str}"
                
                print(f"🎉 {message}")
                
                # 다중 알림 전송
                send_notification("🏥 마일스톤 소아과 - 영유아 검진", message)
                send_popup_alert(message)
                play_alert_sound()
                
                # 텔레그램 알림 추가
                telegram_msg = f"🏥 <b>마일스톤 소아과 - 영유아 검진</b>\n\n✅ {message}\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                send_telegram_message(telegram_msg)
                
                last_status = True
                
            elif not is_available and last_status:
                print(f"⚠️ {current_time} - 영유아 검진 예약 슬롯 없어짐")
                last_status = False
                
            elif is_available:
                print(f"✅ {current_time} - 영유아 검진 예약 계속 가능")
                
            else:
                print(f"⏳ {current_time} - 영유아 검진 예약 대기 중...")
            
            time.sleep(60)  # 1분마다 체크
            
        except KeyboardInterrupt:
            print("\n👋 영유아 검진 모니터링 종료")
            break
        except Exception as e:
            print(f"❌ 모니터링 오류: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
