from PySide6.QtCore import QObject, Signal

class VotingManager(QObject):
    """
    투표 데이터와 상태를 관리하는 클래스입니다.
    UI 로직과 분리되어 투표 카운트, 옵션 설정 등을 담당합니다.
    """
    votes_updated = Signal() # 투표 데이터가 변경되었을 때 UI에 알리는 시그널
    
    def __init__(self):
        super().__init__()
        self.vote_options = ["!1", "!2", "!3"] # 기본 투표 옵션
        self.votes = {opt: 0 for opt in self.vote_options} # 각 옵션별 투표수
        self.total_votes = 0 # 전체 투표수
        self.is_active = False # 현재 투표가 진행 중인지 여부
        self.needs_sync = False # 와루도와 데이터 동기화가 필요한지 여부

    def setup_options(self, options):
        """새로운 투표 항목들을 설정하고 투표를 초기화합니다."""
        print(f"[DEBUG] VotingManager setup_options: {options}")
        self.vote_options = options
        self.votes = {opt: 0 for opt in self.vote_options}
        self.total_votes = 0
        self.votes_updated.emit()

    def process_vote(self, message):
        """채팅 메시지를 분석하여 투표 항목에 해당하면 카운트를 올립니다."""
        if not self.is_active:
            return False
            
        msg = message.strip()
        for opt in self.vote_options:
            if msg == opt:
                self.votes[opt] += 1
                self.total_votes += 1
                self.needs_sync = True
                self.votes_updated.emit()
                return True
        return False

    def reset(self):
        """투표 카운트를 0으로 초기화합니다."""
        self.votes = {opt: 0 for opt in self.vote_options}
        self.total_votes = 0
        self.needs_sync = True
        self.votes_updated.emit()

    def get_sync_data(self):
        """와루도로 전송할 데이터 형식을 생성합니다."""
        return {
            "action": "UpdateVote",
            "data": {
                "options": [{"name": opt, "count": count} for opt, count in self.votes.items()],
            }
        }
