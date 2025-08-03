#!/usr/bin/env python3
"""
간단한 네이버 예약 접근
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def main():
    # 브라우저 설정
    options = Options()
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    
    try:
        # 스크린샷에서 확인된 네이버 예약 URL
        url = "https://m.booking.naver.com/booking/13/bizes/635057?theme=place&service-target=map-pc&lang=ko"
        
        print("🚀 네이버 예약 페이지 접속...")
        driver.get(url)
        time.sleep(5)
        
        print(f"📍 현재 URL: {driver.current_url}")
        
        # 로그인 필요시 대기
        if "nid.naver.com" in driver.current_url:
            print("🔐 로그인 필요! 브라우저에서 로그인 후 Enter...")
            input()
            driver.get(url)
            time.sleep(3)
        
        # 날짜/시간 찾기
        dates = driver.find_elements(By.XPATH, "//button[string-length(text()) <= 2]")
        times = driver.find_elements(By.XPATH, "//button[contains(text(), ':')]")
        
        print(f"📅 날짜 요소: {len(dates)}개")
        print(f"⏰ 시간 요소: {len(times)}개")
        
        if dates:
            print("날짜:", [d.text for d in dates[:5] if d.text.isdigit()])
        if times:
            print("시간:", [t.text for t in times[:5]])
        
        print("✅ 브라우저에서 수동으로 예약을 진행하세요!")
        input("종료하려면 Enter...")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
