import sys
import os

# src 폴더의 경로를 시스템 패스(sys.path)에 추가하여 
# 내부 모듈(ui, core, network 등)을 직접 임포트할 수 있게 설정합니다.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from PySide6.QtWidgets import QApplication
from main_app import MainApp

if __name__ == "__main__":
    # Qt 애플리케이션 생성
    app = QApplication(sys.argv)
    
    # 메인 윈도우 생성 및 표시
    window = MainApp()
    window.show()
    
    # 이벤트 루프 시작 및 프로그램 종료 대기
    sys.exit(app.exec())
