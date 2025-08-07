@echo off
echo Django 예약 시스템 서버 시작 중...

REM 프로젝트 디렉토리로 이동
cd /d C:\tempodiall

REM Django 서버 시작
echo 서버가 시작되었습니다.
echo.
echo ========================================
echo 접속 주소:
echo - 로컬: http://localhost:8000
echo - 내부 IP: http://192.168.0.2:8000
echo - 외부 IP: http://221.153.1.152:8000
echo ========================================
echo.
echo 서버를 중지하려면 Ctrl+C를 누르세요.
echo.

python manage.py runserver 0.0.0.0:8000

pause 