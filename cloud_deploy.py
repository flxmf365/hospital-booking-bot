#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
24시간 클라우드 통합 대화형 텔레그램 봇
컴퓨터 꺼도 계속 작동하는 영유아검진 + 심층상담 모니터링
"""

import time
import threading
import requests
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/hospital_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 텔레그램 설정 (클라우드용)
TELEGRAM_BOT_TOKEN = "8354202456:AAEyAbrWO_cagg-MxjamDpHQWHhe1PN7uk0"
TELEGRAM_CHAT_ID = "8364591827"

class CloudIntegratedBot:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.infant_monitoring_active = False
        self.consultation_monitoring_active = False
        self.infant_thread = None
        self.consultation_thread = None
        self.last_update_id = 0
        
        # 예약 URL들
        self.infant_url = "https://naver.me/5TQg0RuJ"
        self.consultation_url = "https://m.booking.naver.com/booking/13/bizes/635057/items/4867274"
        
    def setup_driver(self):
        """클라우드 서버용 드라이버 설정"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
        return webdriver.Chrome(options=options)

    def send_message(self, message):
        """텔레그램 메시지 전송"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"메시지 전송 오류: {e}")
            return False

    def get_updates(self):
        """텔레그램 업데이트 받기"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {"offset": self.last_update_id + 1, "timeout": 1}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data["ok"] and data["result"]:
                    return data["result"]
            return []
        except Exception as e:
            logger.error(f"업데이트 받기 오류: {e}")
            return []

    def check_booking_status(self):
        """예약 상태 확인"""
        driver = None
        try:
            driver = self.setup_driver()
            driver.get("https://naver.me/5TQg0RuJ")
            time.sleep(3)
            
            current_url = driver.current_url
            if "booking.naver.com" not in current_url:
                return {'available': False, 'dates': [], 'error': '예약 페이지 접속 실패'}
            
            date_buttons = driver.find_elements(By.CLASS_NAME, "calendar_date")
            available_dates = []
            
            for button in date_buttons:
                try:
                    date_span = button.find_element(By.CLASS_NAME, "num")
                    date_text = date_span.text.strip()
                    
                    button_classes = button.get_attribute("class")
                    is_selectable = "unselectable" not in button_classes
                    
                    color = date_span.value_of_css_property("color")
                    is_active_color = (
                        "rgba(34, 34, 37" in color or
                        "rgb(0, 0, 0)" in color or
                        color == "rgb(34, 34, 37)"
                    )
                    
                    if is_selectable and is_active_color and date_text.isdigit():
                        available_dates.append(date_text)
                        
                except Exception:
                    continue
            
            return {
                'available': len(available_dates) > 0,
                'dates': available_dates,
                'checked_time': datetime.now().strftime('%H:%M:%S')
            }
            
        except Exception as e:
            return {'available': False, 'dates': [], 'error': str(e)}
        finally:
            if driver:
                driver.quit()

    def monitoring_loop(self):
        """모니터링 루프"""
        logger.info("🔄 클라우드 모니터링 시작")
        last_status = False
        
        while self.monitoring_active:
            try:
                result = self.check_booking_status()
                is_available = result['available']
                
                if is_available and not last_status:
                    dates_str = ', '.join(result['dates'][:5])
                    message = f"🎉 <b>영유아검진 예약 가능!</b>\n\n📅 날짜: {dates_str}\n🏥 마일스톤소아청소년과의원\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n🚀 지금 바로 예약하세요!"
                    self.send_message(message)
                    last_status = True
                    
                elif not is_available and last_status:
                    last_status = False
                
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"모니터링 오류: {e}")
                time.sleep(30)

    def handle_command(self, message_text):
        """명령어 처리"""
        command = message_text.strip().lower()
        
        if command in ['/start', '/시작', '시작']:
            return self.cmd_start()
        elif command in ['/stop', '/중지', '중지']:
            return self.cmd_stop()
        elif command in ['/status', '/상태', '상태']:
            return self.cmd_status()
        elif command in ['/check', '/체크', '체크']:
            return self.cmd_check()
        elif command in ['/help', '/도움', '도움']:
            return self.cmd_help()
        else:
            return self.cmd_help()

    def cmd_start(self):
        """모니터링 시작"""
        if self.monitoring_active:
            return "⚠️ 모니터링이 이미 실행 중입니다."
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        return "🚀 <b>클라우드 모니터링 시작!</b>\n\n🏥 마일스톤소아청소년과의원\n🍼 국가 영유아검진\n⏰ 1분마다 자동 체크\n🔔 예약 가능시 즉시 알림\n\n💻 컴퓨터 꺼도 계속 작동!"

    def cmd_stop(self):
        """모니터링 중지"""
        if not self.monitoring_active:
            return "⚠️ 모니터링이 실행되고 있지 않습니다."
        
        self.monitoring_active = False
        return "🛑 <b>모니터링 중지</b>\n\n모니터링이 중단되었습니다."

    def cmd_status(self):
        """현재 상태"""
        status = "✅ 실행 중" if self.monitoring_active else "❌ 중지됨"
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return f"📊 <b>클라우드 모니터링 상태</b>\n\n🔄 상태: {status}\n🏥 병원: 마일스톤소아청소년과의원\n🍼 검진: 국가 영유아검진\n⏰ 현재 시간: {current_time}\n\n💻 24시간 클라우드 실행"

    def cmd_check(self):
        """즉시 예약 확인"""
        self.send_message("🔍 예약 상태 확인 중...")
        
        result = self.check_booking_status()
        
        if 'error' in result:
            return f"❌ 확인 실패: {result['error']}"
        
        if result['available']:
            dates_str = ', '.join(result['dates'][:5])
            return f"✅ <b>예약 가능!</b>\n\n📅 날짜: {dates_str}\n⏰ 확인 시간: {result['checked_time']}"
        else:
            return f"❌ <b>예약 불가</b>\n\n📅 현재 예약 가능한 날짜 없음\n⏰ 확인 시간: {result['checked_time']}"

    def cmd_help(self):
        """도움말"""
        return """🤖 <b>24시간 클라우드 영유아검진 봇</b>

📋 <b>사용 가능한 명령어:</b>

🚀 <b>/시작</b> - 모니터링 시작
🛑 <b>/중지</b> - 모니터링 중지
📊 <b>/상태</b> - 현재 상태 확인
🔍 <b>/체크</b> - 즉시 예약 확인
❓ <b>/도움</b> - 이 도움말

🏥 <b>마일스톤소아청소년과의원</b>
🍼 <b>국가 영유아검진 (생후 4개월 이상)</b>

💻 <b>컴퓨터 꺼도 24시간 작동!</b>
💡 명령어는 한글로도 입력 가능합니다!"""

    def run_bot(self):
        """봇 실행"""
        logger.info("🤖 24시간 클라우드 대화형 봇 시작!")
        
        # 시작 메시지
        start_msg = "🤖 <b>24시간 클라우드 봇 시작!</b>\n\n💻 컴퓨터 꺼도 계속 작동합니다!\n📱 텔레그램에서 명령어로 제어 가능\n\n/도움 을 입력하면 사용법을 확인할 수 있습니다."
        self.send_message(start_msg)
        
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.last_update_id = update["update_id"]
                    
                    if "message" in update:
                        message = update["message"]
                        if "text" in message and str(message["chat"]["id"]) == self.chat_id:
                            user_message = message["text"]
                            logger.info(f"📱 받은 메시지: {user_message}")
                            
                            response = self.handle_command(user_message)
                            self.send_message(response)
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("👋 클라우드 봇 종료")
                if self.monitoring_active:
                    self.monitoring_active = False
                break
            except Exception as e:
                logger.error(f"봇 오류: {e}")
                time.sleep(5)

if __name__ == "__main__":
    bot = CloudTelegramBot()
    bot.run_bot()
