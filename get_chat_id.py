#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
텔레그램 채팅 ID 자동 확인 스크립트
"""

import requests
import json

def get_chat_id():
    """텔레그램 봇의 채팅 ID 확인"""
    bot_token = "8354202456:AAEyAbrWO_cagg-MxjamDpHQWHhe1PN7uk0"
    
    try:
        # getUpdates API 호출
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print("📱 텔레그램 봇 업데이트 확인:")
            print(f"✅ 응답 상태: {response.status_code}")
            print(f"📊 업데이트 개수: {len(data.get('result', []))}")
            
            if data.get('result'):
                # 가장 최근 메시지에서 채팅 ID 추출
                latest_update = data['result'][-1]
                
                if 'message' in latest_update:
                    chat_id = latest_update['message']['chat']['id']
                    user_name = latest_update['message']['chat'].get('first_name', 'Unknown')
                    
                    print(f"\n🎯 채팅 ID 발견: {chat_id}")
                    print(f"👤 사용자: {user_name}")
                    
                    return str(chat_id)
                else:
                    print("❌ 메시지가 없습니다.")
                    
            else:
                print("⚠️ 업데이트가 없습니다.")
                print("\n📝 다음 단계를 수행해주세요:")
                print("1. 텔레그램에서 생성한 봇을 찾기")
                print("2. 봇과 대화 시작")
                print("3. /start 명령 전송")
                print("4. 이 스크립트를 다시 실행")
                
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        
    return None

if __name__ == "__main__":
    print("🔍 텔레그램 채팅 ID 확인 중...")
    chat_id = get_chat_id()
    
    if chat_id:
        print(f"\n✅ 채팅 ID: {chat_id}")
        print("\n이 ID를 telegram_config.py 파일의 TELEGRAM_CHAT_ID에 입력하세요!")
    else:
        print("\n❌ 채팅 ID를 찾을 수 없습니다.")
        print("봇과 대화를 시작한 후 다시 시도해주세요.")
