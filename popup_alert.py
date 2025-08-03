#!/usr/bin/env python3
"""
심층상담 예약 팝업 알림 시스템
"""
import time
import subprocess
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import threading

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

def show_popup_alert(title, message):
    """팝업 창 알림"""
    def create_popup():
        root = tk.Tk()
        root.withdraw()  # 메인 창 숨기기
        
        # 팝업 창을 맨 앞으로
        root.attributes('-topmost', True)
        root.lift()
        root.focus_force()
        
        # 메시지 박스 표시
        messagebox.showinfo(title, message)
        root.destroy()
    
    # 별도 스레드에서 팝업 실행
    popup_thread = threading.Thread(target=create_popup)
    popup_thread.daemon = True
    popup_thread.start()

def send_system_notification(title, message):
    """시스템 알림도 함께"""
    try:
        script = f'display notification "{message}" with title "{title}" sound name "Glass"'
        subprocess.run(['osascript', '-e', script])
    except:
        pass

def play_alert_sound():
    """알림음 재생"""
    try:
        # 더 강한 알림음
        subprocess.run(['afplay', '/System/Library/Sounds/Sosumi.aiff'])
    except:
        try:
            subprocess.run(['say', '예약 가능합니다! 지금 확인하세요!'])
        except:
            pass

def check_booking():
    """예약 가능 여부 체크"""
    driver = setup_driver()
    try:
        url = "https://m.booking.naver.com/booking/13/bizes/635057/items/4867274?lang=ko&service-target=map-pc&startDate=2025-08-01&theme=place"
        driver.get(url)
        time.sleep(5)
        
        # 날짜 요소 찾기 - 개선된 로직
        # 1. 모든 날짜 셀 찾기
        date_cells = driver.find_elements(By.XPATH, "//td | //div[contains(@class, 'date')] | //button")
        available_dates = []
        
        for cell in date_cells:
            try:
                text = cell.text.strip()
                # 숫자이고 1-31 범위인 경우
                if text.isdigit() and 1 <= int(text) <= 31:
                    # 휴무가 아니고 활성화된 경우
                    if "휴무" not in cell.text and cell.is_displayed():
                        # 회색이 아닌 경우 (색상으로 구분)
                        color = cell.value_of_css_property("color")
                        if "rgb(153, 153, 153)" not in color:  # 회색이 아님
                            available_dates.append(text)
            except:
                continue
        
        # 중복 제거
        available_dates = list(set(available_dates))
        
        # 시간 요소 찾기  
        times = driver.find_elements(By.XPATH, "//button[contains(text(), ':') and not(@disabled)]")
        available_times = [t.text for t in times if t.is_displayed()]
        
        return {
            'available': len(available_dates) > 0 or len(available_times) > 0,
            'dates': available_dates,
            'times': available_times
        }
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return {'available': False, 'dates': [], 'times': []}
    finally:
        driver.quit()

def monitor_with_popup():
    """팝업 알림과 함께 모니터링"""
    print("🚀 심층상담 예약 팝업 알림 시스템 시작!")
    print("📍 마일스톤소아청소년과의원 모니터링 중...")
    print("💡 예약 가능시 팝업창이 나타납니다!")
    
    last_status = False
    
    while True:
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"🔍 {current_time} - 예약 상태 체크 중...")
            
            result = check_booking()
            is_available = result['available']
            
            if is_available and not last_status:
                # 새로운 예약 슬롯 발견!
                dates_str = ', '.join(result['dates'][:3]) if result['dates'] else '확인 필요'
                times_str = ', '.join(result['times'][:3]) if result['times'] else '확인 필요'
                
                popup_message = f"""🎉 심층상담 예약이 가능합니다!

📅 가능한 날짜: {dates_str}
⏰ 가능한 시간: {times_str}

지금 바로 예약하세요!"""
                
                # 팝업 알림
                show_popup_alert("🏥 마일스톤 소아과 예약 알림", popup_message)
                
                # 시스템 알림도 함께
                send_system_notification("🏥 마일스톤 소아과", "심층상담 예약 가능!")
                
                # 알림음 재생
                play_alert_sound()
                
                print(f"🎉 {current_time} - 예약 가능! 팝업 알림 전송!")
                print(f"📅 날짜: {result['dates']}")
                print(f"⏰ 시간: {result['times']}")
                
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
    monitor_with_popup()
