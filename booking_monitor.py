#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 병원 예약 모니터링 및 알림 스크립트
예약 가능한 날짜가 열리면 자동으로 알림을 보냅니다.
"""

import time
import logging
import platform
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
    from telegram_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, is_telegram_configured, SETUP_GUIDE
except ImportError:
    TELEGRAM_BOT_TOKEN = None
    TELEGRAM_CHAT_ID = None
    def is_telegram_configured():
        return False
    SETUP_GUIDE = "telegram_config.py 파일을 찾을 수 없습니다."

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BookingMonitor:
    def __init__(self):
        self.driver = None
        self.wait = None
        # 실제 예약 페이지 URL (메모리에서 확인된 URL)
        self.booking_url = "https://m.booking.naver.com/booking/13/bizes/635057/items/4867274?lang=ko&service-target=map-pc&startDate=2025-08-01&theme=place"
        self.check_interval = 10  # 10초마다 체크 (더 빠른 감지)
        self.last_available_dates = set()
        
    def setup_driver(self):
        """드라이버 설정"""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")  # 백그라운드 실행
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        logger.info("드라이버 설정 완료 (헤드리스 모드)")
        
    def send_telegram_message(self, message):
        """텔레그램 메시지 전송"""
        if not is_telegram_configured():
            logger.warning("텔레그램이 설정되지 않았습니다.")
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
                logger.info("텔레그램 메시지 전송 성공")
                return True
            else:
                logger.error(f"텔레그램 메시지 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"텔레그램 메시지 전송 중 오류: {e}")
            return False
    
    def send_notification(self, title, message):
        """시스템 알림 보내기"""
        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                script = f'''
                display notification "{message}" with title "{title}" sound name "Glass"
                '''
                subprocess.run(["osascript", "-e", script])
                logger.info(f"macOS 알림 전송: {title} - {message}")
                
            elif system == "Windows":
                # Windows 토스트 알림
                import win10toast
                toaster = win10toast.ToastNotifier()
                toaster.show_toast(title, message, duration=10)
                logger.info(f"Windows 알림 전송: {title} - {message}")
                
            elif system == "Linux":
                # Linux notify-send
                subprocess.run(["notify-send", title, message])
                logger.info(f"Linux 알림 전송: {title} - {message}")
                
        except Exception as e:
            logger.error(f"알림 전송 실패: {e}")
            # 콘솔에라도 출력
            print(f"\n🚨 {title}: {message} 🚨\n")
            
        # 텔레그램 알림도 전송
        telegram_message = f"🏥 <b>{title}</b>\n\n{message}\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.send_telegram_message(telegram_message)
            
    def play_alert_sound(self):
        """알림 소리 재생"""
        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"])
            elif system == "Windows":
                import winsound
                winsound.Beep(1000, 1000)  # 1초간 1000Hz 소리
            elif system == "Linux":
                subprocess.run(["paplay", "/usr/share/sounds/alsa/Front_Left.wav"])
        except Exception as e:
            logger.warning(f"알림 소리 재생 실패: {e}")
            
    def check_available_dates(self):
        """예약 가능한 날짜 확인"""
        try:
            self.driver.get(self.booking_url)
            time.sleep(3)
            
            # 예약 가능한 날짜 버튼들 찾기
            available_dates = []
            
            # 다양한 선택자로 날짜 버튼 찾기
            date_selectors = [
                "//button[not(contains(@class, 'disabled')) and not(contains(@class, 'unavailable')) and string-length(text()) <= 2 and number(text()) > 0]",
                "//div[contains(@class, 'date') and not(contains(@class, 'disabled'))]//button",
                "//button[contains(@class, 'available')]",
                "//*[contains(@class, 'calendar')]//button[not(contains(@class, 'disabled'))]"
            ]
            
            for selector in date_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            date_text = element.text.strip()
                            if date_text.isdigit() and 1 <= int(date_text) <= 31:
                                available_dates.append(date_text)
                except Exception as e:
                    continue
                    
            # 중복 제거
            available_dates = list(set(available_dates))
            available_dates.sort(key=int)
            
            logger.info(f"현재 예약 가능한 날짜: {available_dates}")
            return set(available_dates)
            
        except Exception as e:
            logger.error(f"날짜 확인 중 오류: {e}")
            return set()
            
    def monitor_booking(self):
        """예약 모니터링 시작"""
        logger.info("=== 네이버 병원 예약 모니터링 시작 ===")
        logger.info(f"모니터링 URL: {self.booking_url}")
        logger.info(f"체크 간격: {self.check_interval}초")
        
        # 텔레그램 설정 확인
        if is_telegram_configured():
            logger.info("✅ 텔레그램 알림이 활성화되었습니다.")
            # 시작 알림 전송
            start_message = "🤖 <b>병원 예약 모니터링 시작</b>\n\n📍 마일스톤소아청소년과의원\n⏱ 10초마다 예약 상태 확인\n🔔 새로운 예약 가능 날짜 발견 시 즉시 알림"
            self.send_telegram_message(start_message)
        else:
            logger.warning("❌ 텔레그램이 설정되지 않았습니다. 시스템 알림만 사용됩니다.")
            print("\n" + "="*50)
            print("⚠️  텔레그램 알림 설정이 필요합니다!")
            print(SETUP_GUIDE)
            print("="*50 + "\n")
        
        try:
            self.setup_driver()
            
            # 초기 상태 확인
            self.last_available_dates = self.check_available_dates()
            logger.info(f"초기 예약 가능 날짜: {sorted(self.last_available_dates)}")
            
            while True:
                try:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    logger.info(f"[{current_time}] 예약 상태 확인 중...")
                    
                    current_available_dates = self.check_available_dates()
                    
                    # 새로운 날짜가 추가되었는지 확인
                    new_dates = current_available_dates - self.last_available_dates
                    
                    if new_dates:
                        new_dates_list = sorted(new_dates, key=int)
                        message = f"새로운 예약 가능 날짜: {', '.join(new_dates_list)}일"
                        
                        # 알림 보내기
                        self.send_notification("🏥 병원 예약 알림", message)
                        self.play_alert_sound()
                        
                        logger.info(f"🚨 새로운 예약 가능 날짜 발견: {new_dates_list}")
                        
                        # 콘솔에도 크게 출력
                        print("\n" + "="*50)
                        print("🚨 새로운 예약 가능 날짜 발견! 🚨")
                        print(f"날짜: {', '.join(new_dates_list)}일")
                        print(f"시간: {current_time}")
                        print("="*50 + "\n")
                        
                    # 날짜가 사라진 경우도 로깅
                    removed_dates = self.last_available_dates - current_available_dates
                    if removed_dates:
                        removed_dates_list = sorted(removed_dates, key=int)
                        logger.info(f"예약 마감된 날짜: {removed_dates_list}")
                        
                    # 상태 업데이트
                    self.last_available_dates = current_available_dates
                    
                    # 대기
                    time.sleep(self.check_interval)
                    
                except KeyboardInterrupt:
                    logger.info("모니터링이 사용자에 의해 중단되었습니다.")
                    break
                except Exception as e:
                    logger.error(f"모니터링 중 오류 발생: {e}")
                    time.sleep(self.check_interval)
                    
        except Exception as e:
            logger.error(f"모니터링 시작 실패: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("드라이버 종료")

def main():
    print("=== 네이버 병원 예약 모니터링 ===")
    print("마일스톤소아청소년과의원 예약 가능 날짜를 모니터링합니다.")
    print("새로운 예약 가능 날짜가 생기면 알림을 보냅니다.")
    print("중단하려면 Ctrl+C를 누르세요.\n")
    
    monitor = BookingMonitor()
    monitor.monitor_booking()

if __name__ == "__main__":
    main()
