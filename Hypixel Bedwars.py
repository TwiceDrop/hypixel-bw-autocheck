import requests
import schedule
import time
import os
from datetime import datetime

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

# 配置参数
INTERVAL_SECONDS = int(config['interval_seconds'])
MONITOR_PLAYER = config['monitor_player']
MONITOR_ENABLED = config['monitor_enabled'].lower() == 'true'

# 记录上次的数据
last_data = {}

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

def check_and_notify():
    global last_data
    current_data = get_player_data(MONITOR_PLAYER)

    if current_data is None:
        print("无法获取玩家数据")
        return

    if not last_data:
        last_data = current_data
        return

    changes = []
    for key in current_data:
        if current_data[key] != last_data[key]:
            changes.append(f"{key} 由 {last_data[key]} 变为 {current_data[key]}")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if changes:
        message = f"[{now}] 您好，{MONITOR_PLAYER}，您的数据发生了变化：\n" + "\n".join(changes)
        print(message)
        last_data = current_data
    else:
        print(f"[{now}] 您好，{MONITOR_PLAYER}，您的数据在过去的{INTERVAL_SECONDS}秒内没有发生变化。")

# 设置定时任务
if MONITOR_ENABLED:
    schedule.every(INTERVAL_SECONDS).seconds.do(check_and_notify)

print("开始监控玩家数据...")

while True:
    if MONITOR_ENABLED:
        schedule.run_pending()
    time.sleep(1)
