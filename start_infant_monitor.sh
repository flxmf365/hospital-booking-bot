#!/bin/bash
# 영유아 검진 예약 모니터링 시작 스크립트

echo "🚀 국가 영유아 검진 예약 모니터링 시작!"
echo "🏥 마일스톤소아청소년과의원 - 생후 4개월 이상"
echo "📍 백그라운드에서 실행됩니다."
echo "🔔 예약 가능시 알림을 받으실 수 있습니다."
echo ""

# 현재 디렉토리로 이동
cd "$(dirname "$0")"

# 백그라운드에서 모니터링 시작
nohup python3 infant_checkup_monitor.py > infant_monitor.log 2>&1 &

# 프로세스 ID 저장
echo $! > infant_monitor.pid

echo "✅ 영유아 검진 모니터링이 백그라운드에서 시작되었습니다!"
echo "📋 프로세스 ID: $(cat infant_monitor.pid)"
echo "📄 로그 파일: infant_monitor.log"
echo ""
echo "🛑 모니터링 종료하려면: ./stop_infant_monitor.sh"
echo "📊 상태 확인하려면: ./check_infant_status.sh"
