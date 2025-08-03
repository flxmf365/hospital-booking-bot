#!/bin/bash
# AWS 클라우드 서버 설정 스크립트

echo "🚀 AWS 클라우드 서버 설정을 시작합니다!"
echo "📋 이 스크립트를 AWS Ubuntu 서버에서 실행하세요."

# 시스템 업데이트
echo "📦 시스템 업데이트 중..."
sudo apt update && sudo apt upgrade -y

# Python 및 필수 패키지 설치
echo "🐍 Python 및 필수 패키지 설치 중..."
sudo apt install python3 python3-pip wget curl unzip xvfb -y

# Chrome 브라우저 설치
echo "🌐 Chrome 브라우저 설치 중..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt update
sudo apt install google-chrome-stable -y

# ChromeDriver 설치
echo "🚗 ChromeDriver 설치 중..."
CHROME_VERSION=$(google-chrome --version | cut -d " " -f3 | cut -d "." -f1-3)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Python 패키지 설치
echo "📚 Python 패키지 설치 중..."
pip3 install selenium requests

# 가상 디스플레이 설정 (헤드리스 환경)
echo "🖥️ 가상 디스플레이 설정 중..."
sudo apt install xvfb -y

# 모니터링 디렉토리 생성
echo "📁 모니터링 디렉토리 생성 중..."
mkdir -p ~/hospital_monitoring
cd ~/hospital_monitoring

echo "✅ AWS 클라우드 서버 설정 완료!"
echo "📋 다음 단계:"
echo "1. 모니터링 스크립트 업로드"
echo "2. 텔레그램 봇 설정"
echo "3. 자동 실행 설정"
echo ""
echo "🔗 현재 디렉토리: $(pwd)"
echo "🎯 준비 완료! 모니터링 스크립트를 업로드하세요."
