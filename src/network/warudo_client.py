import json
from PySide6.QtCore import QObject, Signal, QUrl, QTimer
from PySide6.QtWebSockets import QWebSocket

class WarudoClient(QObject):
    """
    와루도(Warudo) 웹소켓 서버와 통신을 담당하는 클라이언트 클래스입니다.
    자동 재연결 기능을 포함합니다.
    """
    status_changed = Signal(bool) # 연결 상태 변경 시 발생하는 시그널
    message_received = Signal(dict) # 메시지 수신 시 발생하는 시그널

    def __init__(self, host="127.0.0.1", port=19190):
        super().__init__()
        self.url = QUrl(f"ws://{host}:{port}")
        self.client = QWebSocket()
        
        # 웹소켓 이벤트 연결
        self.client.connected.connect(self.on_connected)
        self.client.disconnected.connect(self.on_disconnected)
        self.client.textMessageReceived.connect(self.on_message_received)
        self.client.errorOccurred.connect(self.on_error)
        
        self.is_connected = False
        self.reconnect_timer = QTimer()
        self.reconnect_timer.setSingleShot(True)
        self.reconnect_timer.timeout.connect(self.start)

    def start(self):
        """와루도 서버에 연결을 시도합니다."""
        print(f"[DEBUG] 와루도({self.url.toString()}) 연결 시도 중...")
        self.client.open(self.url)

    def stop(self):
        """연결을 종료하고 재연결 타이머를 멈춥니다."""
        self.reconnect_timer.stop()
        self.client.close()

    def on_connected(self):
        print("[DEBUG] 와루도 연결 성공")
        self.is_connected = True
        self.status_changed.emit(True)

    def on_disconnected(self):
        print("[DEBUG] 와루도 연결 끊김")
        self.is_connected = False
        self.status_changed.emit(False)
        # 3초 후 자동으로 재연결 시도
        self.reconnect_timer.start(3000)

    def on_error(self, error):
        print(f"[DEBUG] 와루도 웹소켓 에러: {error}")

    def on_message_received(self, message):
        """서버로부터 메시지를 수신했을 때 실행됩니다."""
        try:
            data = json.loads(message)
            self.message_received.emit(data)
        except json.JSONDecodeError:
            pass

    def send(self, data):
        """JSON 데이터를 와루도 서버로 전송합니다."""
        if self.is_connected:
            message = json.dumps(data)
            self.client.sendTextMessage(message)
        else:
            # print("[DEBUG] 와루도에 연결되어 있지 않아 전송 실패")
            pass
