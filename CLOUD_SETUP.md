# 🌐 24시간 클라우드 모니터링 설정 가이드

## 📋 개요
컴퓨터를 끄더라도 24시간 작동하는 영유아검진 모니터링 시스템을 클라우드에 배포하는 방법입니다.

## 🚀 빠른 배포 옵션들

### 옵션 1: Heroku (무료/간단)
```bash
# 1. Heroku CLI 설치
brew install heroku/brew/heroku

# 2. 로그인
heroku login

# 3. 앱 생성
heroku create infant-monitor-app

# 4. 배포
git add .
git commit -m "Deploy infant monitoring"
git push heroku main
```

### 옵션 2: Railway (무료/간단)
1. https://railway.app 접속
2. GitHub 연결
3. 프로젝트 배포
4. 자동으로 24시간 실행

### 옵션 3: Google Cloud Run (무료 한도)
```bash
# 1. Google Cloud CLI 설치
brew install google-cloud-sdk

# 2. 로그인
gcloud auth login

# 3. 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID

# 4. 배포
gcloud run deploy infant-monitor --source .
```

## 📱 클라우드 버전 특징

### ✅ 장점
- 🔄 **24시간 작동**: 컴퓨터 꺼도 계속 실행
- 📱 **텔레그램 전용**: 클라우드에서는 텔레그램만 사용
- 🔍 **안정적 모니터링**: 1분마다 체크
- 📊 **로그 기록**: 모든 활동 기록
- 🚨 **오류 복구**: 자동 재시도 기능

### ⚠️ 주의사항
- macOS 알림/팝업/음성은 클라우드에서 불가능
- 텔레그램 알림만 사용
- 무료 서비스는 월 사용량 제한 있음

## 🛠️ 필요한 파일들
- `cloud_deploy.py` - 클라우드용 모니터링 스크립트
- `requirements.txt` - 필요한 라이브러리
- `Procfile` - Heroku 배포용 (자동 생성 예정)
- `Dockerfile` - Docker 배포용 (자동 생성 예정)

## 📞 지원
클라우드 배포를 원하시면 어떤 옵션을 선호하시는지 알려주세요:
1. **Heroku** - 가장 간단, 무료
2. **Railway** - 매우 간단, 무료
3. **Google Cloud** - 안정적, 무료 한도
4. **로컬 컴퓨터 유지** - 현재 방식 유지

## 💡 권장사항
처음 사용하시는 경우 **Railway**를 추천합니다. 가장 간단하고 안정적입니다.
