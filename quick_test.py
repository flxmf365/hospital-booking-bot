#!/usr/bin/env python3
"""
빠른 테스트용 - 브라우저 창을 보면서 실행
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def quick_test():
    # headless 모드 끄기 (브라우저 창 보이게)
    options = Options()
    options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print("🚀 병원 페이지 접속 중...")
        driver.get("https://map.naver.com/p/entry/place/1473484582")
        
        print("⏳ 10초 대기 (동적 콘텐츠 로드 대기)...")
        time.sleep(10)
        
        # iframe 확인
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"🖼️ 페이지에 {len(iframes)}개 iframe 발견")
        
        # 네이버 예약 URL 직접 찾기
        page_source = driver.page_source
        if "booking.naver.com" in page_source:
            import re
            booking_urls = re.findall(r'https://[^"\s]*booking\.naver\.com[^"\s]*', page_source)
            if booking_urls:
                print(f"🔗 네이버 예약 URL 발견: {booking_urls[0]}")
                print("🚀 예약 URL로 직접 이동 시도...")
                driver.get(booking_urls[0])
                time.sleep(5)
                
                # 예약 페이지에서 날짜/시간 찾기
                dates = driver.find_elements(By.XPATH, "//button[string-length(text()) <= 2 and text() != '']")
                times = driver.find_elements(By.XPATH, "//button[contains(text(), ':')]")
                
                print(f"📅 예약 페이지 날짜 요소: {len(dates)}개")
                print(f"⏰ 예약 페이지 시간 요소: {len(times)}개")
                
                if dates:
                    print("날짜들:", [d.text for d in dates[:5]])
                if times:
                    print("시간들:", [t.text for t in times[:5]])
                
                print("✅ 예약 URL 직접 접근 성공!")
                input("예약 페이지를 확인하고 Enter를 누르세요...")
                return
        
        print("🔍 예약 버튼 찾는 중...")
        
        # 왼쪽 패널의 예약 버튼 찾기
        selectors = [
            # 왼쪽 패널의 예약 버튼 (스크린샷 기준)
            "//div[contains(@class, 'place')]//button[contains(text(), '예약')]",
            "//div[contains(@class, 'panel')]//button[contains(text(), '예약')]",
            "//div[contains(@class, 'info')]//button[contains(text(), '예약')]",
            # 일반적인 예약 버튼
            "//button[text()='예약']",
            "//a[text()='예약']",
            "//button[contains(text(), '예약')]",
            "//a[contains(text(), '예약')]",
            # 네이버 예약 링크
            "//a[contains(@href, 'booking.naver.com')]"
        ]
        
        all_buttons = []
        for i, selector in enumerate(selectors):
            elements = driver.find_elements(By.XPATH, selector)
            print(f"  선택자 {i+1} ('{selector[:30]}...'): {len(elements)}개")
            if i < 3:  # 예약 관련만
                all_buttons.extend(elements)
        
        # 모든 버튼 정보 출력
        all_page_buttons = driver.find_elements(By.XPATH, "//button")
        print(f"🔍 페이지의 모든 버튼 ({len(all_page_buttons)}개) 분석:")
        
        potential_booking_buttons = []
        for i, btn in enumerate(all_page_buttons):
            try:
                text = btn.text.strip()
                classes = btn.get_attribute("class")
                onclick = btn.get_attribute("onclick")
                
                # 예약 관련 가능성 체크
                is_potential = any([
                    "예약" in text,
                    "booking" in classes.lower() if classes else False,
                    "reservation" in classes.lower() if classes else False,
                    "green" in classes.lower() if classes else False,
                    onclick and "booking" in onclick.lower()
                ])
                
                if is_potential or text:  # 예약 관련이거나 텍스트가 있는 버튼
                    print(f"  버튼 {i+1}: '{text}' | class: {classes} | onclick: {onclick}")
                    if is_potential:
                        potential_booking_buttons.append(btn)
                        
            except Exception as e:
                continue
        
        print(f"✅ 예약 가능성 버튼: {len(potential_booking_buttons)}개")
        buttons = potential_booking_buttons
        
        if buttons:
            print(f"🎯 마지막 버튼 클릭 시도...")
            buttons[-1].click()
            time.sleep(3)
            
            # 새 창 확인
            if len(driver.window_handles) > 1:
                print("🔄 새 창으로 전환")
                driver.switch_to.window(driver.window_handles[-1])
            
            print(f"📍 현재 URL: {driver.current_url}")
            
            # 날짜/시간 요소 찾기
            dates = driver.find_elements(By.XPATH, "//button[string-length(text()) <= 2 and text() != '']")
            times = driver.find_elements(By.XPATH, "//button[contains(text(), ':')]")
            
            print(f"📅 날짜 요소: {len(dates)}개")
            print(f"⏰ 시간 요소: {len(times)}개")
            
            if dates:
                print("날짜들:", [d.text for d in dates[:5]])
            if times:
                print("시간들:", [t.text for t in times[:5]])
        
        print("\n✅ 테스트 완료! 브라우저를 확인해보세요.")
        input("브라우저를 닫으려면 Enter를 누르세요...")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        input("오류 확인 후 Enter를 누르세요...")
    finally:
        driver.quit()

if __name__ == "__main__":
    quick_test()
