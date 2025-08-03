#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 대화형 텔레그램 봇 - 영유아검진 + 심층상담
24시간 클라우드 작동, 모든 예약 타입 동시 모니터링
"""

import time
import threading
import requests
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from telegram_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegratedHospitalBot:
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
            response = requests.post(url, data=data, timeout=15)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"메시지 전송 오류: {e}")
            return False

    def get_updates(self):
        """텔레그램 업데이트 받기"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {"offset": self.last_update_id + 1, "timeout": 3}
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data["ok"] and data["result"]:
                    return data["result"]
            return []
        except Exception as e:
            logger.error(f"업데이트 받기 오류: {e}")
            return []

    def check_infant_booking(self):
        """영유아검진 예약 상태 확인"""
        driver = None
        try:
            driver = self.setup_driver()
            driver.get(self.infant_url)
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

    def check_consultation_booking(self):
        """심층상담 예약 상태 확인"""
        driver = None
        try:
            driver = self.setup_driver()
            driver.get(self.consultation_url)
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

    def infant_monitoring_loop(self):
        """영유아검진 모니터링 루프"""
        logger.info("🍼 영유아검진 모니터링 시작")
        last_status = False
        
        while self.infant_monitoring_active:
            try:
                result = self.check_infant_booking()
                is_available = result['available']
                
                if is_available and not last_status:
                    dates_str = ', '.join(result['dates'][:5])
                    message = f"🎉 <b>영유아검진 예약 가능!</b>\n\n🍼 <b>국가 영유아검진</b>\n📅 날짜: {dates_str}\n🏥 마일스톤소아청소년과의원\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n🚀 지금 바로 예약하세요!"
                    self.send_message(message)
                    last_status = True
                    
                elif not is_available and last_status:
                    last_status = False
                
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"영유아검진 모니터링 오류: {e}")
                time.sleep(30)

    def consultation_monitoring_loop(self):
        """심층상담 모니터링 루프"""
        logger.info("💬 심층상담 모니터링 시작")
        last_status = False
        
        while self.consultation_monitoring_active:
            try:
                result = self.check_consultation_booking()
                is_available = result['available']
                
                if is_available and not last_status:
                    dates_str = ', '.join(result['dates'][:5])
                    message = f"🎉 <b>심층상담 예약 가능!</b>\n\n💬 <b>심층상담</b>\n📅 날짜: {dates_str}\n🏥 마일스톤소아청소년과의원\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n🚀 지금 바로 예약하세요!"
                    self.send_message(message)
                    last_status = True
                    
                elif not is_available and last_status:
                    last_status = False
                
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"심층상담 모니터링 오류: {e}")
                time.sleep(30)

    def handle_command(self, message_text):
        """명령어 처리"""
        command = message_text.strip().lower()
        
        # 영유아검진 명령어
        if command in ['/영유아시작', '/영유아', '영유아시작', '영유아']:
            return self.cmd_start_infant()
        elif command in ['/영유아중지', '영유아중지']:
            return self.cmd_stop_infant()
        elif command in ['/영유아체크', '영유아체크']:
            return self.cmd_check_infant()
            
        # 심층상담 명령어
        elif command in ['/심층시작', '/심층', '심층시작', '심층']:
            return self.cmd_start_consultation()
        elif command in ['/심층중지', '심층중지']:
            return self.cmd_stop_consultation()
        elif command in ['/심층체크', '심층체크']:
            return self.cmd_check_consultation()
            
        # 통합 명령어
        elif command in ['/전체시작', '/모두시작', '전체시작', '모두시작']:
            return self.cmd_start_all()
        elif command in ['/전체중지', '/모두중지', '전체중지', '모두중지']:
            return self.cmd_stop_all()
        elif command in ['/전체상태', '/상태', '전체상태', '상태']:
            return self.cmd_status()
        elif command in ['/전체체크', '전체체크']:
            return self.cmd_check_all()
            
        # 기본 명령어
        elif command in ['/help', '/도움', '도움']:
            return self.cmd_help()
        else:
            return self.cmd_help()

    def cmd_start_infant(self):
        """영유아검진 모니터링 시작"""
        if self.infant_monitoring_active:
            return "⚠️ 영유아검진 모니터링이 이미 실행 중입니다."
        
        self.infant_monitoring_active = True
        self.infant_thread = threading.Thread(target=self.infant_monitoring_loop)
        self.infant_thread.daemon = True
        self.infant_thread.start()
        
        return "🚀 <b>영유아검진 모니터링 시작!</b>\n\n🍼 국가 영유아검진 (생후 4개월 이상)\n🏥 마일스톤소아청소년과의원\n⏰ 1분마다 자동 체크\n🔔 예약 가능시 즉시 알림"

    def cmd_stop_infant(self):
        """영유아검진 모니터링 중지"""
        if not self.infant_monitoring_active:
            return "⚠️ 영유아검진 모니터링이 실행되고 있지 않습니다."
        
        self.infant_monitoring_active = False
        return "🛑 <b>영유아검진 모니터링 중지</b>\n\n영유아검진 모니터링이 중단되었습니다."

    def cmd_start_consultation(self):
        """심층상담 모니터링 시작"""
        if self.consultation_monitoring_active:
            return "⚠️ 심층상담 모니터링이 이미 실행 중입니다."
        
        self.consultation_monitoring_active = True
        self.consultation_thread = threading.Thread(target=self.consultation_monitoring_loop)
        self.consultation_thread.daemon = True
        self.consultation_thread.start()
        
        return "🚀 <b>심층상담 모니터링 시작!</b>\n\n💬 심층상담\n🏥 마일스톤소아청소년과의원\n⏰ 1분마다 자동 체크\n🔔 예약 가능시 즉시 알림"

    def cmd_stop_consultation(self):
        """심층상담 모니터링 중지"""
        if not self.consultation_monitoring_active:
            return "⚠️ 심층상담 모니터링이 실행되고 있지 않습니다."
        
        self.consultation_monitoring_active = False
        return "🛑 <b>심층상담 모니터링 중지</b>\n\n심층상담 모니터링이 중단되었습니다."

    def cmd_start_all(self):
        """모든 모니터링 시작"""
        results = []
        
        if not self.infant_monitoring_active:
            self.infant_monitoring_active = True
            self.infant_thread = threading.Thread(target=self.infant_monitoring_loop)
            self.infant_thread.daemon = True
            self.infant_thread.start()
            results.append("🍼 영유아검진 모니터링 시작")
        else:
            results.append("🍼 영유아검진 모니터링 이미 실행 중")
            
        if not self.consultation_monitoring_active:
            self.consultation_monitoring_active = True
            self.consultation_thread = threading.Thread(target=self.consultation_monitoring_loop)
            self.consultation_thread.daemon = True
            self.consultation_thread.start()
            results.append("💬 심층상담 모니터링 시작")
        else:
            results.append("💬 심층상담 모니터링 이미 실행 중")
        
        return f"🚀 <b>통합 모니터링 시작!</b>\n\n" + "\n".join(results) + f"\n\n🏥 마일스톤소아청소년과의원\n⏰ 1분마다 자동 체크\n🔔 예약 가능시 즉시 알림\n\n💻 컴퓨터 꺼도 계속 작동!"

    def cmd_stop_all(self):
        """모든 모니터링 중지"""
        self.infant_monitoring_active = False
        self.consultation_monitoring_active = False
        return "🛑 <b>모든 모니터링 중지</b>\n\n영유아검진과 심층상담 모니터링이 모두 중단되었습니다."

    def cmd_status(self):
        """현재 상태"""
        infant_status = "✅ 실행 중" if self.infant_monitoring_active else "❌ 중지됨"
        consultation_status = "✅ 실행 중" if self.consultation_monitoring_active else "❌ 중지됨"
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return f"📊 <b>통합 모니터링 상태</b>\n\n🍼 영유아검진: {infant_status}\n💬 심층상담: {consultation_status}\n\n🏥 병원: 마일스톤소아청소년과의원\n⏰ 현재 시간: {current_time}\n\n💻 24시간 클라우드 실행"

    def cmd_check_infant(self):
        """영유아검진 즉시 확인"""
        self.send_message("🔍 영유아검진 예약 상태 확인 중...")
        
        result = self.check_infant_booking()
        
        if 'error' in result:
            return f"❌ 영유아검진 확인 실패: {result['error']}"
        
        if result['available']:
            dates_str = ', '.join(result['dates'][:5])
            return f"✅ <b>영유아검진 예약 가능!</b>\n\n🍼 국가 영유아검진\n📅 날짜: {dates_str}\n⏰ 확인 시간: {result['checked_time']}"
        else:
            return f"❌ <b>영유아검진 예약 불가</b>\n\n📅 현재 예약 가능한 날짜 없음\n⏰ 확인 시간: {result['checked_time']}"

    def cmd_check_consultation(self):
        """심층상담 즉시 확인"""
        self.send_message("🔍 심층상담 예약 상태 확인 중...")
        
        result = self.check_consultation_booking()
        
        if 'error' in result:
            return f"❌ 심층상담 확인 실패: {result['error']}"
        
        if result['available']:
            dates_str = ', '.join(result['dates'][:5])
            return f"✅ <b>심층상담 예약 가능!</b>\n\n💬 심층상담\n📅 날짜: {dates_str}\n⏰ 확인 시간: {result['checked_time']}"
        else:
            return f"❌ <b>심층상담 예약 불가</b>\n\n📅 현재 예약 가능한 날짜 없음\n⏰ 확인 시간: {result['checked_time']}"

    def cmd_check_all(self):
        """모든 예약 즉시 확인"""
        self.send_message("🔍 모든 예약 상태 확인 중...")
        
        infant_result = self.check_infant_booking()
        consultation_result = self.check_consultation_booking()
        
        message = "📊 <b>전체 예약 상태</b>\n\n"
        
        # 영유아검진 결과
        if 'error' in infant_result:
            message += f"🍼 영유아검진: ❌ 확인 실패\n"
        elif infant_result['available']:
            dates_str = ', '.join(infant_result['dates'][:3])
            message += f"🍼 영유아검진: ✅ 가능 ({dates_str})\n"
        else:
            message += f"🍼 영유아검진: ❌ 불가능\n"
        
        # 심층상담 결과
        if 'error' in consultation_result:
            message += f"💬 심층상담: ❌ 확인 실패\n"
        elif consultation_result['available']:
            dates_str = ', '.join(consultation_result['dates'][:3])
            message += f"💬 심층상담: ✅ 가능 ({dates_str})\n"
        else:
            message += f"💬 심층상담: ❌ 불가능\n"
        
        message += f"\n⏰ 확인 시간: {datetime.now().strftime('%H:%M:%S')}"
        
        return message

    def cmd_help(self):
        """도움말"""
        return """🤖 <b>통합 병원 예약 모니터링 봇</b>

📋 <b>영유아검진 명령어:</b>
🍼 <b>/영유아시작</b> - 영유아검진 모니터링 시작
🛑 <b>/영유아중지</b> - 영유아검진 모니터링 중지
🔍 <b>/영유아체크</b> - 영유아검진 즉시 확인

📋 <b>심층상담 명령어:</b>
💬 <b>/심층시작</b> - 심층상담 모니터링 시작
🛑 <b>/심층중지</b> - 심층상담 모니터링 중지
🔍 <b>/심층체크</b> - 심층상담 즉시 확인

📋 <b>통합 명령어:</b>
🚀 <b>/전체시작</b> - 모든 모니터링 시작
🛑 <b>/전체중지</b> - 모든 모니터링 중지
📊 <b>/상태</b> - 전체 상태 확인
🔍 <b>/전체체크</b> - 모든 예약 즉시 확인
❓ <b>/도움</b> - 이 도움말

🏥 <b>마일스톤소아청소년과의원</b>
🍼 <b>국가 영유아검진 (생후 4개월 이상)</b>
💬 <b>심층상담</b>

💻 <b>컴퓨터 꺼도 24시간 작동!</b>
💡 명령어는 한글로도 입력 가능합니다!"""

    def run_bot(self):
        """봇 실행"""
        logger.info("🤖 통합 병원 예약 모니터링 봇 시작!")
        
        # 시작 메시지
        start_msg = """🤖 <b>통합 병원 예약 모니터링 봇 시작!</b>

🏥 <b>마일스톤소아청소년과의원</b>
🍼 국가 영유아검진 (생후 4개월 이상)
💬 심층상담

💻 컴퓨터 꺼도 24시간 작동!
📱 텔레그램에서 명령어로 완전 제어

/도움 을 입력하면 사용법을 확인할 수 있습니다."""
        
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
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                logger.info("👋 통합 봇 종료")
                if self.infant_monitoring_active:
                    self.infant_monitoring_active = False
                if self.consultation_monitoring_active:
                    self.consultation_monitoring_active = False
                break
            except Exception as e:
                logger.error(f"봇 오류: {e}")
                time.sleep(5)

if __name__ == "__main__":
    bot = IntegratedHospitalBot()
    bot.run_bot()
