# 📍 우리 지역 체크인

## 소개

**우리 지역 체크인**은 방문한 지역에 대한 기록을 남기고 관리하는 웹 서비스입니다. 
지역별 방문 현황과 만족도를 통계로 확인하고, 저장된 기록을 검색·필터링·내보내기할 수 있습니다.
FastAPI 백엔드와 Streamlit 프론트엔드로 만들어진 간단하면서도 기능이 풍부한 서비스입니다.

---

## 🎯 주요 기능

### 기록 관리
- ✅ **기록 입력**: 이름, 지역, 만족도(1~5), 메모로 방문 기록 저장
- ✅ **기록 조회**: 전체 기록 또는 사용자별 기록 조회
- ✅ **기록 삭제**: 저장된 기록 중 특정 기록 삭제

### 통계 및 분석
- ✅ **지역별 통계**: 지역별 방문 횟수와 평균 만족도 그래프
- ✅ **전체 통계**: 총 기록 수, 참여자 수, 전체 평균 만족도 표시
- ✅ **사용자별 통계**: 사용자가 남긴 기록 수와 평균 만족도

### 검색 및 필터
- ✅ **지역 필터**: 특정 지역의 기록만 조회
- ✅ **만족도 필터**: 설정한 최소 만족도 이상의 기록만 표시
- ✅ **메모 검색**: 메모에 포함된 키워드로 기록 검색

### 데이터 관리
- ✅ **CSV 내보내기**: 필터가 적용된 기록을 CSV 파일로 다운로드 (엑셀 한글 호환)
- ✅ **JSONL 저장**: 기록을 JSONL 형식으로 안전하게 저장

### UI/UX
- ✅ **탭 기반 인터페이스**: "기록 남기기", "내 기록", "전체 현황" 3개 탭으로 구성
- ✅ **사이드바 필터**: 모든 탭에서 공유되는 검색 조건
- ✅ **반응형 레이아웃**: wide 레이아웃으로 스크롤 최소화

---

## 🛠️ 기술 스택

| 레이어 | 기술 |
|-------|------|
| **백엔드** | FastAPI, Uvicorn |
| **프론트엔드** | Streamlit, Pandas |
| **데이터 저장** | JSONL 파일 |
| **언어** | Python 3.9+ |

---

## 🚀 로컬 실행 방법

### 1️⃣ Conda 환경 생성

```bash
conda create -n my_service python=3.9
conda activate my_service
```

### 2️⃣ 의존성 설치

```bash
# 백엔드 + 프론트엔드 모든 의존성 설치
pip install fastapi==0.115.0 uvicorn==0.30.6 streamlit==1.38.0 pandas==2.2.2 requests==2.32.3
```

### 3️⃣ 백엔드 실행 (터미널 1)

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**예상 출력:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4️⃣ 프론트엔드 실행 (터미널 2)

```bash
cd frontend
streamlit run app.py --server.port 8501
```

**예상 출력:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### 5️⃣ 브라우저에서 접속

```
http://localhost:8501
```

---

## 📁 프로젝트 구조

```
my_service/
├── backend/
│   ├── main.py                 # FastAPI 백엔드 서버
│   ├── requirements.txt
│   ├── data/
│   │   └── records.jsonl       # 저장된 기록 (JSONL 형식)
│   └── Dockerfile
├── frontend/
│   ├── app.py                  # Streamlit 프론트엔드
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 📝 API 엔드포인트

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/locations` | 사용 가능한 지역 목록 |
| POST | `/records` | 새 기록 저장 |
| GET | `/records` | 전체 기록 조회 (필터 가능) |
| GET | `/records/user/{user_name}` | 사용자별 기록 조회 |
| GET | `/records/export.csv` | 기록을 CSV로 내보내기 |
| GET | `/stats` | 전체 통계 조회 |
| DELETE | `/records/{record_id}` | 특정 기록 삭제 |

---

## 💾 데이터 형식

### 저장된 기록 (JSONL)
```json
{"id": "abc123de", "user_name": "김철수", "region": "강남", "score": 4, "memo": "점심 맛집", "lat": 37.5, "lon": 127.0, "created_at": "2026-08-22T12:30:00+09:00"}
```

### CSV 내보내기
| id | user_name | region | score | memo | lat | lon | created_at |
|----|-----------|--------|-------|------|-----|-----|-----------|
| abc123de | 김철수 | 강남 | 4 | 점심 맛집 | 37.5 | 127.0 | 2026-08-22T12:30:00+09:00 |

---

## 🐛 문제 해결

### 백엔드 연결 안 됨
```
백엔드 서버(8000번)에 연결할 수 없습니다.
→ 터미널 1에서 백엔드가 실행 중인지 확인
```

### 포트가 이미 사용 중
```bash
# 다른 포트로 실행
python -m uvicorn main:app --port 8001
streamlit run app.py --server.port 8502
```

### CSV 한글이 깨짐
→ 파일을 UTF-8 with BOM 형식으로 열어야 합니다 (엑셀에서 자동 처리)

---

## 📌 주의사항

- 기록은 `backend/data/records.jsonl` 파일에 저장됩니다
- 파일을 삭제하면 모든 기록이 손실됩니다
- CSV 다운로드 시 필터가 적용된 기록만 포함됩니다
- 데모 지도는 저장된 기록과 무관하게 랜덤 좌표를 표시합니다

---

## 📄 라이선스

이 프로젝트는 학습용으로 제작되었습니다.

---

**마지막 업데이트**: 2026-08-22
