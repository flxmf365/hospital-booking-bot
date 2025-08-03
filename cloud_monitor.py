#!/usr/bin/env python3
"""
마일스톤 소아과 예약 모니터링 시스템 - 클라우드 버전
AWS/Google Cloud 등 클라우드 서버에서 24시간 실행용
- 텔레그램 봇 알림 통합
- 헤드리스 Chrome 최적화
- 심층상담 + 영유아 검진 동시 모니터링
"""

import time
import requests
import traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException

class CloudHospitalMonitor:
    def __init__(self):
        # 텔레그램 봇 설정
        self.telegram_bot_token = "8024330739:AAFjlXlz7qLthxYjxdmr2uD4I2mCvSvvyyY"
        self.telegram_chat_id = "8364591827"
        
        # 모니터링 설정
        self.driver = None
        self.check_interval = 60  # 1분마다 체크
        self.consecutive_errors = 0
        self.max_consecutive_errors = 3
        
        # 상태 추적
        self.last_consultation_status = False
        self.last_infant_status = False
        self.last_check_time = None
        
        print("🏥 마일스톤 소아과 클라우드 모니터링 시스템 초기화")
        print(f"📱 텔레그램 알림: 활성화")
        print(f"🔄 체크 간격: {self.check_interval}초")
    
    def get_current_date(self):
        """현재 날짜를 YYYY-MM-DD 형식으로 반환"""
        return datetime.now().strftime('%Y-%m-%d')
    
    def get_consultation_url(self):
        """심층상담 예약 URL (동적 날짜)"""
        current_date = self.get_current_date()
        base_url = "https://m.booking.naver.com/booking/13/bizes/635057/items/4867274"
        params = f"?lang=ko&service-target=map-pc&startDate={current_date}&theme=place"
        return base_url + params
    
    def get_infant_url(self):
        """영유아 검진 예약 URL (동적 날짜)"""
        current_date = self.get_current_date()
        base_url = "https://m.booking.naver.com/booking/13/bizes/635057/items/4242694"
        params = f"?lang=ko&service-target=map-pc&startDate={current_date}&theme=place"
        return base_url + params
    
    def setup_driver(self):
        """클라우드 환경에 최적화된 ChromeDriver 설정"""
        try:
            options = Options()
            
            # 클라우드 환경 필수 옵션
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-logging")
            options.add_argument("--silent")
            options.add_argument("--window-size=1920,1080")
            
            # 추가 안정성 옵션
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--disable-features=TranslateUI")
            options.add_argument("--disable-iframes")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")  # 이미지 로딩 비활성화로 속도 향상
            
            # 메모리 최적화
            options.add_argument("--memory-pressure-off")
            options.add_argument("--max_old_space_size=2048")
            
            # 클라우드 환경 특화
            options.add_argument("--single-process")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-renderer-backgrounding")
            
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print(f"✅ 클라우드 ChromeDriver 초기화 성공")
            return driver
            
        except Exception as e:
            print(f"❌ ChromeDriver 초기화 실패: {e}")
            return None
    
    def send_telegram_message(self, message):
        """텔레그램 메시지 전송"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print(f"📱 텔레그램 메시지 전송 성공")
                return True
            else:
                print(f"❌ 텔레그램 메시지 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 텔레그램 메시지 전송 오류: {e}")
            return False
    
    def check_reservation_page(self, url, service_name):
        """예약 페이지 확인"""
        try:
            print(f"📍 {service_name} 예약 페이지 접속: {url}")
            
            # 페이지 로드
            self.driver.get(url)
            time.sleep(8)  # 충분한 로딩 시간
            
            # 현재 URL 확인
            current_url = self.driver.current_url
            print(f"🔗 현재 URL: {current_url}")
            
            # 로그인 페이지 체크
            if "login" in current_url.lower() or "auth" in current_url.lower():
                print(f"🔐 {service_name} - 로그인이 필요한 상태입니다.")
                return {'available': False, 'dates': [], 'error': 'login_required'}
            
            # 달력 요소 대기
            wait = WebDriverWait(self.driver, 20)
            
            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "calendar_date")))
                date_buttons = self.driver.find_elements(By.CLASS_NAME, "calendar_date")
                print(f"✅ {service_name} 달력 발견! {len(date_buttons)}개 날짜 버튼")
            except TimeoutException:
                print(f"⚠️ {service_name} - calendar_date 클래스를 찾을 수 없습니다.")
                page_source = self.driver.page_source
                if "예약이 마감" in page_source or "예약 불가" in page_source:
                    print(f"📄 {service_name} - 모든 예약이 마감된 상태")
                    return {'available': False, 'dates': [], 'error': 'all_booked'}
                else:
                    print(f"📄 {service_name} - 페이지 구조를 파악할 수 없습니다.")
                    return {'available': False, 'dates': [], 'error': 'page_structure_unknown'}
            
            # 날짜 분석
            available_dates = []
            
            for i, button in enumerate(date_buttons):
                try:
                    # 날짜 텍스트 추출
                    try:
                        date_span = button.find_element(By.CLASS_NAME, "num")
                        date_text = date_span.text.strip()
                    except:
                        date_text = button.text.strip() or f"날짜{i+1}"
                    
                    # 버튼 상태 확인
                    button_classes = button.get_attribute("class") or ""
                    is_enabled = button.is_enabled()
                    
                    # 글자 색상 확인
                    try:
                        if date_span:
                            color = self.driver.execute_script(
                                "return window.getComputedStyle(arguments[0]).color;", 
                                date_span
                            )
                        else:
                            color = self.driver.execute_script(
                                "return window.getComputedStyle(arguments[0]).color;", 
                                button
                            )
                    except:
                        color = "unknown"
                    
                    # 예약 가능 조건 확인
                    is_selectable = (
                        "calendar_date" in button_classes and
                        "unselectable" not in button_classes and
                        "dayoff" not in button_classes and
                        "closed" not in button_classes
                    )
                    
                    # 글자 색상이 검은색인지 확인 (활성화된 날짜)
                    is_active_color = (
                        "rgba(34, 34, 37" in color or
                        "rgb(0, 0, 0)" in color or
                        color == "rgb(34, 34, 37)"
                    )
                    
                    if is_selectable and is_active_color and is_enabled:
                        available_dates.append(date_text)
                        print(f"    ✅ {service_name} 날짜 {date_text}: 예약 가능!")
                        
                except Exception as date_error:
                    continue
            
            print(f"📅 {service_name} 최종 예약 가능 날짜: {available_dates}")
            return {
                'available': len(available_dates) > 0,
                'dates': available_dates,
                'error': None
            }
            
        except Exception as e:
            print(f"❌ {service_name} 예약 확인 중 오류: {e}")
            return {'available': False, 'dates': [], 'error': str(e)}
    
    def run_single_check(self):
        """단일 체크 실행"""
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"\n🔍 {current_time} - 예약 상태 체크 시작...")
            
            # 드라이버 초기화
            if not self.driver:
                print("🌐 새 ChromeDriver 생성 중...")
                self.driver = self.setup_driver()
                if not self.driver:
                    raise Exception("ChromeDriver 생성 실패")
            
            # 심층상담 체크
            consultation_result = self.check_reservation_page(
                self.get_consultation_url(), 
                "심층상담"
            )
            
            # 영유아 검진 체크
            infant_result = self.check_reservation_page(
                self.get_infant_url(), 
                "영유아 검진"
            )
            
            # 상태 변화 확인 및 알림
            consultation_available = consultation_result['available']
            infant_available = infant_result['available']
            
            # 심층상담 알림
            if consultation_available and not self.last_consultation_status:
                dates_str = ', '.join(consultation_result['dates'][:5])
                message = f"🏥 <b>마일스톤 소아과 - 심층상담</b>\n\n✅ 예약 가능!\n📅 날짜: {dates_str}\n\n🔗 바로 예약하기:\nhttps://m.booking.naver.com/booking/13/bizes/635057/items/4867274"
                self.send_telegram_message(message)
                self.last_consultation_status = True
                
            elif not consultation_available and self.last_consultation_status:
                print(f"⚠️ {current_time} - 심층상담 예약 슬롯 없어짐")
                self.last_consultation_status = False
            
            # 영유아 검진 알림
            if infant_available and not self.last_infant_status:
                dates_str = ', '.join(infant_result['dates'][:5])
                message = f"🏥 <b>마일스톤 소아과 - 영유아 검진</b>\n\n✅ 예약 가능!\n📅 날짜: {dates_str}\n\n🔗 바로 예약하기:\nhttps://m.booking.naver.com/booking/13/bizes/635057/items/4242694"
                self.send_telegram_message(message)
                self.last_infant_status = True
                
            elif not infant_available and self.last_infant_status:
                print(f"⚠️ {current_time} - 영유아 검진 예약 슬롯 없어짐")
                self.last_infant_status = False
            
            # 상태 출력
            if consultation_available:
                print(f"✅ {current_time} - 심층상담 예약 가능")
            else:
                print(f"⏳ {current_time} - 심층상담 예약 대기 중")
                
            if infant_available:
                print(f"✅ {current_time} - 영유아 검진 예약 가능")
            else:
                print(f"⏳ {current_time} - 영유아 검진 예약 대기 중")
            
            # 성공적인 체크
            self.last_check_time = datetime.now()
            self.consecutive_errors = 0
            return True
            
        except Exception as e:
            print(f"❌ 체크 실행 오류: {e}")
            print(f"📄 오류 상세: {traceback.format_exc()}")
            self.consecutive_errors += 1
            
            # 드라이버 문제일 가능성이 높으므로 정리
            self.cleanup_driver()
            return False
    
    def cleanup_driver(self):
        """드라이버 정리"""
        if self.driver:
            try:
                self.driver.quit()
                print("🧹 ChromeDriver 정리 완료")
            except:
                pass
            finally:
                self.driver = None
    
    def run_monitoring_loop(self):
        """메인 모니터링 루프"""
        print("🚀 마일스톤 소아과 클라우드 모니터링 시작!")
        print("☁️ 24시간 무중단 서비스")
        print(f"🔄 {self.check_interval}초마다 자동 체크")
        print("📱 텔레그램으로 즉시 알림")
        print("=" * 60)
        
        # 시작 알림
        start_message = f"🚀 <b>마일스톤 소아과 모니터링 시작</b>\n\n☁️ 클라우드 서버에서 24시간 모니터링\n📱 예약 가능시 즉시 알림\n🕐 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.send_telegram_message(start_message)
        
        while True:
            try:
                # 연속 오류가 너무 많으면 잠시 대기
                if self.consecutive_errors >= self.max_consecutive_errors:
                    wait_time = min(300, 60 * self.consecutive_errors)  # 최대 5분
                    print(f"⚠️ 연속 오류 {self.consecutive_errors}회 - {wait_time}초 대기 후 재시도")
                    time.sleep(wait_time)
                    self.consecutive_errors = 0
                
                # 단일 체크 실행
                success = self.run_single_check()
                
                if success:
                    print(f"✅ 체크 완료 - 다음 체크까지 {self.check_interval}초 대기")
                else:
                    print(f"⚠️ 체크 실패 - 30초 후 재시도")
                    time.sleep(30)
                    continue
                
                # 정상적인 대기
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("\n👋 사용자에 의한 모니터링 종료")
                break
            except Exception as e:
                print(f"❌ 모니터링 루프 오류: {e}")
                print(f"📄 오류 상세: {traceback.format_exc()}")
                
                # 심각한 오류 - 시스템 재초기화
                self.cleanup_driver()
                self.consecutive_errors += 1
                
                print("🔄 30초 후 재시도...")
                time.sleep(30)
        
        # 정리
        self.cleanup_driver()
        
        # 종료 알림
        end_message = f"🛑 <b>마일스톤 소아과 모니터링 종료</b>\n\n🕐 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.send_telegram_message(end_message)
        
        print("✅ 클라우드 모니터링 종료 완료")

def main():
    """메인 함수"""
    monitor = CloudHospitalMonitor()
    try:
        monitor.run_monitoring_loop()
    except Exception as e:
        print(f"❌ 치명적 오류: {e}")
        print(f"📄 오류 상세: {traceback.format_exc()}")
        
        # 치명적 오류 알림
        error_message = f"🚨 <b>모니터링 시스템 오류</b>\n\n❌ 치명적 오류 발생\n📄 오류: {str(e)}\n🔄 수동 재시작이 필요합니다"
        monitor.send_telegram_message(error_message)
    finally:
        monitor.cleanup_driver()

if __name__ == "__main__":
    main()
