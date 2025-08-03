#!/usr/bin/env python3
"""
간단한 예약 슬롯 체커
"""
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

def check_booking_page_slots(driver):
    """예약 페이지에서 슬롯 체크"""
    try:
        # 날짜 찾기
        dates = []
        date_elements = driver.find_elements(By.XPATH, 
            "//button[not(contains(@class, 'disabled')) and string-length(text()) <= 2]")
        
        for elem in date_elements:
            if elem.is_displayed() and elem.text.isdigit():
                dates.append(elem.text)
        
        # 시간 찾기
        times = []
        time_elements = driver.find_elements(By.XPATH, "//button[contains(text(), ':')]")
        
        for elem in time_elements:
            if elem.is_displayed() and "disabled" not in elem.get_attribute("class"):
                times.append(elem.text)
        
        # 결과 출력
        print(f"📅 가능한 날짜: {dates if dates else '없음'}")
        print(f"⏰ 가능한 시간: {times if times else '없음'}")
        
        if dates and times:
            print("✅ 예약 가능한 슬롯 발견!")
        else:
            print("⚠️ 예약 가능한 슬롯 없음")
            
    except Exception as e:
        print(f"❌ 슬롯 체크 오류: {e}")

def check_available_slots():
    driver = setup_driver()
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 예약 슬롯 확인 중...")
        
        # 병원 페이지 접속
        driver.get("https://map.naver.com/p/entry/place/1473484582")
        time.sleep(3)
        
        # 초록색 예약하기 버튼 찾기 (스크린샷 기준)
        selectors = [
            # 정확한 텍스트 매칭
            "//button[text()='예약하기']",
            "//a[text()='예약하기']",
            # 포함 텍스트 매칭
            "//button[contains(text(), '예약하기')]",
            "//a[contains(text(), '예약하기')]",
            "//button[contains(text(), '예약')]",
            "//a[contains(text(), '예약')]",
            # 초록색 스타일 버튼들
            "//button[contains(@style, 'background') and contains(@style, 'green')]",
            "//button[contains(@class, 'green')]",
            "//a[contains(@class, 'green')]",
            # 네이버 예약 시스템 관련
            "//*[contains(@class, 'booking')]",
            "//*[contains(@href, 'booking')]",
            # 모든 활성화된 버튼 (disabled가 아닌)
            "//button[not(@disabled) and not(contains(@class, 'disabled'))]",
            "//a[not(contains(@class, 'disabled'))]"
        ]
        
        buttons = []
        for selector in selectors:
            elements = driver.find_elements(By.XPATH, selector)
            buttons.extend(elements)
        
        if not buttons:
            # 디버깅: 페이지의 모든 버튼 확인
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            all_links = driver.find_elements(By.TAG_NAME, "a")
            
            print(f"🔍 디버깅: 페이지에 총 {len(all_buttons)}개 버튼, {len(all_links)}개 링크")
            
            # 버튼 내용 확인 (처음 10개)
            for i, btn in enumerate(all_buttons[:10]):
                try:
                    text = btn.text.strip()
                    classes = btn.get_attribute("class")
                    if text or classes:
                        print(f"  버튼 {i+1}: '{text}' (class: {classes})")
                except:
                    pass
            
            # 링크 내용 확인 (처음 5개)
            for i, link in enumerate(all_links[:5]):
                try:
                    text = link.text.strip()
                    href = link.get_attribute("href")
                    if text and href:
                        print(f"  링크 {i+1}: '{text}' -> {href[:50]}...")
                except:
                    pass
            
            # 페이지 소스에서 예약 관련 정보 확인
            page_source = driver.page_source
            keywords = ['예약', 'booking', '진료', '상담', '온라인']
            found_keywords = [k for k in keywords if k in page_source]
            
            print(f"❌ 예약 버튼 없음")
            print(f"🔍 페이지에서 발견된 키워드: {found_keywords}")
            
            # 네이버 예약 링크 직접 확인
            if 'booking.naver.com' in page_source:
                import re
                booking_urls = re.findall(r'https://[^"]*booking\.naver\.com[^"]*', page_source)
                if booking_urls:
                    print(f"🔗 예약 URL 발견: {booking_urls[0][:50]}...")
                    driver.get(booking_urls[0])
                    time.sleep(3)
                    return check_booking_page_slots(driver)
            return
        
        print(f"✅ 예약 관련 요소 {len(buttons)}개 발견")
        
        # 발견된 버튼들 정보 출력
        for i, btn in enumerate(buttons):
            try:
                text = btn.text.strip()
                classes = btn.get_attribute("class")
                print(f"  버튼 {i+1}: '{text}' (class: {classes})")
            except:
                pass
        
        # 심층상담 버튼 찾기 (보통 마지막이거나 3번째)
        target_button = None
        for btn in buttons:
            try:
                # 버튼 주변 텍스트에서 심층상담 찾기
                parent_text = btn.find_element(By.XPATH, "../..").text
                if "심층상담" in parent_text or "영유아검진 불가" in parent_text:
                    target_button = btn
                    print(f"🎯 심층상담 버튼 발견!")
                    break
            except:
                continue
        
        # 심층상담 버튼을 못 찾으면 마지막 버튼 사용
        if not target_button and buttons:
            target_button = buttons[-1]
            print(f"🎯 마지막 버튼 사용 (심층상담으로 추정)")
        
        if target_button:
            target_button.click()
        time.sleep(3)
        
        # 새 창으로 전환
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
        
        # 날짜 찾기
        dates = []
        date_elements = driver.find_elements(By.XPATH, 
            "//button[not(contains(@class, 'disabled')) and string-length(text()) <= 2]")
        
        for elem in date_elements:
            if elem.is_displayed() and elem.text.isdigit():
                dates.append(elem.text)
        
        # 시간 찾기
        times = []
        time_elements = driver.find_elements(By.XPATH, "//button[contains(text(), ':')]")
        
        for elem in time_elements:
            if elem.is_displayed() and not "disabled" in elem.get_attribute("class"):
                times.append(elem.text)
        
        # 결과 출력
        print(f"📅 가능한 날짜: {dates if dates else '없음'}")
        print(f"⏰ 가능한 시간: {times if times else '없음'}")
        
        if dates and times:
            print("✅ 예약 가능한 슬롯 발견!")
        else:
            print("⚠️ 예약 가능한 슬롯 없음")
            
    except Exception as e:
        print(f"❌ 오류: {e}")
    finally:
        driver.quit()

def monitor_slots(interval=5):
    print("=== 예약 슬롯 모니터링 시작 ===")
    print(f"체크 간격: {interval}분")
    print("종료: Ctrl+C\n")
    
    try:
        while True:
            check_available_slots()
            print("-" * 40)
            time.sleep(interval * 60)
    except KeyboardInterrupt:
        print("\n모니터링 종료")

if __name__ == "__main__":
    choice = input("1. 한번 체크 / 2. 지속 모니터링: ")
    
    if choice == "1":
        check_available_slots()
    else:
        interval = input("간격(분, 기본 5): ")
        interval = int(interval) if interval.isdigit() else 5
        monitor_slots(interval)
