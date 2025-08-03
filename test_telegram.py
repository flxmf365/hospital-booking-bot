#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
텔레그램 알림 테스트 스크립트
"""

import requests
from datetime import datetime
from telegram_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_test_message():
    """텔레그램 테스트 메시지 전송"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = f"""🤖 <b>텔레그램 알림 테스트</b>

✅ 연결 상태: 정상
📱 수신자: Seo Hyun님
⏰ 테스트 시간: {current_time}

🏥 <b>마일스톤소아청소년과의원</b>
🍼 국가 영유아검진 모니터링
🔄 로컬 + 클라우드 이중 모니터링 준비 완료

🎉 <b>모든 시스템 정상 작동 중!</b>"""
        
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        print("📱 텔레그램 테스트 메시지 전송 중...")
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ 텔레그램 테스트 메시지 전송 성공!")
            print(f"📞 채팅 ID: {TELEGRAM_CHAT_ID}")
            return True
        else:
            print(f"❌ 텔레그램 전송 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 텔레그램 전송 오류: {e}")
        return False

if __name__ == "__main__":
    print("🚀 텔레그램 알림 테스트 시작!")
    success = send_test_message()
    
    if success:
        print("\n🎉 텔레그램 알림이 정상적으로 작동합니다!")
        print("📱 휴대폰에서 메시지를 확인해보세요!")
    else:
        print("\n❌ 텔레그램 알림 전송에 실패했습니다.")
        print("설정을 다시 확인해주세요.")
