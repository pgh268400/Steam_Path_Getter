from dataclasses import dataclass

# 딕셔너리 대신 내보낼 데이터 클래스
@dataclass
class GameDirData:
    app_id: str
    base_path: str
    executable: str
    installdir: str
    full_path: str

# library data 에서 내보낼 데이터 클래스
@dataclass
class SteamLibrary:
    base_path: str
    apps: list[str]