#!/usr/bin/env python3
"""
마일스톤 소아과 심층상담 예약 모니터링 시스템 (완전 안정화 버전)
- 동적 날짜 처리
- 강화된 에러 처리 및 자동 복구
- 상세한 로깅 및 헬스체크
- ChromeDriver 안정성 개선
"""

import time
import subprocess
import traceback
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException

class RobustReservationMonitor:
    def __init__(self):
        self.driver = None
        self.last_check_time = None
        self.consecutive_errors = 0
        self.max_consecutive_errors = 3
        self.check_interval = 60  # 1분
        self.last_status = False
        
    def get_current_date(self):
        """현재 날짜를 YYYY-MM-DD 형식으로 반환"""
        return datetime.now().strftime('%Y-%m-%d')
    
    def get_reservation_url(self):
        """동적으로 예약 URL 생성 (항상 오늘 날짜)"""
        current_date = self.get_current_date()
        base_url = "https://m.booking.naver.com/booking/13/bizes/635057/items/4867274"
        params = f"?lang=ko&service-target=map-pc&startDate={current_date}&theme=place"
        return base_url + params
    
    def setup_driver(self):
        """안정적인 ChromeDriver 설정"""
        try:
            options = Options()
            # 헤드리스 모드 + 안정성 옵션
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
            
            # 메모리 및 성능 최적화
            options.add_argument("--memory-pressure-off")
            options.add_argument("--max_old_space_size=4096")
            
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print(f"✅ ChromeDriver 초기화 성공")
            return driver
            
        except Exception as e:
            print(f"❌ ChromeDriver 초기화 실패: {e}")
            return None
    
    def send_notification(self, title, message):
        """macOS 시스템 알림 전송"""
        try:
            script = f'''
            display notification "{message}" with title "{title}" sound name "Sosumi"
            '''
            subprocess.run(['osascript', '-e', script], check=True, timeout=10)
            print(f"🔔 시스템 알림 전송: {message}")
            return True
        except Exception as e:
            print(f"❌ 알림 전송 실패: {e}")
            return False
    
    def send_popup_alert(self, message):
        """팝업 대화상자 표시"""
        try:
            script = f'''
            display dialog "{message}" with title "🏥 마일스톤 소아과 - 심층상담" buttons {{"확인"}} default button "확인" with icon note
            '''
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=True, timeout=30)
            print(f"💬 팝업 표시: {message}")
            return result.stdout.strip()
        except Exception as e:
            print(f"❌ 팝업 표시 실패: {e}")
            return None
    
    def play_alert_sound(self):
        """알림음 재생"""
        try:
            subprocess.run(['afplay', '/System/Library/Sounds/Sosumi.aiff'], 
                         check=False, timeout=5)
            subprocess.run(['say', '심층상담 예약 가능합니다'], 
                         check=False, timeout=10)
            print("🔊 알림음 재생 완료")
            return True
        except Exception as e:
            print(f"❌ 알림음 재생 실패: {e}")
            return False
    
    def send_all_alerts(self, message):
        """모든 종류의 알림 전송"""
        print(f"🎉 {message}")
        
        # 병렬로 알림 전송 (하나 실패해도 다른 것들은 계속)
        results = []
        results.append(self.send_notification("🏥 마일스톤 소아과 - 심층상담", message))
        results.append(self.send_popup_alert(message))
        results.append(self.play_alert_sound())
        
        # 결과를 boolean으로 변환하여 합계 계산
        success_count = sum(1 for result in results if result)
        print(f"📊 알림 전송 결과: {success_count}/3 성공")
        return success_count > 0
    
    def check_reservation_availability(self):
        """예약 가능 여부 확인 (강화된 에러 처리)"""
        url = self.get_reservation_url()
        print(f"📍 예약 페이지 접속: {url}")
        
        try:
            # 페이지 로드
            self.driver.get(url)
            print("⏳ 페이지 로딩 대기 중...")
            time.sleep(8)  # 충분한 로딩 시간
            
            # 현재 URL 확인
            current_url = self.driver.current_url
            print(f"🔗 현재 URL: {current_url}")
            
            # 로그인 페이지 체크
            if "login" in current_url.lower() or "auth" in current_url.lower():
                print("🔐 로그인이 필요한 상태입니다.")
                return {'available': False, 'dates': [], 'error': 'login_required'}
            
            # 달력 요소 대기 (여러 방법으로 시도)
            wait = WebDriverWait(self.driver, 20)
            
            # 방법 1: calendar_date 클래스
            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "calendar_date")))
                date_buttons = self.driver.find_elements(By.CLASS_NAME, "calendar_date")
                print(f"✅ 달력 발견! {len(date_buttons)}개 날짜 버튼")
            except TimeoutException:
                print("⚠️ calendar_date 클래스를 찾을 수 없습니다.")
                # 페이지 소스 분석으로 대체
                page_source = self.driver.page_source
                if "예약이 마감" in page_source or "예약 불가" in page_source:
                    print("📄 페이지 분석: 모든 예약이 마감된 상태")
                    return {'available': False, 'dates': [], 'error': 'all_booked'}
                else:
                    print("📄 페이지 구조를 파악할 수 없습니다.")
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
                    
                    print(f"  날짜 {date_text}: 클래스={button_classes}, 활성화={is_enabled}, 색상={color}")
                    
                    if is_selectable and is_active_color and is_enabled:
                        available_dates.append(date_text)
                        print(f"    ✅ 예약 가능!")
                    else:
                        print(f"    ❌ 예약 불가")
                        
                except Exception as date_error:
                    print(f"    ❌ 날짜 {i+1} 분석 오류: {date_error}")
                    continue
            
            print(f"📅 최종 예약 가능 날짜: {available_dates}")
            return {
                'available': len(available_dates) > 0,
                'dates': available_dates,
                'error': None
            }
            
        except Exception as e:
            print(f"❌ 예약 확인 중 오류 발생: {e}")
            print(f"📄 오류 상세: {traceback.format_exc()}")
            return {'available': False, 'dates': [], 'error': str(e)}
    
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
    
    def health_check(self):
        """모니터링 헬스체크"""
        current_time = datetime.now()
        
        # 마지막 체크로부터 너무 오래 지났는지 확인
        if self.last_check_time:
            time_diff = (current_time - self.last_check_time).total_seconds()
            if time_diff > self.check_interval * 2:  # 2배 이상 지연
                print(f"⚠️ 헬스체크 경고: 마지막 체크로부터 {time_diff:.0f}초 경과")
                return False
        
        return True
    
    def run_single_check(self):
        """단일 체크 실행"""
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"\n🔍 {current_time} - 심층상담 예약 상태 체크 중...")
            
            # 드라이버가 없거나 문제가 있으면 새로 생성
            if not self.driver:
                print("🌐 새 ChromeDriver 생성 중...")
                self.driver = self.setup_driver()
                if not self.driver:
                    raise Exception("ChromeDriver 생성 실패")
            
            # 예약 상태 확인
            result = self.check_reservation_availability()
            is_available = result['available']
            dates = result['dates']
            error = result.get('error')
            
            if error:
                print(f"⚠️ 체크 중 오류: {error}")
                if error in ['login_required', 'page_structure_unknown']:
                    # 심각한 오류 - 드라이버 재생성 필요
                    self.cleanup_driver()
                    self.consecutive_errors += 1
                    return False
            
            print(f"📅 발견된 날짜: {dates}")
            
            # 상태 변화 확인 및 알림
            if is_available and not self.last_status:
                # 새로운 예약 슬롯 발견!
                dates_str = ', '.join(dates[:5])
                message = f"심층상담 예약 가능! 날짜: {dates_str}"
                
                self.send_all_alerts(message)
                self.last_status = True
                
            elif not is_available and self.last_status:
                print(f"⚠️ {current_time} - 예약 슬롯 없어짐")
                self.last_status = False
                
            elif is_available:
                print(f"✅ {current_time} - 예약 계속 가능")
                
            else:
                print(f"⏳ {current_time} - 예약 대기 중...")
            
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
    
    def run_monitoring_loop(self):
        """메인 모니터링 루프"""
        print("🚀 마일스톤 소아과 심층상담 예약 모니터링 시작!")
        print("📍 완전 안정화 버전 - 동적 날짜 처리 및 자동 복구")
        print(f"🔄 {self.check_interval}초마다 자동 체크합니다...")
        print("🔔 예약 가능시 알림을 받으실 수 있습니다.")
        print("=" * 60)
        
        while True:
            try:
                # 헬스체크
                if not self.health_check():
                    print("⚠️ 헬스체크 실패 - 시스템 재초기화")
                    self.cleanup_driver()
                    self.consecutive_errors = 0
                
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
        print("✅ 모니터링 종료 완료")

def main():
    """메인 함수"""
    monitor = RobustReservationMonitor()
    try:
        monitor.run_monitoring_loop()
    except Exception as e:
        print(f"❌ 치명적 오류: {e}")
        print(f"📄 오류 상세: {traceback.format_exc()}")
    finally:
        monitor.cleanup_driver()

if __name__ == "__main__":
    main()
