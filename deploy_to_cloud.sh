#!/bin/bash
# 클라우드 서버 배포 스크립트
# AWS EC2 인스턴스에 모니터링 시스템 배포

echo "🚀 마일스톤 소아과 모니터링 시스템 클라우드 배포"
echo "📋 이 스크립트를 로컬 Mac에서 실행하여 AWS 서버로 파일을 전송합니다."
echo ""

# 사용자 입력 받기
read -p "🔑 AWS EC2 키 파일 경로 (.pem): " KEY_FILE
read -p "🌐 AWS EC2 서버 주소 (예: ubuntu@ec2-xx-xx-xx-xx.compute-1.amazonaws.com): " SERVER_ADDRESS

# 키 파일 권한 설정
echo "🔐 키 파일 권한 설정 중..."
chmod 400 "$KEY_FILE"

# 서버에 디렉토리 생성
echo "📁 서버에 모니터링 디렉토리 생성 중..."
ssh -i "$KEY_FILE" "$SERVER_ADDRESS" "mkdir -p ~/hospital_monitoring"

# 파일 전송
echo "📤 모니터링 파일들을 서버로 전송 중..."
scp -i "$KEY_FILE" cloud_setup.sh "$SERVER_ADDRESS":~/hospital_monitoring/
scp -i "$KEY_FILE" cloud_monitor.py "$SERVER_ADDRESS":~/hospital_monitoring/

# 서버에서 설정 스크립트 실행
echo "⚙️ 서버에서 환경 설정 중..."
ssh -i "$KEY_FILE" "$SERVER_ADDRESS" "cd ~/hospital_monitoring && chmod +x cloud_setup.sh && ./cloud_setup.sh"

# 자동 실행 설정
echo "🔄 자동 실행 설정 중..."
ssh -i "$KEY_FILE" "$SERVER_ADDRESS" "cd ~/hospital_monitoring && python3 -c \"
import os
crontab_line = '@reboot cd ~/hospital_monitoring && python3 cloud_monitor.py >> monitor.log 2>&1 &'
os.system('(crontab -l 2>/dev/null; echo \\\"' + crontab_line + '\\\") | crontab -')
print('✅ 자동 실행 설정 완료')
\""

# 모니터링 시작
echo "🚀 모니터링 시작 중..."
ssh -i "$KEY_FILE" "$SERVER_ADDRESS" "cd ~/hospital_monitoring && nohup python3 cloud_monitor.py >> monitor.log 2>&1 &"

echo ""
echo "🎉 클라우드 배포 완료!"
echo "📱 텔레그램으로 시작 알림이 전송됩니다."
echo ""
echo "📋 관리 명령어:"
echo "  로그 확인: ssh -i $KEY_FILE $SERVER_ADDRESS 'tail -f ~/hospital_monitoring/monitor.log'"
echo "  상태 확인: ssh -i $KEY_FILE $SERVER_ADDRESS 'ps aux | grep cloud_monitor'"
echo "  재시작: ssh -i $KEY_FILE $SERVER_ADDRESS 'pkill -f cloud_monitor && cd ~/hospital_monitoring && nohup python3 cloud_monitor.py >> monitor.log 2>&1 &'"
echo ""
echo "✅ 24시간 무중단 모니터링이 시작되었습니다!"
