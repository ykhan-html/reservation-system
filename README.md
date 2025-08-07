# Django 예약 시스템

Django와 Django REST Framework를 사용하여 만든 온라인 예약 시스템입니다.

## 주요 기능

- **서비스 관리**: 다양한 서비스 등록 및 관리
- **카테고리 관리**: 서비스 카테고리 분류 및 관리
- **예약 시스템**: 실시간 예약 가능 시간 확인 및 예약
- **사용자 관리**: 회원가입, 로그인, 예약 내역 조회
- **리뷰 시스템**: 완료된 예약에 대한 리뷰 작성
- **관리자 기능**: 예약 상태 관리, 서비스 관리, 상품 관리
- **영업시간 관리**: 요일별 영업시간 설정
- **상품 관리**: 카테고리별 상품 관리, 이미지 업로드, 재고 관리

## 기술 스택

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Database**: SQLite (개발용)
- **Frontend**: Bootstrap 5, JavaScript (Vanilla)
- **Authentication**: Django 기본 인증 시스템
- **File Upload**: Pillow (이미지 처리)

## 설치 및 실행

### 1. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 데이터베이스 마이그레이션

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 슈퍼유저 생성

```bash
python manage.py createsuperuser
```

### 5. 초기 데이터 로드

```bash
python manage.py load_initial_data
```

### 6. 개발 서버 실행

```bash
python manage.py runserver
```

## API 엔드포인트

### 카테고리 관련
- `GET /api/categories/` - 카테고리 목록 조회 (인증 필요)
- `POST /api/categories/` - 새 카테고리 생성 (관리자만)
- `GET /api/categories/{id}/` - 특정 카테고리 조회 (인증 필요)
- `PUT /api/categories/{id}/` - 카테고리 수정 (관리자만)
- `DELETE /api/categories/{id}/` - 카테고리 삭제 (관리자만)

### 서비스 관련
- `GET /api/services/` - 서비스 목록 조회
- `POST /api/services/` - 새 서비스 생성 (관리자만)
- `GET /api/services/{id}/` - 특정 서비스 조회
- `PUT /api/services/{id}/` - 서비스 수정 (관리자만)
- `DELETE /api/services/{id}/` - 서비스 삭제 (관리자만)
- `GET /api/services/{id}/available_times/?date=YYYY-MM-DD` - 예약 가능 시간 조회
- `GET /api/services/featured/` - 추천 서비스 조회
- `GET /api/services/by_category/?category_id={id}` - 카테고리별 서비스 조회

### 예약 관련
- `GET /api/reservations/` - 예약 목록 조회 (인증 필요)
- `POST /api/reservations/` - 새 예약 생성 (인증 필요)
- `GET /api/reservations/{id}/` - 특정 예약 조회 (인증 필요)
- `PUT /api/reservations/{id}/` - 예약 수정 (인증 필요)
- `DELETE /api/reservations/{id}/` - 예약 삭제 (인증 필요)
- `POST /api/reservations/{id}/cancel/` - 예약 취소 (인증 필요)
- `POST /api/reservations/{id}/confirm/` - 예약 확정 (관리자만)
- `POST /api/reservations/{id}/complete/` - 예약 완료 (관리자만)
- `GET /api/reservations/upcoming/` - 다가오는 예약 조회 (인증 필요)
- `GET /api/reservations/history/` - 예약 내역 조회 (인증 필요)

### 리뷰 관련
- `GET /api/reviews/` - 리뷰 목록 조회 (인증 필요)
- `POST /api/reviews/` - 새 리뷰 작성 (인증 필요)
- `GET /api/reviews/service_reviews/?service_id={id}` - 서비스별 리뷰 조회

### 영업시간 관련
- `GET /api/business-hours/` - 영업시간 조회

### 사용자 관련
- `GET /api/users/` - 사용자 정보 조회 (인증 필요)
- `POST /api/register/` - 회원가입
- `POST /api/login/` - 로그인
- `POST /api/logout/` - 로그아웃 (인증 필요)
- `PUT /api/profile/update/` - 프로필 수정 (인증 필요)

## 페이지 구조

### 사용자 페이지
- `/` - 메인 페이지 (서비스 조회, 예약)
- `/register/` - 회원가입 페이지
- `/login/` - 로그인 페이지
- `/profile/` - 회원관리 페이지 (예약 내역, 리뷰, 프로필 수정)

### 관리자 페이지
- `/admin/` - Django 관리자 페이지
- `/product-management/` - 상품관리 페이지 (관리자만 접근 가능)

## 상품 관리 기능

### 카테고리 관리
- 카테고리 추가/수정/삭제
- 카테고리 활성화/비활성화
- 카테고리별 설명 관리

### 서비스 관리
- 서비스 추가/수정/삭제
- 이미지 업로드 지원
- 재고 수량 관리
- 추천 서비스 설정
- 예약 가능 시간 설정
- 카테고리 분류

### 주요 기능
- **이미지 업로드**: 서비스별 이미지 등록
- **재고 관리**: 서비스별 재고 수량 추적
- **추천 서비스**: 특별한 서비스 강조 표시
- **카테고리 분류**: 서비스를 카테고리별로 분류
- **예약 설정**: 최소/최대 예약 가능 시간 설정

## 데이터베이스 모델

### Category (카테고리)
- `name`: 카테고리명
- `description`: 카테고리 설명
- `is_active`: 활성화 여부
- `created_at`: 생성일
- `updated_at`: 수정일

### Service (서비스)
- `category`: 카테고리 (ForeignKey)
- `name`: 서비스명
- `description`: 서비스 설명
- `price`: 가격
- `duration`: 소요시간 (분)
- `image`: 서비스 이미지
- `is_active`: 활성화 여부
- `is_featured`: 추천 서비스 여부
- `stock_quantity`: 재고 수량
- `min_advance_booking`: 최소 예약 가능 시간 (시간)
- `max_advance_booking`: 최대 예약 가능 시간 (일)
- `created_at`: 생성일
- `updated_at`: 수정일

## 사용법

### 1. 관리자 계정으로 로그인
```bash
python manage.py createsuperuser
```

### 2. 상품 관리 페이지 접근
- 관리자로 로그인 후 메인 페이지에서 "상품관리" 링크 클릭
- 또는 직접 `/product-management/` 접근

### 3. 카테고리 관리
- "카테고리 관리" 탭에서 카테고리 추가/수정/삭제
- 카테고리명, 설명, 활성화 상태 설정

### 4. 서비스 관리
- "서비스 관리" 탭에서 서비스 추가/수정/삭제
- 이미지 업로드, 가격, 소요시간, 재고 등 설정
- 카테고리 선택 및 추천 서비스 설정

### 5. 예약 관리
- Django 관리자 페이지에서 예약 상태 관리
- 예약 확정, 완료, 취소 처리

## 개발 환경 설정

### 환경 변수
- `DEBUG=True` (개발 환경)
- `LANGUAGE_CODE='ko-kr'` (한국어)
- `TIME_ZONE='Asia/Seoul'` (한국 시간)

### 미디어 파일
- 업로드된 이미지는 `media/services/` 디렉토리에 저장
- 개발 환경에서는 자동으로 미디어 파일 서빙

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 