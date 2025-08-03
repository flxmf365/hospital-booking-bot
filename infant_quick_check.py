#!/usr/bin/env python3
"""
국가 영유아 검진 예약 즉시 확인 도구
마일스톤소아청소년과의원 - 생후 4개월 이상
"""

import time
import subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

def main():
    """즉시 예약 상태 확인"""
    print("🚀 국가 영유아 검진 예약 상태 즉시 확인!")
    print("🏥 마일스톤소아청소년과의원 - 생후 4개월 이상")
    print("=" * 50)
    
    driver = None
    try:
        print("🌐 브라우저 시작...")
        driver = setup_driver()
        
        # 단축 URL을 통해 실제 예약 페이지로 이동
        print("📍 예약 페이지 접속 중...")
        driver.get("https://naver.me/5TQg0RuJ")
        
        # 페이지 로딩 대기 (더 길게)
        print("⏳ 페이지 로딩 대기 중...")
        time.sleep(8)
        
        # 실제 예약 URL로 리다이렉트되었는지 확인
        current_url = driver.current_url
        print(f"🔗 현재 URL: {current_url}")
        
        # booking.naver.com으로 리다이렉트되었는지 확인
        if "booking.naver.com" not in current_url:
            print("⚠️ 예약 페이지로 리다이렉트되지 않음")
            print("💡 수동으로 로그인이 필요할 수 있습니다.")
            return
        
        # 달력 날짜 버튼들 찾기
        print("📅 예약 날짜 확인 중...")
        wait = WebDriverWait(driver, 15)  # 더 긴 대기 시간
        
        # 달력이 로드될 때까지 대기 (더 안전하게)
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "calendar_date")))
            print("✅ 달력 로딩 완료")
        except Exception as e:
            print(f"⚠️ 달력 로딩 실패: {e}")
            print("🔄 추가 대기 후 재시도...")
            time.sleep(5)
            # 한 번 더 시도
            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "calendar_date")))
                print("✅ 달력 로딩 완료 (재시도 성공)")
            except:
                print("❌ 달력을 찾을 수 없습니다.")
                return
        
        # 모든 달력 날짜 버튼 찾기
        date_buttons = driver.find_elements(By.CLASS_NAME, "calendar_date")
        
        available_dates = []
        
        print(f"📊 총 {len(date_buttons)}개의 날짜 버튼 발견")
        print()
        
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
                
                print()
                        
            except Exception as e:
                print(f"    ❌ 날짜 분석 오류: {e}")
                continue
        
        print(f"📅 최종 예약 가능 날짜: {available_dates}")
        
        # 예약 가능한 경우 알림
        if available_dates:
            dates_str = ', '.join(available_dates)
            message = f"영유아 검진 예약 가능! 날짜: {dates_str}"
            
            print(f"🎉 {message}")
            
            # 다중 알림 전송
            send_notification("🏥 마일스톤 소아과 - 영유아 검진", message)
            send_popup_alert(message)
            play_alert_sound()
        else:
            print("⏳ 현재 예약 가능한 날짜가 없습니다.")
        
    except Exception as e:
        print(f"❌ 예약 확인 오류: {e}")
    
    finally:
        if driver:
            driver.quit()
        print("\n✅ 확인 완료!")

if __name__ == "__main__":
    main()
