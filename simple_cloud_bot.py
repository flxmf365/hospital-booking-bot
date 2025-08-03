#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
24시간 클라우드 통합 텔레그램 봇 (Chrome 없이 작동)
Render 클라우드에서 안정적으로 실행되는 간단한 버전
"""

import time
import threading
import requests
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 텔레그램 설정
TELEGRAM_BOT_TOKEN = "8354202456:AAEyAbrWO_cagg-MxjamDpHQWHhe1PN7uk0"
TELEGRAM_CHAT_ID = "8364591827"

class SimpleCloudBot:
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

    def check_booking_simple(self, url, booking_type):
        """간단한 예약 상태 확인 (HTTP 요청만 사용)"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            
            # 응답 상태 확인
            if response.status_code == 200:
                content = response.text.lower()
                
                # 예약 관련 키워드 검색
                booking_keywords = ['예약', 'booking', '날짜', 'date', '시간', 'time']
                available_keywords = ['가능', 'available', '선택', 'select']
                
                has_booking = any(keyword in content for keyword in booking_keywords)
                has_available = any(keyword in content for keyword in available_keywords)
                
                # 간단한 가용성 판단
                is_available = has_booking and has_available and len(content) > 1000
                
                return {
                    'available': is_available,
                    'dates': ['확인 필요'] if is_available else [],
                    'checked_time': datetime.now().strftime('%H:%M:%S'),
                    'type': booking_type,
                    'status_code': response.status_code
                }
            else:
                return {
                    'available': False,
                    'dates': [],
                    'error': f'HTTP {response.status_code}',
                    'type': booking_type
                }
                
        except Exception as e:
            return {
                'available': False,
                'dates': [],
                'error': str(e),
                'type': booking_type
            }

    def infant_monitoring_loop(self):
        """영유아검진 모니터링 루프"""
        logger.info("🍼 클라우드 영유아검진 모니터링 시작 (간단 버전)")
        last_status = False
        
        while self.infant_monitoring_active:
            try:
                result = self.check_booking_simple(self.infant_url, "영유아검진")
                is_available = result['available']
                
                if is_available and not last_status:
                    message = f"🎉 <b>영유아검진 예약 확인 필요!</b>\n\n🍼 <b>국가 영유아검진</b>\n📅 상태: 예약 가능 가능성 있음\n🏥 마일스톤소아청소년과의원\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n🔍 직접 확인해보세요!\n💻 클라우드에서 24시간 모니터링 중"
                    self.send_message(message)
                    last_status = True
                    logger.info(f"🎉 영유아검진 예약 가능성 감지!")
                    
                elif not is_available and last_status:
                    last_status = False
                    logger.info("⚠️ 영유아검진 예약 상태 변경")
                
                time.sleep(120)  # 2분마다 체크
                
            except Exception as e:
                logger.error(f"영유아검진 모니터링 오류: {e}")
                time.sleep(60)

    def consultation_monitoring_loop(self):
        """심층상담 모니터링 루프"""
        logger.info("💬 클라우드 심층상담 모니터링 시작 (간단 버전)")
        last_status = False
        
        while self.consultation_monitoring_active:
            try:
                result = self.check_booking_simple(self.consultation_url, "심층상담")
                is_available = result['available']
                
                if is_available and not last_status:
                    message = f"🎉 <b>심층상담 예약 확인 필요!</b>\n\n💬 <b>심층상담</b>\n📅 상태: 예약 가능 가능성 있음\n🏥 마일스톤소아청소년과의원\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n🔍 직접 확인해보세요!\n💻 클라우드에서 24시간 모니터링 중"
                    self.send_message(message)
                    last_status = True
                    logger.info(f"🎉 심층상담 예약 가능성 감지!")
                    
                elif not is_available and last_status:
                    last_status = False
                    logger.info("⚠️ 심층상담 예약 상태 변경")
                
                time.sleep(120)  # 2분마다 체크
                
            except Exception as e:
                logger.error(f"심층상담 모니터링 오류: {e}")
                time.sleep(60)

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
        elif command in ['/서버상태', '서버상태']:
            return self.cmd_server_status()
            
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
        
        return "🚀 <b>클라우드 영유아검진 모니터링 시작!</b>\n\n🍼 국가 영유아검진 (생후 4개월 이상)\n🏥 마일스톤소아청소년과의원\n⏰ 2분마다 자동 체크\n🔔 변화 감지시 즉시 알림\n\n💻 컴퓨터 꺼도 계속 작동!\n📝 간단 모니터링 버전 (안정성 우선)"

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
        
        return "🚀 <b>클라우드 심층상담 모니터링 시작!</b>\n\n💬 심층상담\n🏥 마일스톤소아청소년과의원\n⏰ 2분마다 자동 체크\n🔔 변화 감지시 즉시 알림\n\n💻 컴퓨터 꺼도 계속 작동!\n📝 간단 모니터링 버전 (안정성 우선)"

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
        
        return f"🚀 <b>클라우드 통합 모니터링 시작!</b>\n\n" + "\n".join(results) + f"\n\n🏥 마일스톤소아청소년과의원\n⏰ 2분마다 자동 체크\n🔔 변화 감지시 즉시 알림\n\n💻 컴퓨터 꺼도 24시간 계속 작동!\n📝 간단 모니터링 버전 (안정성 우선)"

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
        
        return f"📊 <b>클라우드 통합 모니터링 상태</b>\n\n🍼 영유아검진: {infant_status}\n💬 심층상담: {consultation_status}\n\n🏥 병원: 마일스톤소아청소년과의원\n⏰ 현재 시간: {current_time}\n\n💻 24시간 클라우드 실행 중\n📝 간단 모니터링 버전"

    def cmd_server_status(self):
        """서버 상태 확인"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        infant_status = "🟢 활성" if self.infant_monitoring_active else "🔴 비활성"
        consultation_status = "🟢 활성" if self.consultation_monitoring_active else "🔴 비활성"
        
        return f"🖥️ <b>클라우드 서버 상태</b>\n\n🌐 서버: 정상 운영 중\n⏰ 서버 시간: {current_time}\n🍼 영유아검진: {infant_status}\n💬 심층상담: {consultation_status}\n\n✅ 서버가 정상적으로 작동하고 있습니다!\n💻 컴퓨터 꺼도 계속 실행됩니다.\n📝 간단 모니터링 버전 (Chrome 없이 작동)"

    def cmd_check_infant(self):
        """영유아검진 즉시 확인"""
        self.send_message("🔍 영유아검진 예약 상태 확인 중...")
        
        result = self.check_booking_simple(self.infant_url, "영유아검진")
        
        if 'error' in result:
            return f"❌ 영유아검진 확인 실패: {result['error']}"
        
        if result['available']:
            return f"✅ <b>영유아검진 예약 확인 필요!</b>\n\n🍼 국가 영유아검진\n📅 상태: 예약 가능 가능성 있음\n⏰ 확인 시간: {result['checked_time']}\n\n🔍 직접 사이트에서 확인해보세요!\n💻 클라우드에서 확인됨"
        else:
            return f"❌ <b>영유아검진 예약 변화 없음</b>\n\n📅 현재 특별한 변화 감지되지 않음\n⏰ 확인 시간: {result['checked_time']}\n\n💻 클라우드에서 확인됨"

    def cmd_check_consultation(self):
        """심층상담 즉시 확인"""
        self.send_message("🔍 심층상담 예약 상태 확인 중...")
        
        result = self.check_booking_simple(self.consultation_url, "심층상담")
        
        if 'error' in result:
            return f"❌ 심층상담 확인 실패: {result['error']}"
        
        if result['available']:
            return f"✅ <b>심층상담 예약 확인 필요!</b>\n\n💬 심층상담\n📅 상태: 예약 가능 가능성 있음\n⏰ 확인 시간: {result['checked_time']}\n\n🔍 직접 사이트에서 확인해보세요!\n💻 클라우드에서 확인됨"
        else:
            return f"❌ <b>심층상담 예약 변화 없음</b>\n\n📅 현재 특별한 변화 감지되지 않음\n⏰ 확인 시간: {result['checked_time']}\n\n💻 클라우드에서 확인됨"

    def cmd_check_all(self):
        """모든 예약 즉시 확인"""
        self.send_message("🔍 모든 예약 상태 확인 중...")
        
        infant_result = self.check_booking_simple(self.infant_url, "영유아검진")
        consultation_result = self.check_booking_simple(self.consultation_url, "심층상담")
        
        message = "📊 <b>전체 예약 상태</b>\n\n"
        
        # 영유아검진 결과
        if 'error' in infant_result:
            message += f"🍼 영유아검진: ❌ 확인 실패\n"
        elif infant_result['available']:
            message += f"🍼 영유아검진: ✅ 확인 필요\n"
        else:
            message += f"🍼 영유아검진: ❌ 변화 없음\n"
        
        # 심층상담 결과
        if 'error' in consultation_result:
            message += f"💬 심층상담: ❌ 확인 실패\n"
        elif consultation_result['available']:
            message += f"💬 심층상담: ✅ 확인 필요\n"
        else:
            message += f"💬 심층상담: ❌ 변화 없음\n"
        
        message += f"\n⏰ 확인 시간: {datetime.now().strftime('%H:%M:%S')}\n💻 클라우드에서 확인됨\n📝 간단 모니터링 버전"
        
        return message

    def cmd_help(self):
        """도움말"""
        return """🤖 <b>24시간 클라우드 통합 병원 예약 봇</b>
<b>(간단 모니터링 버전)</b>

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
🖥️ <b>/서버상태</b> - 클라우드 서버 상태 확인
❓ <b>/도움</b> - 이 도움말

🏥 <b>마일스톤소아청소년과의원</b>
🍼 <b>국가 영유아검진 (생후 4개월 이상)</b>
💬 <b>심층상담</b>

💻 <b>컴퓨터 꺼도 24시간 작동!</b>
🌐 <b>클라우드에서 안정적으로 실행</b>
📝 <b>간단 모니터링 버전 (Chrome 없이 작동)</b>
💡 명령어는 한글로도 입력 가능합니다!"""

    def run_bot(self):
        """봇 실행"""
        logger.info("🤖 24시간 클라우드 통합 병원 예약 모니터링 봇 시작! (간단 버전)")
        
        # 시작 메시지
        start_msg = """🤖 <b>24시간 클라우드 통합 병원 예약 봇 시작!</b>
<b>(간단 모니터링 버전)</b>

🏥 <b>마일스톤소아청소년과의원</b>
🍼 국가 영유아검진 (생후 4개월 이상)
💬 심층상담

💻 <b>컴퓨터 꺼도 24시간 작동!</b>
🌐 클라우드에서 안정적으로 실행
📱 텔레그램에서 명령어로 완전 제어

<b>서버 정상 작동 확인:</b>
✅ 클라우드 서버 연결됨
✅ 텔레그램 봇 활성화됨
✅ 모니터링 시스템 준비됨

📝 <b>간단 모니터링 버전</b>
- Chrome 없이 작동 (안정성 우선)
- HTTP 요청으로 변화 감지
- 2분마다 자동 체크

/도움 을 입력하면 사용법을 확인할 수 있습니다."""
        
        self.send_message(start_msg)
        
        # 정기적으로 서버 상태 로그 출력
        last_heartbeat = time.time()
        
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
                
                # 5분마다 서버 상태 로그
                current_time = time.time()
                if current_time - last_heartbeat > 300:  # 5분
                    infant_status = "활성" if self.infant_monitoring_active else "비활성"
                    consultation_status = "활성" if self.consultation_monitoring_active else "비활성"
                    logger.info(f"💻 서버 상태: 정상 | 영유아검진: {infant_status} | 심층상담: {consultation_status} | 간단 버전")
                    last_heartbeat = current_time
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                logger.info("👋 클라우드 통합 봇 종료")
                if self.infant_monitoring_active:
                    self.infant_monitoring_active = False
                if self.consultation_monitoring_active:
                    self.consultation_monitoring_active = False
                break
            except Exception as e:
                logger.error(f"봇 오류: {e}")
                time.sleep(5)

if __name__ == "__main__":
    bot = SimpleCloudBot()
    bot.run_bot()
