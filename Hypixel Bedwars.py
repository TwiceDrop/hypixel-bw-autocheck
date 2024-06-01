import requests
import time

# Hypixel API密钥
API_KEY = 'Your API Key'

def get_player_data(player_name):
    # 请求玩家UUID
    uuid_response = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{player_name}')

    if uuid_response.status_code == 200:
        player_uuid = uuid_response.json()['id']

        # 请求玩家数据
        player_data_response = requests.get(f'https://api.hypixel.net/player?key={API_KEY}&uuid={player_uuid}')

        if player_data_response.status_code == 200:
            player_data = player_data_response.json()

            if player_data['success'] and player_data['player']:
                # 获取起床战争等级
                bedwars_level = player_data['player'].get('achievements', {}).get('bedwars_level', '数据不可用')
                return bedwars_level
            else:
                return "该玩家尚未收录或未在Hypixel服务器上玩过"
        else:
            return "无法获取玩家数据"
    else:
        return "无效的玩家名称"


while True:
    # 获取用户输入并转换为小写
    check_input = input("请输入你要查询的玩家名称 (输入0退出): ").lower()

    if check_input == '0':
        print("退出程序")
        break

    player_level = get_player_data(check_input)
    print(check_input + "的起床战争等级为: " + str(player_level))
    print("请等待5s继续查询")
    time.sleep(5)