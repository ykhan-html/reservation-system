@echo off
echo Django 예약 시스템 서비스 설치 중...

REM 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 관리자 권한 확인됨
) else (
    echo 이 스크립트는 관리자 권한이 필요합니다.
    echo 관리자 권한으로 다시 실행해주세요.
    pause
    exit /b 1
)

REM pywin32 패키지 설치
echo pywin32 패키지 설치 중...
pip install pywin32

REM 서비스 설치
echo Django 서비스 설치 중...
python install_service.py install

REM 서비스 시작
echo Django 서비스 시작 중...
python install_service.py start

echo.
echo 서비스 설치가 완료되었습니다!
echo 서비스 이름: DjangoReservationSystem
echo 서비스 상태 확인: services.msc
echo 서비스 중지: python install_service.py stop
echo 서비스 제거: python install_service.py remove
echo.
pause 