# 📱 GitHub 저장소 생성 가이드

## 🚀 1단계: GitHub 저장소 생성 (2분)

### 1. GitHub 접속
1. https://github.com 접속
2. 로그인 (계정 없으면 회원가입)

### 2. 새 저장소 생성
1. **"New repository"** 또는 **"+"** 버튼 클릭
2. **Repository name**: `hospital-booking-bot` (또는 원하는 이름)
3. **Description**: `24시간 병원 예약 모니터링 텔레그램 봇`
4. **Public** 선택 (무료)
5. **"Create repository"** 클릭

### 3. 저장소 URL 복사
생성된 저장소 페이지에서 **HTTPS URL** 복사
예: `https://github.com/사용자명/hospital-booking-bot.git`

## 🔗 2단계: 로컬 코드 연결

터미널에서 다음 명령어 실행:

```bash
# GitHub 저장소 연결 (URL은 위에서 복사한 것으로 변경)
git remote add origin https://github.com/사용자명/hospital-booking-bot.git

# 코드 업로드
git branch -M main
git push -u origin main
```

## ✅ 완료 확인

GitHub 저장소 페이지에서 파일들이 업로드되었는지 확인:
- `cloud_integrated_bot.py` ✅
- `Procfile` ✅  
- `requirements.txt` ✅
- `README.md` ✅

## 🚂 3단계: Railway 배포

1. https://railway.app 접속
2. **"Login"** → GitHub 계정으로 로그인
3. **"New Project"** → **"Deploy from GitHub repo"**
4. 방금 만든 저장소 선택
5. **자동 배포 시작!** 🎉

## 🎯 배포 완료 확인

- 텔레그램에서 봇 시작 메시지 수신
- `/서버상태` 명령어로 클라우드 서버 확인
- **24시간 무료 클라우드 봇 완성!** ✅
