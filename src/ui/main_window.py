from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QListWidget, 
                             QProgressBar, QFrame, QScrollArea)
from PySide6.QtCore import Qt, Slot

class MainWindowUI(QMainWindow):
    """
    메인 윈도우의 UI 구조 및 위젯 배치를 정의하는 클래스입니다.
    비즈니스 로직은 배제하고 순수 레이아웃 구성을 담당합니다.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warudo YouTube Live Link")
        self.resize(500, 700)
        self.option_inputs = [] # 투표 항목 입력 위젯 리스트
        self.bars = {} # 투표 진행 바 위젯 딕셔너리
        self.init_ui()

    def init_ui(self):
        """전체 UI 레이아웃을 초기화합니다."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 상단 헤더
        header = QLabel("Warudo YouTube Live Link by NEGU")
        header.setObjectName("headerTitle")
        layout.addWidget(header)

        # 상태 표시줄 (유튜브, 와루도 연결 상태)
        status_layout = QHBoxLayout()
        self.yt_status_label = QLabel("유튜브: 연결 안됨")
        self.yt_status_label.setObjectName("statusDisconnected")
        self.warudo_status_label = QLabel("와루도: 대기 중")
        self.warudo_status_label.setObjectName("statusDisconnected")
        status_layout.addWidget(self.yt_status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.warudo_status_label)
        layout.addLayout(status_layout)

        # URL 입력창
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("유튜브 라이브 URL 또는 Video ID 입력")
        layout.addWidget(self.url_input)

        self.connect_btn = QPushButton("유튜브 연결 시작")
        layout.addWidget(self.connect_btn)

        # 구분선
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # 투표 항목 설정 섹션
        layout.addWidget(QLabel("투표 항목 설정"))
        
        # 항목 입력을 위한 스크롤 영역
        self.options_scroll = QScrollArea()
        self.options_scroll.setWidgetResizable(True)
        self.options_scroll.setFixedHeight(180)
        self.options_scroll.setObjectName("optionsScroll")
        
        self.options_container = QWidget()
        self.options_layout = QVBoxLayout(self.options_container)
        self.options_layout.setAlignment(Qt.AlignTop)
        self.options_scroll.setWidget(self.options_container)
        layout.addWidget(self.options_scroll)
        
        self.add_opt_btn = QPushButton("+ 항목 추가")
        self.add_opt_btn.setObjectName("addOptionButton")
        layout.addWidget(self.add_opt_btn)

        # 투표 제어 버튼 (시작, 초기화, 테스트)
        vote_ctrl_layout = QHBoxLayout()
        self.start_vote_btn = QPushButton("투표 시작")
        self.reset_vote_btn = QPushButton("초기화")
        self.reset_vote_btn.setObjectName("stopButton")
        self.test_sync_btn = QPushButton("테스트 전송")
        
        vote_ctrl_layout.addWidget(self.start_vote_btn)
        vote_ctrl_layout.addWidget(self.reset_vote_btn)
        vote_ctrl_layout.addWidget(self.test_sync_btn)
        layout.addLayout(vote_ctrl_layout)

        # 실시간 투표 현황 표시 영역 (진행 바 출력 위치)
        self.vote_container = QFrame()
        self.vote_container.setObjectName("card")
        self.vote_layout = QVBoxLayout(self.vote_container)
        layout.addWidget(self.vote_container)

        # 채팅 로그 출력 영역
        layout.addWidget(QLabel("실시간 채팅 로그"))
        self.chat_log = QListWidget()
        layout.addWidget(self.chat_log)

    def add_option_field(self, text="", on_delete=None):
        """새로운 투표 항목 입력창 한 줄을 추가합니다."""
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 5, 0, 5)
        
        line_edit = QLineEdit(text)
        line_edit.setPlaceholderText("예: !1 또는 단어")
        self.option_inputs.append(line_edit)
        
        del_btn = QPushButton("삭제")
        del_btn.setObjectName("deleteOptionButton")
        del_btn.setFixedWidth(60)
        if on_delete:
            del_btn.clicked.connect(lambda: on_delete(row, line_edit))
        
        row_layout.addWidget(line_edit)
        row_layout.addWidget(del_btn)
        self.options_layout.addWidget(row)
        return line_edit

    def refresh_vote_display_area(self, options):
        """현재 투표 항목들에 맞춰 진행 바 영역을 다시 생성합니다."""
        # 기존 위젯 제거
        for i in reversed(range(self.vote_layout.count())): 
            item = self.vote_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                for j in reversed(range(item.layout().count())):
                    w = item.layout().itemAt(j).widget()
                    if w: w.setParent(None)
        
        self.bars = {}
        for opt in options:
            row = QHBoxLayout()
            label = QLabel(f"{opt}:")
            label.setFixedWidth(40)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setFormat("%v 표")
            self.bars[opt] = bar
            row.addWidget(label)
            row.addWidget(bar)
            self.vote_layout.addLayout(row)
        
        self.total_label = QLabel(f"총 투표수: 0")
        self.vote_layout.addWidget(self.total_label)

    def update_status_labels(self, yt_alive, yt_msg, warudo_connected):
        """네트워크 상태 레이블의 텍스트와 스타일(색상)을 업데이트합니다."""
        self.yt_status_label.setText(f"유튜브: {yt_msg}")
        self.yt_status_label.setObjectName("statusConnected" if yt_alive else "statusDisconnected")
        self.yt_status_label.setStyle(self.yt_status_label.style())

        if warudo_connected:
            self.warudo_status_label.setText("와루도: 연결됨")
            self.warudo_status_label.setObjectName("statusConnected")
        else:
            self.warudo_status_label.setText("와루도: 연결 안됨")
            self.warudo_status_label.setObjectName("statusDisconnected")
        self.warudo_status_label.setStyle(self.warudo_status_label.style())
