#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 병원 예약 자동화 스크립트 - 마일스톤소아청소년과의원
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HospitalBooking:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.url = "https://map.naver.com/p/entry/place/1473484582"
        
    def setup_driver(self):
        """드라이버 설정"""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        logger.info("드라이버 설정 완료")
        
    def navigate_to_hospital(self):
        """병원 페이지로 이동"""
        self.driver.get(self.url)
        time.sleep(3)
        logger.info("병원 페이지 로딩 완료")
        
    def click_consultation_booking(self):
        """심층상담 예약하기 클릭"""
        # 페이지가 완전히 로드될 때까지 대기
        time.sleep(5)
        
        # 디버깅: 현재 페이지 정보 출력
        logger.info(f"현재 URL: {self.driver.current_url}")
        logger.info(f"페이지 제목: {self.driver.title}")
        
        # 페이지 소스에서 '예약' 관련 텍스트 찾기
        page_source = self.driver.page_source
        if "예약" in page_source:
            logger.info("페이지에 '예약' 텍스트가 있습니다")
            # 예약 관련 HTML 조각 출력
            import re
            booking_matches = re.findall(r'.{0,100}예약.{0,100}', page_source)
            for i, match in enumerate(booking_matches[:5]):  # 처음 5개만
                logger.info(f"예약 관련 텍스트 {i+1}: {match.strip()}")
        else:
            logger.warning("페이지에 '예약' 텍스트가 없습니다")
        
        # 다양한 방법으로 예약 버튼 찾기
        selectors = [
            "//button[contains(text(), '예약하기')]",
            "//a[contains(text(), '예약하기')]",
            "//button[contains(text(), '예약')]",
            "//a[contains(text(), '예약')]",
            "//*[contains(@class, 'booking')]",
            "//*[contains(@class, 'reservation')]",
            "//button[contains(@onclick, 'booking')]",
            "//a[contains(@href, 'booking')]"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                logger.info(f"선택자 '{selector}'로 {len(elements)}개 요소 발견")
                
                if elements:
                    for i, element in enumerate(elements):
                        try:
                            if element.is_displayed() and element.is_enabled():
                                logger.info(f"예약 버튼 {i+1} 클릭 시도")
                                self.driver.execute_script("arguments[0].scrollIntoView();", element)
                                time.sleep(1)
                                self.driver.execute_script("arguments[0].click();", element)
                                time.sleep(3)
                                
                                # 새 창이나 페이지 변화 확인
                                if len(self.driver.window_handles) > 1:
                                    self.driver.switch_to.window(self.driver.window_handles[-1])
                                    logger.info("새 창으로 전환")
                                    return True
                                elif "booking" in self.driver.current_url.lower() or "예약" in self.driver.page_source:
                                    logger.info("예약 페이지로 이동 성공")
                                    return True
                        except Exception as e:
                            logger.warning(f"버튼 {i+1} 클릭 실패: {e}")
                            continue
            except Exception as e:
                logger.warning(f"선택자 '{selector}' 실행 실패: {e}")
                continue
        
        # 페이지 소스에서 예약 관련 링크 찾기
        try:
            page_source = self.driver.page_source
            if "booking.naver.com" in page_source:
                import re
                booking_urls = re.findall(r'https://[^"]*booking\.naver\.com[^"]*', page_source)
                if booking_urls:
                    logger.info(f"예약 URL 발견: {booking_urls[0]}")
                    self.driver.get(booking_urls[0])
                    time.sleep(3)
                    return True
        except Exception as e:
            logger.warning(f"URL 추출 실패: {e}")
        
        logger.error("예약 버튼을 찾을 수 없습니다")
        return False
        
    def handle_login(self):
        """로그인 처리"""
        if "nid.naver.com" in self.driver.current_url:
            print("로그인이 필요합니다. 브라우저에서 로그인 후 Enter를 눌러주세요...")
            input()
            
    def select_date_and_time(self):
        """날짜와 시간 선택"""
        time.sleep(2)
        
        # 1. 사용 가능한 날짜 선택
        date_buttons = self.driver.find_elements(By.XPATH, 
            "//button[not(contains(@class, 'disabled')) and string-length(text()) <= 2 and number(text()) > 0]")
        
        if date_buttons:
            date_buttons[0].click()
            time.sleep(1)
            logger.info("날짜 선택 완료")
            
        # 2. 사용 가능한 시간 선택
        time_buttons = self.driver.find_elements(By.XPATH, 
            "//button[contains(text(), ':') and not(contains(@class, 'disabled'))]")
        
        if time_buttons:
            time_buttons[0].click()
            time.sleep(1)
            logger.info("시간 선택 완료")
            
    def fill_additional_info(self, child_name="테스트"):
        """추가 정보 입력"""
        time.sleep(2)
        
        try:
            # 1. 동의 드롭다운 선택
            dropdown = self.driver.find_element(By.XPATH, 
                "//select | //*[contains(text(), '해당하는 항목을 선택해주세요')]")
            dropdown.click()
            time.sleep(1)
            
            # 첫 번째 옵션 선택
            options = self.driver.find_elements(By.XPATH, "//option[position()>1]")
            if options:
                options[0].click()
                logger.info("동의 항목 선택 완료")
                
        except Exception as e:
            logger.warning(f"드롭다운 선택 실패: {e}")
            
        try:
            # 2. 아이 이름 입력
            name_input = self.driver.find_element(By.XPATH, 
                "//textarea[contains(@placeholder, '내용을 입력')] | //input[contains(@placeholder, '내용을 입력')]")
            name_input.clear()
            name_input.send_keys(child_name)
            logger.info(f"아이 이름 입력 완료: {child_name}")
            
        except Exception as e:
            logger.warning(f"이름 입력 실패: {e}")
            
    def submit_booking(self):
        """예약 제출"""
        try:
            submit_button = self.driver.find_element(By.XPATH, 
                "//button[contains(text(), '예약') or contains(text(), '신청') or contains(text(), '완료')]")
            submit_button.click()
            logger.info("예약 신청 완료!")
            return True
        except Exception as e:
            logger.error(f"예약 제출 실패: {e}")
            return False
            
    def run_booking(self, child_name="테스트"):
        """전체 예약 프로세스 실행"""
        try:
            self.setup_driver()
            self.navigate_to_hospital()
            
            if not self.click_consultation_booking():
                logger.error("예약 버튼 클릭 실패")
                return False
                
            self.handle_login()
            self.select_date_and_time()
            self.fill_additional_info(child_name)
            
            print("예약 정보를 확인하고 제출하시겠습니까? (y/n): ", end="")
            confirm = input().lower()
            
            if confirm == 'y':
                return self.submit_booking()
            else:
                logger.info("예약이 취소되었습니다.")
                return False
                
        except Exception as e:
            logger.error(f"예약 프로세스 실패: {e}")
            return False
        finally:
            if self.driver:
                input("브라우저를 닫으려면 Enter를 눌러주세요...")
                self.driver.quit()

if __name__ == "__main__":
    booking = HospitalBooking()
    
    print("=== 네이버 병원 예약 자동화 ===")
    child_name = input("아이 이름을 입력하세요 (기본값: 테스트): ").strip()
    if not child_name:
        child_name = "테스트"
        
    success = booking.run_booking(child_name)
    
    if success:
        print("✅ 예약이 완료되었습니다!")
    else:
        print("❌ 예약에 실패했습니다.")
