#!/usr/bin/env python3
"""
브라우저 상태와 시스템 감지 결과 비교
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def compare_states():
    options = Options()
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    
    try:
        url = "https://m.booking.naver.com/booking/13/bizes/635057/items/4867274?lang=ko&service-target=map-pc&startDate=2025-08-01&theme=place"
        print("🚀 예약 페이지 접속...")
        driver.get(url)
        time.sleep(10)
        
        print("🔍 현재 달력 상태 상세 분석:")
        print("=" * 50)
        
        # 모든 달력 버튼 분석
        calendar_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'calendar_date')]")
        
        available_dates = []
        unavailable_dates = []
        
        for btn in calendar_buttons:
            try:
                text = btn.text.strip().split('\n')[0]
                classes = btn.get_attribute('class') or ""
                is_enabled = btn.is_enabled()
                
                if text.isdigit() and 1 <= int(text) <= 31:
                    print(f"📅 {text}일:")
                    print(f"   클래스: {classes}")
                    print(f"   활성화: {is_enabled}")
                    
                    # 클릭 가능성 테스트
                    try:
                        # 실제로 클릭해보기 (테스트용)
                        if ('calendar_date' in classes and 
                            'unselectable' not in classes and 
                            'dayoff' not in classes and
                            is_enabled):
                            
                            print(f"   🎯 시스템 판단: 예약 가능")
                            available_dates.append(text)
                            
                            # 실제 클릭 테스트 (매우 짧게)
                            try:
                                btn.click()
                                time.sleep(0.5)
                                print(f"   ✅ 실제 클릭: 성공")
                            except Exception as e:
                                print(f"   ❌ 실제 클릭: 실패 ({e})")
                        else:
                            reasons = []
                            if 'unselectable' in classes:
                                reasons.append('unselectable')
                            if 'dayoff' in classes:
                                reasons.append('dayoff')
                            if not is_enabled:
                                reasons.append('disabled')
                            
                            print(f"   ❌ 시스템 판단: 예약 불가 ({', '.join(reasons)})")
                            unavailable_dates.append(text)
                    except Exception as e:
                        print(f"   ❌ 분석 실패: {e}")
                    
                    print()
            except:
                continue
        
        print("📊 최종 결과:")
        print(f"✅ 예약 가능: {sorted(available_dates)}")
        print(f"❌ 예약 불가: {sorted(unavailable_dates)}")
        
        print(f"\n💡 사용자가 확인한 날짜: 2일, 6일")
        print(f"🤖 시스템이 감지한 날짜: {sorted(available_dates)}")
        
        # 차이점 분석
        user_dates = set(['2', '6'])
        system_dates = set(available_dates)
        
        if user_dates == system_dates:
            print("✅ 완전 일치!")
        else:
            extra_dates = system_dates - user_dates
            missing_dates = user_dates - system_dates
            
            if extra_dates:
                print(f"🔍 시스템이 추가로 감지한 날짜: {sorted(extra_dates)}")
            if missing_dates:
                print(f"⚠️ 시스템이 놓친 날짜: {sorted(missing_dates)}")
        
        print("\n💡 브라우저에서 실제 달력을 확인해보세요!")
        print("   2일과 6일이 정말 클릭 가능한지 테스트해보고")
        print("   다른 날짜들도 클릭해보세요!")
        
        input("확인 후 Enter를 누르세요...")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    compare_states()
