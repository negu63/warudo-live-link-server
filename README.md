# Warudo Live Link Server

Warudo와 유튜브 라이브 채팅을 실시간으로 연결하여 시청자 참여형 콘텐츠(투표 등)를 구현할 수 있게 도와주는 서버 애플리케이션입니다.

<img width="250" height="484.5" alt="Warudo_Youtube_LiveLInk_Server2" src="https://github.com/user-attachments/assets/229266fc-2208-497c-b0e5-39b9b0276e08" />

## 🚀 주요 기능

- **실시간 유튜브 채팅 연동**: 유튜브 라이브 URL 입력만으로 실시간 채팅을 모니터링합니다.
- **와루도(Warudo) WebSocket 통신**: 전용 WebSocket 클라이언트를 통해 실시간 투표 데이터를 와루도로 전송합니다.
- **동적 투표 시스템**: 투표 항목을 자유롭게 추가/삭제할 수 있으며, 특정 키워드에 반응하여 숫자를 집계합니다.
- **직관적인 관리 UI**: GUI를 통해 연결 상태 확인 및 투표 현황을 실시간으로 파악할 수 있습니다.
- **데이터 전송 최적화 (Throttling)**: 모든 채팅에 대해 즉각 응답하는 대신, 0.5초 간격으로 데이터를 모아서 일괄 전송하여 네트워크 부하를 최소화하고 안정적인 동기화를 제공합니다.

## 🛠 설치 및 시작하기

### 필수 요구 사항
- **Python 3.10 이상**이 설치되어 있어야 합니다.
- **와루도 플러그인**: 와루도와 연동하려면 [WarudoModding](https://github.com/negu63/WarudoModding) 플러그인이 와루도에 설치되어 있어야 합니다.

### 의존성 설치
본 프로젝트의 필수 라이브러리를 설치합니다.

```bash
pip install -r requirements.txt
```

또는 직접 설치 시:
```bash
pip install PySide6 pytchat
```

### 실행 방법
프로젝트 루트 디렉토리에서 아래 명령어를 실행합니다.

```bash
python run.py
```

## 📖 사용 방법

1. **유튜브 연결**: 실행 후 상단 '유튜브 라이브 URL' 입력창에 스트리밍 주소를 넣고 `유튜브 연결 시작` 버튼을 누릅니다.
2. **투표 항목 설정**: 하단의 투표 설정 영역에서 시청자가 입력할 키워드(예: 1, 2, A, B 등)를 입력합니다.
3. **투표 시작**: `투표 시작` 버튼을 누르면 그때부터 입력된 키워드에 대한 채팅 집계가 시작됩니다. 투표 진행 사항은 0.5초마다 집계하여 한 번에 와루도 플러그인으로 전송됩니다.
4. **와루도 연동**: 와루도에 [WarudoModding](https://github.com/negu63/WarudoModding) 플러그인을 설치한 후, 와루도에서 본 서버(`ws://localhost:19190`)에 접속하여 데이터를 수신하도록 설정합니다.

## 🔗 와루도 연동 데이터 규격

서버는 다음과 같은 JSON 형식의 데이터를 WebSocket을 통해 전송합니다.

### 투표 업데이트 (`UpdateVote`)
```json
{
  "action": "UpdateVote",
  "data": {
    "options": [
      { "name": "항목1", "count": 10 },
      { "name": "항목2", "count": 5 },
      ...
    ]
  }
}
```

### 투표 초기화 (`ClearVotes`)
```json
{
  "action": "ClearVotes"
}
```

## 📁 디렉토리 구조
- `src/`: 핵심 소스 코드 (UI, Network, Core 로직)
- `assets/`: 스타일시트 및 리소스 파일
- `run.py`: 애플리케이션 진입점(Entry point)
