#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
텔레그램 봇 설정 파일
"""

# 텔레그램 봇 설정
# 1. @BotFather에게 /newbot 명령으로 새 봇 생성
# 2. 봇 토큰을 받아서 아래에 입력
# 3. 봇과 대화를 시작하고 /start 명령 전송
# 4. https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates 에서 chat_id 확인

TELEGRAM_BOT_TOKEN = "8354202456:AAEyAbrWO_cagg-MxjamDpHQWHhe1PN7uk0"  # 봇 토큰을 여기에 입력
TELEGRAM_CHAT_ID = "8364591827"     # 채팅 ID를 여기에 입력

# 설정 완료 여부 확인
def is_telegram_configured():
    return (TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE" and 
            TELEGRAM_CHAT_ID != "YOUR_CHAT_ID_HERE" and
            TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

# 텔레그램 봇 설정 가이드
SETUP_GUIDE = """
🤖 텔레그램 봇 설정 가이드:

1. 텔레그램에서 @BotFather 검색
2. /newbot 명령으로 새 봇 생성
3. 봇 이름과 사용자명 설정
4. 받은 토큰을 telegram_config.py의 TELEGRAM_BOT_TOKEN에 입력

5. 생성된 봇과 대화 시작
6. /start 명령 전송
7. 브라우저에서 다음 URL 접속:
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
8. 응답에서 "chat":{"id": 숫자} 찾아서 TELEGRAM_CHAT_ID에 입력

예시:
TELEGRAM_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM_CHAT_ID = "123456789"
"""
