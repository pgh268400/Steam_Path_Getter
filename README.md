# Steam_Path_Getter
파이썬에서 쉽게 스팀 설치 경로를 획득 가능합니다.  
참고 : 같은 경로내에 내장된 VDFParse의 경우 [해당 프로젝트](https://github.com/shravan2x/Gameloop.Vdf)에 의존하고 있습니다.

# How to Use?
사용법은 아래와 같습니다. 같은 경로의 main.py를 실행해주시면 됩니다.

```python
from pprint import pprint
from module.module import SteamPath


steam_path = SteamPath()
pprint(steam_path.install_path)
pprint(steam_path.library_path)
pprint(steam_path.appinfo_path)
pprint(steam_path.library_data)
pprint(steam_path.app_info_dic)
pprint(steam_path.game_dir_data, width=100)
```
참고 : app_info_dic 의 데이터가 매우 크므로 한 줄씩 주석처리를 하면서 각각 출력을 확인하시는게 좋습니다.
