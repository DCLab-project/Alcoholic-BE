# BE

## 1. 저장소 목적
이 저장소는 **술안주 추천 AI 냉장고의 서버 및 오케스트레이션 로직**을 담당합니다.

프로젝트 계획서 기준으로 BE는 센서 이벤트 처리, 재고 상태 관리, 추천 요청 생성, DB/캐시 조회, RAG/LLM 연계, 추천 결과 반환의 중심 역할을 수행합니다.

## 2. 주요 역할
- 문열림/움직임 이벤트 수신 및 분기
- 식재료 인식 결과 재고 반영
- 주류 인식 결과와 재고를 결합한 추천 요청 생성
- 추천 캐시 조회 및 이력 저장
- 레시피 DB / 페어링 규칙 DB 기반 후보 조회
- 필요 시 LLM API 연계를 통한 설명 보완
- FE/디스플레이에 추천 결과 전달

## 3. 권장 구조
```bash
app/
  api/
  services/
  domain/
  repositories/
  schemas/
  clients/
  utils/
  config/
```

## 4. 핵심 도메인
- Inventory
- Alcohol
- Recipe
- PairingRule
- Recommendation
- Correction
- SensorEvent

## 5. 서버 설계 원칙
- 라우터는 입출력 처리만 담당합니다.
- 핵심 비즈니스 로직은 service/domain 계층에 둡니다.
- DB 접근은 repository 계층으로 분리합니다.
- 외부 API 호출은 client 계층으로 분리합니다.
- 추천 로직은 "입력 구성 → 후보 조회 → 점수화 → 결과 구성" 순서를 명확히 유지합니다.

## 6. 실행 방법
현재 PDF에는 실제 서버 프레임워크 및 실행 명령이 명시되어 있지 않으므로, 아래는 **초기 템플릿 예시**입니다.
실제 프로젝트 초기화 후 수정해주세요.

```bash
# example
pip install -r requirements.txt
python app/main.py
```

## 7. 환경 변수 예시
```bash
DATABASE_URL=
CACHE_URL=
LLM_API_KEY=
MODEL_SERVICE_URL=
```

## 8. BE에서 특히 중요하게 볼 것
- 이벤트 분기 정확성
- 재고 갱신의 일관성
- 동일 입력 재사용을 위한 캐시 전략
- 추천 설명과 추천 결과의 정합성
- 사용자 보정 반영 흐름
