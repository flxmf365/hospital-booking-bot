#!/usr/bin/env python3
"""
팝업 테스트 - 어떻게 나타나는지 확인
"""
import tkinter as tk
from tkinter import messagebox
import subprocess

def show_test_popup():
    """테스트 팝업 표시"""
    root = tk.Tk()
    root.withdraw()  # 메인 창 숨기기
    
    # 팝업을 화면 맨 앞으로
    root.attributes('-topmost', True)
    root.lift()
    root.focus_force()
    
    # 테스트 메시지
    test_message = """🎉 심층상담 예약이 가능합니다!

📅 가능한 날짜: 15, 16, 17
⏰ 가능한 시간: 09:00, 10:00, 11:00

지금 바로 예약하세요!

(이것은 테스트 팝업입니다)"""
    
    # 팝업 표시
    messagebox.showinfo("🏥 마일스톤 소아과 예약 알림", test_message)
    
    root.destroy()
    print("✅ 테스트 팝업이 표시되었습니다!")

def play_test_sound():
    """테스트 알림음"""
    try:
        subprocess.run(['afplay', '/System/Library/Sounds/Sosumi.aiff'])
        print("🔊 알림음 재생 완료!")
    except:
        try:
            subprocess.run(['say', '예약 가능합니다! 지금 확인하세요!'])
            print("🗣️ 음성 알림 재생 완료!")
        except:
            print("❌ 알림음 재생 실패")

if __name__ == "__main__":
    print("🧪 팝업 알림 테스트 시작!")
    print("📱 팝업창이 화면 중앙에 나타납니다...")
    
    # 알림음 먼저 재생
    play_test_sound()
    
    # 팝업 표시
    show_test_popup()
    
    print("✅ 테스트 완료!")
    print("💡 실제 예약 가능시 이런 팝업이 나타납니다!")
