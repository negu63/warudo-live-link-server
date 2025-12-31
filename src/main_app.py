import sys
import os
from PySide6.QtCore import QTimer, Slot, Qt
from PySide6.QtWidgets import QPushButton

# 소스 경로를 시스템 패스에 추가하여 내부 모듈을 임포트할 수 있도록 합니다.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindowUI
from core.voting_manager import VotingManager
from network.warudo_client import WarudoClient
from network.chat_worker import ChatWorker
from utils.helpers import extract_video_id

class MainApp(MainWindowUI):
    """
    애플리케이션의 메인 클래스입니다.
    UI와 비즈니스 로직(투표 관리, 네트워크 클라이언트)을 연결하고 제어합니다.
    """
    def __init__(self):
        super().__init__()
        
        # 각 기능을 담당하는 모듈 인스턴스화
        self.voting_manager = VotingManager()
        self.warudo_client = WarudoClient()
        self.chat_worker = None
        
        # 주기적인 와루도 데이터 동기화를 위한 타이머 (0.5초 간격)
        self.sync_timer = QTimer()
        self.sync_timer.setInterval(500)
        self.sync_timer.timeout.connect(self.sync_with_warudo)

        # 초기 UI 상태 설정 (기본 투표 항목 추가 및 영역 생성)
        for opt in self.voting_manager.vote_options:
            self.add_option_field(opt, self.remove_option_field)
        self.refresh_vote_display_area(self.voting_manager.vote_options)
        
        # UI 이벤트와 함수 연결
        self.connect_btn.clicked.connect(self.toggle_youtube_connection)
        self.add_opt_btn.clicked.connect(lambda: self.add_option_field("", self.remove_option_field))
        self.start_vote_btn.clicked.connect(self.toggle_voting)
        self.reset_vote_btn.clicked.connect(self.reset_votes)
        self.test_sync_btn.clicked.connect(self.send_test_packet)
        
        # 시그널 연결 (데이터 변경 시 UI 업데이트 등)
        self.voting_manager.votes_updated.connect(self.update_vote_display)
        self.warudo_client.status_changed.connect(self.on_warudo_status_changed)
        
        # 와루도 서버 연결 시작 및 스타일 로드
        self.warudo_client.start()
        self.load_styles()
        print("[DEBUG] MainApp initialized")

    def load_styles(self):
        """외부 QSS 파일을 로드하여 UI 스타일을 적용합니다."""
        style_paths = ["assets/style.qss", "style.qss", "assets/styles.qss", "styles.qss"]
        for p in style_paths:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
                break

    def remove_option_field(self, row_widget, line_edit):
        """투표 항목 입력줄을 삭제합니다."""
        if len(self.option_inputs) <= 1:
            return
        self.option_inputs.remove(line_edit)
        row_widget.setParent(None)
        row_widget.deleteLater()

    @Slot(bool)
    def on_warudo_status_changed(self, connected):
        """와루도 연결 상태가 변경되었을 때 호출됩니다."""
        yt_msg = self.yt_status_label.text().replace("유튜브: ", "")
        yt_alive = self.yt_status_label.objectName() == "statusConnected"
        self.update_status_labels(yt_alive, yt_msg, connected)

    def toggle_youtube_connection(self):
        """유튜브 연결을 시작하거나 종료합니다."""
        if self.chat_worker and self.chat_worker.isRunning():
            self.chat_worker.stop()
            self.connect_btn.setText("유튜브 연결 시작")
            self.chat_log.addItem("--- 연결이 종료되었습니다 ---")
            self.update_status_labels(False, "연결 안됨", self.warudo_client.is_connected)
            return

        url = self.url_input.text().strip()
        video_id = extract_video_id(url)
        
        if not video_id:
            self.chat_log.addItem("오류: 올바른 URL 또는 ID를 입력하세요.")
            return

        self.chat_log.addItem(f"연결 시도 중... (ID: {video_id})")
        self.chat_worker = ChatWorker(video_id)
        self.chat_worker.chat_received.connect(self.on_chat_received)
        self.chat_worker.status_changed.connect(self.on_yt_status_changed)
        self.chat_worker.start()
        self.connect_btn.setText("유튜브 연결 종료")

    @Slot(str, bool)
    def on_yt_status_changed(self, msg, alive):
        """유튜브 연결 상태 변화를 로그와 UI에 반영합니다."""
        self.update_status_labels(alive, msg, self.warudo_client.is_connected)
        if alive:
            self.chat_log.addItem("--- 유튜브 연결 성공 ---")
        else:
            self.chat_log.addItem(f"--- 유튜브 연결 해제/실패: {msg} ---")

    @Slot(object)
    def on_chat_received(self, chat):
        """새로운 채팅이 들어왔을 때 처리합니다."""
        # 로그 창에 채팅 추가
        item = f"[{chat.author.name}]: {chat.message}"
        self.chat_log.addItem(item)
        if self.chat_log.count() > 50:
            self.chat_log.takeItem(0)
        self.chat_log.scrollToBottom()

        # 투표 로직 처리 (투표 진행 중인 경우)
        if self.voting_manager.process_vote(chat.message):
            # 투표 반영 시 UI 업데이트는 votes_updated 시그널을 통해 이루어짐
            pass

    def update_vote_display(self):
        """UI상의 투표수와 진행 바를 최신 데이터로 업데이트합니다."""
        self.total_label.setText(f"총 투표수: {self.voting_manager.total_votes}")
        for opt, count in self.voting_manager.votes.items():
            if opt in self.bars:
                self.bars[opt].setValue(count)

    def sync_with_warudo(self):
        """투표 데이터에 변경 사항이 있을 경우 와루도로 전송합니다."""
        if self.voting_manager.needs_sync:
            self.warudo_client.send(self.voting_manager.get_sync_data())
            self.voting_manager.needs_sync = False

    def toggle_voting(self):
        """투표를 시작하거나 종료합니다."""
        print(f"[DEBUG] toggle_voting called. Current state: {self.voting_manager.is_active}")
        if not self.voting_manager.is_active:
            # 설정한 항목 모으기
            new_options = []
            for inp in self.option_inputs:
                txt = inp.text().strip()
                if txt and txt not in new_options:
                    new_options.append(txt)
            
            if not new_options:
                self.chat_log.addItem("오류: 최소 하나 이상의 투표 항목이 필요합니다.")
                return
                
            # 투표 시작 설정
            self.voting_manager.setup_options(new_options)
            self.refresh_vote_display_area(new_options)
            
            self.set_ui_enabled(False) # 진행 중 옵션 수정 금지
            self.sync_timer.start()
            self.voting_manager.is_active = True
            self.voting_manager.needs_sync = True
            self.sync_with_warudo()
            
            self.start_vote_btn.setText("투표 종료")
            self.start_vote_btn.setObjectName("stopButton")
            print("[DEBUG] Voting started")
        else:
            # 투표 종료 설정
            self.voting_manager.is_active = False
            self.set_ui_enabled(True)
            self.sync_timer.stop()
            self.voting_manager.needs_sync = True
            self.sync_with_warudo() # 마지막 데이터 전송
            
            self.start_vote_btn.setText("투표 시작")
            self.start_vote_btn.setObjectName("")
            print("[DEBUG] Voting stopped")
        
        # 스타일 강제 갱신
        self.start_vote_btn.style().unpolish(self.start_vote_btn)
        self.start_vote_btn.style().polish(self.start_vote_btn)

    def set_ui_enabled(self, enabled):
        """투표 진행 중에는 설정을 변경하지 못하도록 관련 위젯들을 잠급니다."""
        for inp in self.option_inputs:
            inp.setEnabled(enabled)
        self.add_opt_btn.setEnabled(enabled)
        for btn in self.options_container.findChildren(QPushButton, "deleteOptionButton"):
            btn.setEnabled(enabled)

    def reset_votes(self):
        """투표를 초기화하고 와루도에도 리셋 명령을 보냅니다."""
        self.voting_manager.reset()
        self.update_vote_display()
        self.warudo_client.send({"action": "ClearVotes"})
        self.chat_log.addItem("--- 투표가 초기화되었습니다 ---")

    def send_test_packet(self):
        """와루도 통신 테스트를 위한 패킷을 전송합니다."""
        if not hasattr(self, 'test_value'): self.test_value = 10
        else: self.test_value += 10

        test_options = []
        for inp in self.option_inputs:
            txt = inp.text().strip()
            if txt and txt not in test_options: test_options.append(txt)
        
        if not test_options:
            self.chat_log.addItem("오류: 테스트를 위한 투표 항목이 없습니다.")
            return
            
        data = {
            "action": "UpdateVote",
            "data": {"options": [{"name": opt, "count": self.test_value} for opt in test_options]}
        }
        self.warudo_client.send(data)
        self.chat_log.addItem(f"--- 와루도로 테스트 패킷을 전송했습니다 (값: {self.test_value}) ---")

    def closeEvent(self, event):
        """프로그램 종료 시 열려 있는 연결들을 닫습니다."""
        if self.chat_worker: self.chat_worker.stop()
        self.warudo_client.stop()
        event.accept()
