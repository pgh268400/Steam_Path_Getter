import json
import subprocess
import sys
from typing import Any
import winreg
import os
import vdf

# SteamPath 객체를 통해 스팀 경로를 관리한다.
# SteamPath 의 설계도 (Class)
class SteamPath:
    # 전역적으로 사용할 상수들
    steam_apps = "steamapps" # 스팀 설치 경로의 steamapps 폴더 이름
    library_folders = "libraryfolders.vdf" # 스팀 설치 경로의 steamapps 폴더 안에 있는 libraryfolders.vdf 파일 이름
    app_cache = "appcache" # 스팀 설치 경로의 appcache 폴더 이름
    appinfo = "appinfo.vdf" # 스팀 설치 경로의 appcache 폴더 안에 있는 appinfo.vdf 파일 이름
    app_manifest = "appmanifest_{0}.acf" # 스팀 설치 경로의 steamapps 폴더 안에 있는 acf 파일 이름
    common = "common" # 스팀 설치 경로의 steamapps 폴더 안에 있는 common 폴더 이름

    def __init__(self) -> None:
        self.__install_path : str = self.__get_steam_path()
        self.__library_path : str = os.path.join(self.__install_path, SteamPath.steam_apps, SteamPath.library_folders)
        self.__appinfo_path : str = os.path.join(self.__install_path, SteamPath.app_cache, SteamPath.appinfo)

        # libraryfolders.vdf를 파싱해서 설치된 스팀 게임들의 app 번호를 리스트로 반환한다
        self.__library_data = self.parse_library_vdf(self.__library_path)
        
        # 스팀 설치 경로 + appcache 안에 appinfo.vdf를 파싱한다
        self.__app_info_dic = self.parse_appinfo_vdf(self.__appinfo_path,  self.__library_data)

        # library 데이터와 appinfo 데이터를 합쳐서 게임 디렉토리 경로를 만든다
        self.__game_dir_data = self.get_game_dirs(self.__app_info_dic, self.__library_data)

    # 스팀 설치 경로를 자동으로 읽어오는 함수
    def __get_steam_path(self) -> str:
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
    def __run_process(self, command: list[str]) -> str:
        # command ex) ['ls', '-al']

        # 명령어 실행 후, 결과를 output에 저장
        # text = True : output을 text로 저장,
        # encoding은 기본이 cp949라 문제 없이 저장할려면 utf-8로 설정
        try:
            output: str = subprocess.check_output(
                command, stderr=subprocess.STDOUT, encoding="utf-8", text=True
            )
        except Exception as e:
            raise Exception("Command execution failed", command, e)

        return output
    
    # libraryfolders.vdf 파일을 경로로 받아서 파싱하는 함수
    def parse_library_vdf(self, vdf_file_path : str):
        dic : dict = vdf.load(open(vdf_file_path, encoding="utf-8"))

        inner : dict = dic['libraryfolders']

        result : list[dict] = []

        for key, value in inner.items():
            base_path : str = value['path']
            apps : list[str] = list(value['apps'])

            result.append({"base_path" : base_path, "apps" : apps})
        return result

    # appinfo.vdf 파일을 딕셔너리로 파싱하는 함수
    def parse_appinfo_vdf(self, appinfo_path : str, library_data : list) -> dict[Any, Any]:
        # library_data 에서 apps 를 모두 가져온다
        app_id_lst : list[str] = []
        for element in library_data:
            app_id_lst.extend(element['apps'])

        result = self.__run_process(["VDFparse.exe", appinfo_path, *app_id_lst])
        # result를 json 형식으로 변환
        json_dict : dict = json.loads(result)
        return json_dict

    # app id 리스트를 받아서 acf 파일을 파싱하는 함수
    # def parse_acf(self, steam_path : str, app_id_lst : list[str]) -> list[dict]:
    #     acf_lst : list[dict] = []

    #     for app_id in app_id_lst:
    #         acf_file_path = os.path.join(steam_path, SteamPath.steam_apps, SteamPath.app_manifest.format(app_id))

    #         # acf 파일이 없다면 그냥 넘어간다
    #         # (libraryfolders.vdf 파일은 스팀을 재시작해야 반영되기 때문에 게임을 삭제한 직후라면 acf 파일이 없을 수 있다.)
    #         if not os.path.isfile(acf_file_path):
    #             continue
                
    #         # 확장자는 acf 로 끝나지만 vdf 와 구조가 똑같기 때문에 vdf 라이브러리로 파싱 가능하다.
    #         dic : dict = vdf.load(open(acf_file_path, encoding="utf-8"))
    #         acf_lst.append(dic['AppState'])

    #     return acf_lst

    def get_game_dirs(self, app_info_dic, library_data : list):
        result = []

        # 각 app_id 에 대해 경로를 매칭시키는 데이터를 생성
        app_id_match = {}
        for i, element in enumerate(library_data):
            for app_id in element['apps']:
                app_id_match[app_id] = element['base_path']

        for element in app_info_dic['datasets']:
            appinfo = element['data']['appinfo']
            app_id = str(appinfo['appid'])
            base_path = app_id_match[app_id]

            config = appinfo['config']
            executable = ""
            
            installdir = config['installdir']

            for key, value in config['launch'].items():
                # 실행 경로의 경우 리눅스, 윈도우, 맥에 따라 다르나
                # 해당 코드는 윈도우에서만 동작하기 때문에 윈도우 경로만 추출한다.

                # 'config' 키가 존재하고, 'oslist' 키도 존재하면 해당 값을 가져오고, 그렇지 않으면 None을 반환
                oslist = value.get('config', {}).get('oslist', None)
                executable : str = value['executable']

                if executable == "":
                    continue

                if oslist == "windows" or "exe" in executable or "bat" in executable or "cmd" in executable:
                    full_path = os.path.join(base_path, SteamPath.steam_apps, SteamPath.common, installdir, executable)

                    # 실행 파일이 존재해야만 경로를 저장한다.
                    if os.path.isfile(full_path):
                        break

            
            full_path = os.path.join(base_path, SteamPath.steam_apps, SteamPath.common, installdir, executable)

            # result에 모든 데이터를 담는다
            result.append({
                "app_id" : app_id,
                "base_path" : base_path,
                "executable" : executable,
                "installdir" : installdir,
                "full_path" : full_path
            })

        return result

    # 프로퍼티로 데이터 반환
    @property
    def install_path(self) -> str:
        return self.__install_path
    
    @property
    def library_path(self) -> str:
        return self.__library_path
    
    @property
    def appinfo_path(self) -> str:
        return self.__appinfo_path
    
    @property
    def library_data(self) -> list:
        return self.__library_data
    
    @property
    def app_info_dic(self) -> dict:
        return self.__app_info_dic
    
    @property
    def game_dir_data(self) -> list:
        return self.__game_dir_data



