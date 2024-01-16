import json
from pprint import pprint
import subprocess
import sys
from typing import Any
import winreg
import os

# 전역적으로 사용할 상수들
steam_apps = "steamapps" # 스팀 설치 경로의 steamapps 폴더 이름
library_folders = "libraryfolders.vdf" # 스팀 설치 경로의 steamapps 폴더 안에 있는 libraryfolders.vdf 파일 이름
app_manifest = "appmanifest_{0}.acf" # 스팀 설치 경로의 steamapps 폴더 안에 있는 acf 파일 이름

# 스팀 설치 경로를 자동으로 읽어오는 함수
def steam_install_path_read() -> str:
    # 시스템이 32비트인지 64비트인지 확인
    is_64bit = sys.maxsize > 2**32

    # 시스템 아키텍처에 따라 올바른 레지스트리 경로 설정
    if is_64bit:
        registry_path = r"SOFTWARE\Wow6432Node\Valve\Steam"
    else:
        registry_path = r"SOFTWARE\Valve\Steam"

    try:
        # 레지스트리 키 열기
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_READ)

        install_path : str = ""

        # InstallPath 값 읽기
        install_path, _ = winreg.QueryValueEx(key, "InstallPath")

        # 레지스트리 키 닫기
        winreg.CloseKey(key)
        return install_path

    # 예외는 호출자쪽에 맡긴다.
    except FileNotFoundError:
        raise FileNotFoundError("It looks like Steam isn't installed.")
    except Exception as e:
        raise e


# 프로세스 실행하고 결과를 반환하는 함수
def run_process(command: list[str]) -> str:
    # command ex) ['ls', '-al']

    # 명령어 실행 후, 결과를 output에 저장
    # text = True : output을 text로 저장,
    # encoding은 기본이 cp949라 문제 없이 저장할려면 utf-8로 설정
    try:
        output: str = subprocess.check_output(
            command, stderr=subprocess.STDOUT, encoding="utf-8", text=True
        )
    except Exception as e:
        raise Exception("명령어 실행에 실패했습니다", command)

    return output

# appinfo.vdf 파일을 딕셔너리로 파싱하는 함수
def read_appinfo_vdf(appinfo_path : str) -> dict[Any, Any]:
    result = run_process(["VDFparse.exe", appinfo_path])
    # result를 json 형식으로 변환
    json_dict : dict = json.loads(result)
    return json_dict

# 예제 사용
install_path = steam_install_path_read()

print(f"스팀 설치 경로 : {install_path}")

# 스팀 설치 경로 + appcache 안에 appinfo.vdf를 파싱한다
appinfo_path = os.path.join(install_path, "appcache", "appinfo.vdf")
result = read_appinfo_vdf(appinfo_path)

# for element in result["datasets"]:
#     pprint(element)

# data json 파일로 저장
with open("appinfo.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=4)
