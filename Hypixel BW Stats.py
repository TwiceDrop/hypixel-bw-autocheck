import requests
import os
import time

# 读取配置文件
def read_config():
    config = {}
    if not os.path.exists('config.txt'):
        with open('config.txt', 'w') as f:
            f.write('interval_seconds = 10\n')
            f.write('monitor_player = your_minecraft_username\n')
            f.write('monitor_enabled = True\n')
    with open('config.txt', 'r') as f:
        for line in f:
            key, value = line.strip().split(' = ')
            config[key] = value
    return config

config = read_config()

# Hypixel API密钥
API_KEY = 'input your api key here'

def get_player_data(player_name):
    try:
        # 请求玩家UUID
        uuid_response = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{player_name}')
        uuid_response.raise_for_status()

        player_uuid = uuid_response.json()['id']

        # 请求玩家数据
        player_data_response = requests.get(f'https://api.hypixel.net/player?key={API_KEY}&uuid={player_uuid}')
        player_data_response.raise_for_status()

        player_data = player_data_response.json()

        if player_data['success'] and player_data['player']:
            stats = player_data['player'].get('stats', {}).get('Bedwars', {})
            achievements = player_data['player'].get('achievements', {})
            data = {
                'stars': achievements.get('bedwars_level', 0),
                'final_kills': stats.get('final_kills_bedwars', 0),
                'kills': stats.get('bedwars_killer', 0),
                'final_deaths': stats.get('final_deaths_bedwars', 0),
                'deaths': stats.get('deaths_bedwars', 0),
                'beds_broken': stats.get('beds_broken_bedwars', 0),
                'wins': stats.get('wins_bedwars', 0),
                'fkdr': round(stats.get('final_kills_bedwars', 0) / max(stats.get('final_deaths_bedwars', 1), 1), 3),
                'kdr': round(stats.get('bedwars_killer', 0) / max(stats.get('deaths_bedwars', 1), 1), 3)
            }
            return data
        else:
            return None
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

while True:
    check_input = input("请输入你要查询的玩家名称 (输入0退出): ").lower()

    if check_input == '0':
        print("退出程序")
        break

    player_data = get_player_data(check_input)
    if player_data is not None:
        print(f"{check_input}的起床战争数据：")
        for key, value in player_data.items():
            print(f"{key}: {value}")
    else:
        print("无法获取玩家数据")
