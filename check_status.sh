#!/bin/bash
# 예약 모니터링 상태 확인 스크립트

echo "📊 마일스톤 소아과 예약 모니터링 상태 확인"
echo "=" * 50

# PID 파일 확인
if [ -f "monitor.pid" ]; then
    PID=$(cat monitor.pid)
    
    # 프로세스가 실행 중인지 확인
    if ps -p $PID > /dev/null; then
        echo "✅ 모니터링 실행 중"
        echo "📋 프로세스 ID: $PID"
        
        # 실행 시간 확인
        START_TIME=$(ps -o lstart= -p $PID)
        echo "⏰ 시작 시간: $START_TIME"
        
        # CPU 및 메모리 사용량
        echo "💻 리소스 사용량:"
        ps -o pid,pcpu,pmem,time,command -p $PID
        
    else
        echo "❌ 모니터링이 실행되고 있지 않습니다."
        echo "💡 다시 시작하려면: ./start_monitor.sh"
        rm monitor.pid
    fi
else
    echo "❌ 모니터링이 시작되지 않았습니다."
    echo "🚀 시작하려면: ./start_monitor.sh"
fi

echo ""

# 로그 파일 확인
if [ -f "monitor.log" ]; then
    echo "📄 최근 로그 (마지막 10줄):"
    echo "---"
    tail -10 monitor.log
else
    echo "📄 로그 파일이 없습니다."
fi

echo ""
echo "🔄 새로고침: ./check_status.sh"
echo "🛑 종료: ./stop_monitor.sh"
