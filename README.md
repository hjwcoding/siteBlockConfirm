# 📘 프로젝트명
> 방화벽정보(IP,PORT) 열려 있는지 확인해 주는 툴

---

## 📖 개요
수작업으로 IP, PORT를 확인하는데 번거로움을 해결하기 위하여 개발

예시:
> 특정 IP/PORT의 연결 상태를 주기적으로 점검하고 문제가 있는 IP, PORT는 text형식으로 남도록 되어 있습니다.
> 사이트 : https://ko.rakko.tools/tools/15/
> Python + Playwright + schedule 라이브러리를 기반으로 개발되었습니다.

---

## ⚙️ 기술 스택
| 구분 | 기술 |
|------|------|
| 언어 | Python / JavaScript / TypeScript |

---

## 🧱 주요 기능
- ✅ 기능1: 대상 사이트의 IP 및 포트 자동 점검
- ✅ 기능2: 정상 : OPEN 비정상 : 그 외 문구(그 외 문구일 때 텍스트 형식으로 남음) 

---

# 1. 환경 세팅
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)

# 확인해야 할 사항
- https://ko.rakko.tools/tools/15/ 에서 **"데이터 수집에 실패했습니다. 입력 내용에 오류가 없는지 확인하십시오."** 문구가 나올 때 어떨 때 나오는지 정확히 확인이 안됨.
- 신분증 / 부동산 / 대법원 / 자동차 / 건강보험 / 시가표준액조회 (데이터 수집에 실패했습니다. 입력 내용에 오류가 없는지 확인하십시오.) 문구 왼쪽 사이트만 해당됨.
- 사이트가 정확히 동작하는지 알려면 예시 : curl -v "https://www.epost.go.kr/" --data "ip=27.101.203.224&port=80" 로 확인해야 함.
  
