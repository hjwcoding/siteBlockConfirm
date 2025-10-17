# Firewall Port Checker (Web)

Electron 데스크톱 앱을 웹 애플리케이션으로 변환한 프로젝트입니다.

## 기능

- 도메인 DNS 조회 (nslookup)
- 방화벽 포트 체크 목록 관리
- 도메인 목록 관리
- 실시간 로그 표시

## 프로젝트 구조

```
firewall-checker-web/
├── src/                 # React 프론트엔드 소스
│   ├── index.html      # HTML 템플릿
│   ├── index.js        # React 엔트리 포인트
│   └── App.jsx         # 메인 React 컴포넌트
├── data/               # JSON 데이터 파일
│   ├── domain_list.json
│   └── tuples_list.json
├── server.js           # Express 백엔드 서버
├── webpack.config.js   # Webpack 설정
└── package.json
```

## 설치 및 실행

### 1. 의존성 설치
```bash
npm install
```

### 2. 프론트엔드 빌드
```bash
npm run build
```

### 3. 서버 실행
```bash
npm start
```

서버가 실행되면 브라우저에서 `http://localhost:3000` 으로 접속하세요.

## 개발 모드

개발 중에는 webpack-dev-server를 사용할 수 있습니다:

```bash
# 터미널 1: 백엔드 서버 실행
npm start

# 터미널 2: 프론트엔드 개발 서버 실행
npm run dev
```

개발 서버는 `http://localhost:8080` 에서 실행되며, API 요청은 자동으로 `http://localhost:3000` 으로 프록시됩니다.

## API 엔드포인트

### POST /api/check-domain
도메인의 IP 주소를 조회합니다.

**요청:**
```json
{
  "domain": "example.com"
}
```

**응답:**
```json
{
  "success": true,
  "message": "IP 확인 성공! :: 93.184.216.34",
  "ip": "93.184.216.34"
}
```

### GET /api/tuples
방화벽 포트 체크 목록을 가져옵니다.

### GET /api/domains
도메인 목록을 가져옵니다.

## 네트워크에서 접근하기

다른 PC에서 접근하려면 다음 단계를 따르세요:

### 1. 서버 실행

```bash
npm start
```

실행하면 자동으로 네트워크 IP 주소가 표시됩니다:

```
=================================================
🚀 Firewall Checker Web Server is running!
=================================================

로컬 접속: http://localhost:3000
네트워크 접속: http://192.168.1.100:3000

다른 PC에서 접속하려면:
1. 브라우저에서 http://192.168.1.100:3000 접속
2. Windows 방화벽에서 포트 3000 허용 필요
=================================================
```

### 2. 방화벽 설정 (자동)

**PowerShell을 관리자 권한으로 실행**한 후:

```powershell
.\setup-firewall.ps1
```

### 3. 방화벽 설정 (수동)

PowerShell(관리자 권한)에서:

```powershell
New-NetFirewallRule -DisplayName "Firewall Checker Web" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow
```

### 4. 다른 PC에서 접속

같은 네트워크에 연결된 다른 PC의 브라우저에서:

```
http://192.168.1.100:3000
```

(서버 실행 시 표시된 IP 주소 사용)

### 자세한 가이드

더 자세한 설정 방법은 `네트워크_접속_가이드.md` 파일을 참고하세요.

## 기술 스택

- **백엔드:** Node.js, Express
- **프론트엔드:** React, Material-UI
- **빌드 도구:** Webpack, Babel

## 기존 Electron 앱과의 차이점

| 항목 | Electron 앱 | 웹 앱 |
|------|------------|-------|
| 실행 방법 | 각 PC에 설치 필요 | 브라우저에서 URL 접속 |
| 배포 | .exe 파일 배포 | 서버 한 곳에서 운영 |
| 통신 방식 | IPC (window.api) | REST API (fetch) |
| 플랫폼 | Windows, macOS, Linux | 모든 브라우저 |
