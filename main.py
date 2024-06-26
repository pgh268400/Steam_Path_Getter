from pprint import pprint
from module.module import SteamPath


steam_path = SteamPath()
pprint(steam_path.install_path)
# pprint(steam_path.library_path)
# pprint(steam_path.appinfo_path)
# pprint(steam_path.library_data)
# pprint(steam_path.app_info_dic)
pprint(steam_path.game_dir_data, width=100)

