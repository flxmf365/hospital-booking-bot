#!/bin/bash
# 예약 모니터링 시작 스크립트

echo "🚀 마일스톤 소아과 예약 모니터링 시작!"
echo "📍 백그라운드에서 실행됩니다."
echo "🔔 예약 가능시 알림을 받으실 수 있습니다."
echo ""

# 현재 디렉토리로 이동
cd "$(dirname "$0")"

# 백그라운드에서 모니터링 시작
nohup python3 stable_alert.py > monitor.log 2>&1 &

# 프로세스 ID 저장
echo $! > monitor.pid

echo "✅ 모니터링이 백그라운드에서 시작되었습니다!"
echo "📋 프로세스 ID: $(cat monitor.pid)"
echo "📄 로그 파일: monitor.log"
echo ""
echo "🛑 모니터링 종료하려면: ./stop_monitor.sh"
echo "📊 상태 확인하려면: ./check_status.sh"
