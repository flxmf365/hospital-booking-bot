#!/bin/bash
# 영유아 검진 예약 모니터링 종료 스크립트

echo "🛑 국가 영유아 검진 예약 모니터링 종료 중..."

# PID 파일 확인
if [ -f "infant_monitor.pid" ]; then
    PID=$(cat infant_monitor.pid)
    
    # 프로세스가 실행 중인지 확인
    if ps -p $PID > /dev/null; then
        echo "📋 프로세스 ID $PID 종료 중..."
        kill $PID
        
        # 종료 확인
        sleep 2
        if ps -p $PID > /dev/null; then
            echo "⚠️ 강제 종료 중..."
            kill -9 $PID
        fi
        
        echo "✅ 영유아 검진 모니터링이 종료되었습니다!"
    else
        echo "⚠️ 영유아 검진 모니터링 프로세스가 이미 종료되어 있습니다."
    fi
    
    # PID 파일 삭제
    rm infant_monitor.pid
else
    echo "❌ infant_monitor.pid 파일을 찾을 수 없습니다."
    echo "💡 수동으로 프로세스를 확인해보세요: ps aux | grep infant_checkup_monitor"
fi

echo ""
echo "🔄 다시 시작하려면: ./start_infant_monitor.sh"
