# Django 골프 예약 시스템

골프 레슨 예약을 위한 Django 기반 웹 애플리케이션입니다.

## 주요 기능

- 🏌️ 골프 레슨 예약 시스템
- 👥 사용자 회원가입/로그인
- 👨‍💼 서비스 제공자 관리
- 📅 예약 관리 및 상태 변경
- ⭐ 리뷰 시스템
- 🎨 모던한 골프 테마 디자인

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 데이터베이스 마이그레이션
```bash
python manage.py migrate
```

### 3. 초기 데이터 로드
```bash
python manage.py load_initial_data
```

### 4. 서버 시작
```bash
python manage.py runserver 0.0.0.0:8000
```

## 접속 주소

- **로컬 접속**: http://localhost:8000
- **내부 IP 접속**: http://192.168.0.2:8000
- **외부 IP 접속**: http://221.153.1.152:8000

## Windows 서비스로 실행

### 방법 1: 수동 시작
```bash
start_server.bat
```

### 방법 2: 자동 시작 프로그램 등록
```bash
create_startup_script.bat
```

### 방법 3: Windows 서비스로 등록
```bash
install_service.bat
```

## 방화벽 설정

외부 접속을 위해 방화벽 설정이 필요합니다:
```bash
setup_firewall.bat
```

## 관리자 계정

- **관리자 페이지**: http://localhost:8000/admin/
- **기본 관리자 계정**: admin / admin123

## 서비스 제공자 계정

- **김태호**: kimtaeho / password123
- **이준호**: leejunho / password123
- **박성민**: parksungmin / password123
- **최영수**: choiyoungsu / password123

## 프로젝트 구조

```
reservation_system/
├── booking/                 # 예약 시스템 앱
│   ├── models.py           # 데이터 모델
│   ├── views.py            # 뷰 및 API
│   ├── serializers.py      # API 시리얼라이저
│   ├── admin.py            # 관리자 인터페이스
│   └── templates/          # HTML 템플릿
├── reservation_system/      # 프로젝트 설정
│   ├── settings.py         # Django 설정
│   └── urls.py             # URL 설정
├── requirements.txt         # Python 의존성
└── manage.py              # Django 관리 스크립트
```

## 기술 스택

- **Backend**: Django 4.2.7, Django REST Framework
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite
- **Authentication**: Django Session Authentication

## 라이선스

MIT License 