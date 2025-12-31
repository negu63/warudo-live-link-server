import pytchat
from PySide6.QtCore import QThread, Signal
import time
import traceback

class ChatWorker(QThread):
    """
    유튜브 라이브 채팅을 실시간으로 수집하는 백그라운드 스레드 클래스입니다.
    """
    chat_received = Signal(object) # 새로운 채팅 메시지를 받았을 때 발생하는 시그널
    status_changed = Signal(str, bool) # 유튜브 연결 상태가 변경되었을 때 발생하는 시그널

    def __init__(self, video_id):
        super().__init__()
        self.video_id = video_id
        self.active = True # 스레드 활성화 상태 제어

    def run(self):
        # 백그라운드 스레드에서 시그널 핸들러를 등록하려는 라이브러리(pytchat 등)의 에러를 방지하기 위해 
        # signal.signal 기능을 잠시 무력화합니다.
        import signal
        original_signal = signal.signal
        signal.signal = lambda s, h: None 
        
        try:
            print(f"\n[DEBUG] pytchat 연결 시도 중... Video ID: {self.video_id}")
            # interruptable=False는 내부적으로 시그널 핸들러 등록을 하지 않도록 함
            chat = pytchat.create(video_id=self.video_id, interruptable=False)
            
            # 시그널 복구
            signal.signal = original_signal
            
            # 연결 확인을 위해 잠시 대기
            time.sleep(1.5) 
            
            if not chat.is_alive():
                print(f"[DEBUG] pytchat.is_alive()가 False를 반환했습니다. (Video ID: {self.video_id})")
                self.status_changed.emit("라이브를 찾을 수 없거나 종료되었습니다. (ID/URL 확인 필요)", False)
                return

            print(f"[DEBUG] pytchat 연결 성공! 채팅 수집을 시작합니다.")
            self.status_changed.emit("연결됨", True)

            while chat.is_alive() and self.active:
                # 새로운 채팅 항목들을 가져와 리스트로 변환합니다.
                raw_items = chat.get().sync_items()
                items = list(raw_items) if raw_items else []
                
                if items:
                    for c in items:
                        self.chat_received.emit(c)
                time.sleep(0.1) # 과도한 루프 방지를 위한 짧은 대기

        except Exception as e:
            error_msg = f"에러 발생: {str(e)}"
            print(f"[DEBUG] {error_msg}")
            print(traceback.format_exc())
            self.status_changed.emit(error_msg, False)
        finally:
            self.active = False
            self.status_changed.emit("연결 종료", False)
            print("[DEBUG] ChatWorker 스레드 종료")

    def stop(self):
        """채팅 수집을 중단하고 스레드를 안전하게 종료합니다."""
        print("[DEBUG] ChatWorker 중지 요청됨")
        self.active = False
        self.wait()
