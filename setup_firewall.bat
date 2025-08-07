@echo off
echo Django 예약 시스템 방화벽 설정 중...

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

echo.
echo Windows 방화벽에서 8000번 포트를 허용하는 규칙을 추가합니다...
echo.

REM 인바운드 규칙 추가 (Django 서버)
netsh advfirewall firewall add rule name="Django Reservation System" dir=in action=allow protocol=TCP localport=8000

REM 아웃바운드 규칙 추가 (필요한 경우)
netsh advfirewall firewall add rule name="Django Reservation System Outbound" dir=out action=allow protocol=TCP localport=8000

echo.
echo 방화벽 설정이 완료되었습니다!
echo.
echo 접속 가능한 주소:
echo - 로컬: http://localhost:8000
echo - 내부 IP: http://192.168.0.2:8000
echo - 외부 IP: http://221.153.1.152:8000
echo.
echo 외부에서 접속하려면 공유기에서 포트 포워딩 설정이 필요할 수 있습니다.
echo.
pause 