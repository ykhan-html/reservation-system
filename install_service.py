import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import time
import subprocess
import threading

class DjangoService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DjangoReservationSystem"
    _svc_display_name_ = "Django Reservation System"
    _svc_description_ = "골프 예약 시스템 Django 서버"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = False

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False

    def SvcDoRun(self):
        self.running = True
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                             servicemanager.PYS_SERVICE_STARTED,
                             (self._svc_name_, ''))
        self.main()

    def main(self):
        # Django 프로젝트 디렉토리로 이동
        os.chdir(r'C:\tempodiall')
        
        # Django 서버 실행
        while self.running:
            try:
                # Django 서버 시작
                process = subprocess.Popen([
                    sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'
                ], cwd=r'C:\tempodiall')
                
                # 서비스가 중지될 때까지 대기
                while self.running and process.poll() is None:
                    time.sleep(1)
                
                if process.poll() is not None:
                    # 프로세스가 종료된 경우 재시작
                    time.sleep(5)
                    
            except Exception as e:
                servicemanager.LogErrorMsg(f"Django 서비스 오류: {str(e)}")
                time.sleep(10)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DjangoService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(DjangoService) 