@echo off
echo Windows 시작 프로그램에 Django 서버 등록 중...

REM 시작 프로그램 폴더 경로
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

REM 시작 스크립트 복사
copy "start_server.bat" "%STARTUP_FOLDER%\DjangoReservationSystem.bat"

echo.
echo 시작 프로그램 등록이 완료되었습니다!
echo 이제 PC가 시작될 때 자동으로 Django 서버가 실행됩니다.
echo.
echo 등록된 파일: %STARTUP_FOLDER%\DjangoReservationSystem.bat
echo.
pause 