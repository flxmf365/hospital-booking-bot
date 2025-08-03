#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
병원 페이지에서 국가 영유아검진 예약 링크 직접 확인
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_checkup_url():
    """국가 영유아검진 예약 URL 찾기"""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # 사용자가 제공한 URL로 이동
        url = "https://map.naver.com/p/entry/place/1473484582?lng=127.1919889&lat=37.5607552&placePath=%2F%3Fac%3D0%26adm_lat%3D37.489772%26adm_long%3D127.068952%26bizId%3D1473484582%26bookingRedirectUrl%3Dhttps%25253A%25252F%25252Fm.booking.naver.com%25252Fbooking%25252F13%25252Fbizes%25252F635057%25253Ftheme%25253Dplace%252526service-target%25253Dmap-pc%252526lang%25253Dko%26debug%3D0%26deviceType%3Dpc%26lgl_lat%3D37.482438%26lgl_long%3D127.060247%26lgl_rcode%3D09680103%26ngn_country%3DKR%26nlu_query%3D%257B%2522qr%2522%253A%255B%257B%2522query%2522%253A%2522%25EB%25A7%2588%25EC%259D%25BC%25EC%258A%25A4%25ED%2586%25A4%2520%25EC%2586%258C%25EC%2595%2584%2520%25EC%25B2%25AD%25EC%2586%258C%25EB%2585%2584%25EA%25B3%25BC%2522%252C%2522c_score%2522%253A0.808389%252C%2522score%2522%253A0.859986%252C%2522qr_category%2522%253A7%252C%2522qr_type%2522%253A33%257D%252C%257B%2522query%2522%253A%2522%25EB%25A7%2588%25EC%259D%25BC%25EC%258A%25A4%25ED%2586%25A4%2520%25EC%2586%258C%25EC%2595%2584%2522%252C%2522c_score%2522%253A0.789102%252C%2522score%2522%253A0.94678%252C%2522qr_category%2522%253A2%252C%2522qr_type%2522%253A34%257D%252C%257B%2522query%2522%253A%2522%25EB%25A7%2588%25EC%259D%25BC%25EC%258A%25A4%25ED%2586%25A4%2520%25EC%2586%258C%25EC%2595%2584%2520%25EC%25B2%25AD%25EC%2586%258C%25EB%2585%2584%25EA%25B3%25BC%2522%252C%2522c_score%2522%253A0.0%252C%2522score%2522%253A2.0%252C%2522qr_category%2522%253A1%252C%2522qr_type%2522%253A2%257D%252C%257B%2522query%2522%253A%2522%25EB%25A7%2588%25EC%259D%25BC%25EC%258A%25A4%25ED%2586%25A4%25EC%2586%258C%25EC%2595%2584%25EC%25B2%25AD%25EC%2586%258C%25EB%2585%2584%25EA%25B3%25BC%25EC%259D%2598%25EC%259B%2590%2522%252C%2522c_score%2522%253A0.0%252C%2522score%2522%253A61.0%252C%2522qr_category%2522%253A6%252C%2522qr_type%2522%253A61%257D%255D%252C%2522hospital%2522%253A%257B%2522source%2522%253A%2522placesearch%2522%252C%2522sid%2522%253A%25221473484582%2522%252C%2522q%2522%253A%2522%25EB%25A7%2588%25EC%259D%25BC%25EC%258A%25A4%25ED%2586%25A4%2520%25EC%2586%258C%25EC%2595%2584%25EA%25B3%25BC%2522%257D%252C%2522nluQuery%2522%253A%2522%25EB%25A7%2588%25EC%259D%25BC%25EC%258A%25A4%25ED%2586%25A4%2520%25EC%2586%258C%25EC%2595%2584%25EA%25B3%25BC%2522%257D%26nqx_theme%3D%257B%2522theme%2522%253A%257B%2522sub%2522%253A%255B%257B%2522name%2522%253A%2522location%2522%257D%252C%257B%2522name%2522%253A%2522hospital%2522%257D%255D%257D%257D%26r1%3D%25EC%2584%259C%25EC%259A%25B8%25ED%258A%25B9%25EB%25B3%2584%25EC%258B%259C%26r2%3D%25EA%25B0%2595%25EB%2582%25A8%25EA%25B5%25AC%26r3%3D%25EA%25B0%259C%25ED%258F%25AC2%25EB%258F%2599%26rcode%3D09680670%26rev%3D45%26sm%3Dtop_sug.pre%26spq%3D0%26ssc%3Dtab.nx.all%26target%3Dpc%26where%3Dnexearch%26x%3D127.068952%26y%3D37.489772&searchType=place&c=15.52,0,0,0,dh"
        
        driver.get(url)
        time.sleep(5)
        
        print(f"현재 URL: {driver.current_url}")
        print(f"페이지 제목: {driver.title}")
        
        # 페이지에서 모든 예약 관련 요소 찾기
        print("\n=== 예약 관련 요소 검색 ===")
        
        # 1. 텍스트로 예약 관련 요소 찾기
        booking_keywords = ["예약", "진료", "검진", "영유아", "국가", "건강"]
        
        for keyword in booking_keywords:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
            if elements:
                print(f"\n'{keyword}' 관련 요소 {len(elements)}개 발견:")
                for i, elem in enumerate(elements[:5]):  # 처음 5개만
                    try:
                        if elem.is_displayed():
                            text = elem.text.strip()
                            tag = elem.tag_name
                            if text:
                                print(f"  {i+1}. [{tag}] {text}")
                                
                                # 클릭 가능한 요소인지 확인
                                if elem.is_enabled() and tag in ['button', 'a']:
                                    href = elem.get_attribute('href')
                                    onclick = elem.get_attribute('onclick')
                                    if href:
                                        print(f"      → href: {href}")
                                    if onclick:
                                        print(f"      → onclick: {onclick}")
                    except:
                        continue
        
        # 2. 예약 버튼 직접 클릭해보기
        print("\n=== 예약 버튼 클릭 시도 ===")
        
        # 다양한 예약 버튼 선택자
        button_selectors = [
            "//button[contains(text(), '예약')]",
            "//a[contains(text(), '예약')]",
            "//button[contains(text(), '진료')]",
            "//a[contains(text(), '진료')]",
            "//*[contains(@class, 'booking')]",
            "//*[contains(@class, 'reservation')]",
            "//button[contains(text(), '검진')]",
            "//a[contains(text(), '검진')]"
        ]
        
        for selector in button_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        text = elem.text.strip()
                        print(f"\n클릭 시도: '{text}'")
                        
                        # 현재 창 개수 확인
                        current_windows = len(driver.window_handles)
                        
                        try:
                            # JavaScript로 클릭
                            driver.execute_script("arguments[0].click();", elem)
                            time.sleep(3)
                            
                            # 새 창이 열렸는지 확인
                            if len(driver.window_handles) > current_windows:
                                # 새 창으로 전환
                                driver.switch_to.window(driver.window_handles[-1])
                                new_url = driver.current_url
                                new_title = driver.title
                                
                                print(f"✅ 새 창 열림!")
                                print(f"   URL: {new_url}")
                                print(f"   제목: {new_title}")
                                
                                # 영유아검진 관련 내용 확인
                                page_content = driver.page_source
                                checkup_keywords = ['영유아검진', '국가검진', '건강검진', '예방접종']
                                found_checkup = []
                                
                                for ck in checkup_keywords:
                                    if ck in page_content:
                                        found_checkup.append(ck)
                                
                                if found_checkup:
                                    print(f"   🎯 검진 관련 키워드 발견: {', '.join(found_checkup)}")
                                    
                                    # 예약 가능한 날짜 확인
                                    date_elements = driver.find_elements(By.XPATH, 
                                        "//button[not(contains(@class, 'disabled')) and string-length(text()) <= 2 and number(text()) > 0]")
                                    
                                    if date_elements:
                                        available_dates = [elem.text for elem in date_elements if elem.text.isdigit()]
                                        print(f"   📅 예약 가능 날짜: {available_dates}")
                                        
                                        return {
                                            'url': new_url,
                                            'title': new_title,
                                            'keywords': found_checkup,
                                            'available_dates': available_dates
                                        }
                                
                                # 원래 창으로 돌아가기
                                driver.switch_to.window(driver.window_handles[0])
                                
                            elif driver.current_url != url:
                                # 같은 창에서 페이지 이동
                                new_url = driver.current_url
                                print(f"✅ 페이지 이동: {new_url}")
                                
                                if "booking" in new_url:
                                    return {'url': new_url, 'title': driver.title}
                                    
                        except Exception as e:
                            print(f"   ❌ 클릭 실패: {e}")
                            
            except Exception as e:
                continue
        
        return None
        
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        return None
    finally:
        input("브라우저를 닫으려면 Enter를 눌러주세요...")
        driver.quit()

if __name__ == "__main__":
    print("🔍 국가 영유아검진 예약 URL 찾기")
    result = find_checkup_url()
    
    if result:
        print(f"\n🎯 발견된 예약 정보:")
        print(f"   URL: {result['url']}")
        print(f"   제목: {result['title']}")
        if 'keywords' in result:
            print(f"   키워드: {', '.join(result['keywords'])}")
        if 'available_dates' in result:
            print(f"   예약 가능 날짜: {result['available_dates']}")
    else:
        print("\n❌ 국가 영유아검진 예약 페이지를 찾을 수 없습니다.")
