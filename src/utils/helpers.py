import re

def extract_video_id(url):
    """
    다양한 형태의 유튜브 URL 또는 Video ID 문자열에서 11자리 고유 ID를 추출합니다.
    
    추출 가능한 예시:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/live/VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - VIDEO_ID (직접 입력)
    """
    url = url.strip()
    
    # 이미 11자리이고 ID 형식에 맞으면 그대로 반환
    if len(url) == 11 and re.match(r"^[0-9A-Za-z_-]{11}$", url):
        return url
    
    # 다양한 URL 패턴 정의
    patterns = [
        r"v=([0-9A-Za-z_-]{11})",
        r"\/live\/([0-9A-Za-z_-]{11})",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
        r"\/v\/([0-9A-Za-z_-]{11})",
        r"\/embed\/([0-9A-Za-z_-]{11})"
    ]
    
    for p in patterns:
        match = re.search(p, url)
        if match:
            return match.group(1)
            
    return None
