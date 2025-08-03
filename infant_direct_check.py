#!/usr/bin/env python3
"""
국가 영유아 검진 예약 직접 확인 도구 (안정적인 버전)
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
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
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
    """즉시 예약 상태 확인 (직접 URL 접근)"""
    print("🚀 국가 영유아 검진 예약 상태 즉시 확인!")
    print("🏥 마일스톤소아청소년과의원 - 생후 4개월 이상")
    print("🔗 직접 URL 접근 방식 (더 안정적)")
    print("=" * 50)
    
    driver = None
    try:
        print("🌐 브라우저 시작...")
        driver = setup_driver()
        
        # 확인된 직접 URL로 접근
        direct_url = "https://m.booking.naver.com/booking/13/bizes/635057/items/4242694?lang=ko&service-target=map-pc&startDate=2025-08-01&theme=place"
        print("📍 영유아 검진 예약 페이지 직접 접속...")
        print(f"🔗 URL: {direct_url}")
        
        driver.get(direct_url)
        
        # 페이지 로딩 대기
        print("⏳ 페이지 로딩 대기 중...")
        time.sleep(10)
        
        current_url = driver.current_url
        print(f"🔗 현재 URL: {current_url}")
        
        # 로그인 페이지로 리다이렉트되었는지 확인
        if "login" in current_url.lower() or "auth" in current_url.lower():
            print("🔐 로그인이 필요한 상태입니다.")
            print("💡 수동으로 로그인 후 다시 시도해주세요.")
            return
        
        # 달력 날짜 버튼들 찾기
        print("📅 예약 날짜 확인 중...")
        wait = WebDriverWait(driver, 20)
        
        # 여러 방법으로 달력 요소 찾기 시도
        calendar_found = False
        
        # 방법 1: calendar_date 클래스
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "calendar_date")))
            date_buttons = driver.find_elements(By.CLASS_NAME, "calendar_date")
            calendar_found = True
            print(f"✅ 달력 발견! (방법 1) - {len(date_buttons)}개 날짜")
        except:
            print("⚠️ 방법 1 실패 - calendar_date 클래스 없음")
        
        # 방법 2: 다른 가능한 클래스들
        if not calendar_found:
            possible_classes = ["date-item", "calendar-date", "booking-date", "date_button"]
            for class_name in possible_classes:
                try:
                    elements = driver.find_elements(By.CLASS_NAME, class_name)
                    if elements:
                        date_buttons = elements
                        calendar_found = True
                        print(f"✅ 달력 발견! (방법 2: {class_name}) - {len(date_buttons)}개 날짜")
                        break
                except:
                    continue
        
        # 방법 3: 페이지 소스 분석
        if not calendar_found:
            print("🔍 페이지 소스 분석 중...")
            page_source = driver.page_source
            
            # 예약 관련 키워드 확인
            keywords = ["예약", "booking", "calendar", "날짜", "date"]
            found_keywords = [kw for kw in keywords if kw in page_source]
            print(f"📝 발견된 키워드: {found_keywords}")
            
            # 현재 페이지 상태 확인
            if "예약이 마감" in page_source or "예약 불가" in page_source:
                print("❌ 현재 모든 예약이 마감된 상태입니다.")
            elif "로그인" in page_source:
                print("🔐 로그인이 필요한 상태입니다.")
            else:
                print("⚠️ 예약 시스템 상태를 정확히 파악할 수 없습니다.")
            
            print("📄 페이지 소스 일부:")
            print(page_source[:500] + "..." if len(page_source) > 500 else page_source)
            return
        
        # 달력을 찾은 경우 분석
        available_dates = []
        
        print(f"📊 총 {len(date_buttons)}개의 날짜 버튼 발견")
        print()
        
        for i, button in enumerate(date_buttons):
            try:
                # 날짜 텍스트 추출
                date_text = button.text.strip()
                if not date_text:
                    # span.num에서 텍스트 찾기
                    try:
                        date_span = button.find_element(By.CLASS_NAME, "num")
                        date_text = date_span.text.strip()
                    except:
                        date_text = f"날짜{i+1}"
                
                # 버튼 클래스 확인
                button_classes = button.get_attribute("class")
                
                # 활성화 상태 확인
                is_enabled = button.is_enabled()
                
                print(f"  날짜: {date_text}")
                print(f"    클래스: {button_classes}")
                print(f"    활성화: {is_enabled}")
                
                # 글자 색상 확인 (가능한 경우)
                try:
                    color = driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).color;", 
                        button
                    )
                    print(f"    글자 색상: {color}")
                    
                    # 예약 가능 조건 확인
                    is_selectable = (
                        "calendar_date" in button_classes and
                        "unselectable" not in button_classes and
                        "dayoff" not in button_classes
                    )
                    
                    # 글자 색상이 검은색인지 확인
                    is_active_color = (
                        "rgba(34, 34, 37" in color or
                        "rgb(0, 0, 0)" in color or
                        color == "rgb(34, 34, 37)"
                    )
                    
                    if is_selectable and is_active_color and is_enabled:
                        available_dates.append(date_text)
                        print(f"    ✅ 예약 가능 (검은 글씨)")
                    else:
                        if not is_active_color:
                            print(f"    ❌ 예약 불가 (회색 글씨 - 마감)")
                        else:
                            print(f"    ❌ 예약 불가 (비활성화)")
                            
                except Exception as color_error:
                    print(f"    ⚠️ 색상 확인 실패: {color_error}")
                    # 색상 확인 실패시 기본 조건만으로 판단
                    if is_enabled and "unselectable" not in button_classes:
                        available_dates.append(date_text)
                        print(f"    ✅ 예약 가능 (기본 조건)")
                    else:
                        print(f"    ❌ 예약 불가")
                
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
            print("💡 모든 날짜가 마감된 상태입니다.")
        
    except Exception as e:
        print(f"❌ 예약 확인 오류: {e}")
        print("💡 네트워크 상태나 페이지 구조가 변경되었을 수 있습니다.")
    
    finally:
        if driver:
            driver.quit()
        print("\n✅ 확인 완료!")

if __name__ == "__main__":
    main()
