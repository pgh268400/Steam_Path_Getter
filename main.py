from pprint import pprint
import sys
import winreg
import os
import vdf

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

# libraryfolders.vdf 파일을 경로로 받아서 파싱하는 함수
def parse_library_vdf(vdf_file_path : str) -> list[str]:
    dic : dict = vdf.load(open(vdf_file_path, encoding="utf-8"))
    inner : dict = dic['libraryfolders']

    acf_path_lst : list[str] = []

    for key, value in inner.items():
        base_path : str = value['path']
        apps : list[str] = list(value['apps'])

        for app in apps:
            app_path : str = os.path.join(base_path, steam_apps, app_manifest.format(app))
            acf_path_lst.append(app_path)
    return acf_path_lst

# acf 파일 목록을 받아서 파싱하는 함수
def parse_acf(acf_file_path_lst : list[str]) -> list[dict]:
    acf_lst : list[dict] = []

    for acf_file_path in acf_file_path_lst:
        # acf_file_path 파일이 없다면 그냥 넘어간다
        # (libraryfolders.vdf 파일은 스팀을 재시작해야 반영되기 때문에 게임을 삭제한 직후라면 acf 파일이 없을 수 있다.)
        if not os.path.isfile(acf_file_path):
            continue
            
        # 확장자는 acf 로 끝나지만 vdf 와 구조가 똑같기 때문에 vdf 라이브러리로 파싱 가능하다.
        dic : dict = vdf.load(open(acf_file_path, encoding="utf-8"))
        acf_lst.append(dic['AppState'])

    pprint(acf_lst)
    return acf_lst

    
# 예제 사용
install_path = steam_install_path_read()

print(f"스팀 설치 경로 : {install_path}")

# 스팀 설치 경로 + appcache 안에 appinfo.vdf를 파싱한다


# 스팀 설치 경로의 steamapps 폴더 안에 있는 libraryfolders.vdf 파일을 파싱한다.
# libraryfolders.vdf 파일은 각 드라이브에 설치된 스팀 게임들의 경로를 가진 acf 파일의 이름과 경로를 가지고 있다.

# ex) C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf
library_file_path = os.path.join(install_path, steam_apps, library_folders)

# libraryfolders.vdf 파일을 파싱한다.
acf_path_lst : list[str] = parse_library_vdf(library_file_path)

print("acf 파일 목록 :")
pprint(acf_path_lst)

# acf 파일 목록을 파싱해서 각 acf 파일의 정보를 가진 리스트를 만든다.
acf_lst : list[dict] = parse_acf(acf_path_lst)