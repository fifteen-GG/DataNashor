from utils.calc_gold import calc_gold
from metadata import MetaDataParser
from client import ReplayClient
import os
import requests
import json
from time import sleep

from requests.packages import urllib3
from utils.send_serial import send_serial

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


LIVE_CLIENT_DATA_API_ROOT = 'https://127.0.0.1:2999/liveclientdata/'


class ReplayParser():
    """
    Replay Parser class for parsing League of Legends replay files (.rofl)

    replay_file_dir: Directory of League of Legends replay files. Defaults to C:\Users\username\Documents\League of Legends\Replays
    game_dir: Directory of League of Legends game files. Defaults to C:\Riot Games\League of Legends
    interval: Interval between each request to the Live Client Data API. Defaults to 0.8 seconds
    player_data_keys: Keys to parse from Live Client Data API. Defaults to ['summonerName', 'championName', 'isDead', 'level', 'scores', 'items', 'team']
    """

    def __init__(
            self,
            replay_file_dir=os.environ['USERPROFILE'] +
        '/Documents/League of Legends/Replays',
            game_dir='C:/Riot Games/League of Legends',
            interval=0.8,
            player_data_keys=[
                'summonerName',
                'championName',
                'isDead',
                'level',
                'scores',
                'items',
                'team',
            ]):

        self.replay_file_dir = replay_file_dir
        self.game_dir = game_dir
        self.interval = interval
        self.replay_files = os.listdir(replay_file_dir)
        self.metadata = MetaDataParser(replay_file_dir)
        self.player_data_keys = player_data_keys

    def parse(self):
        """
        Parse all replay files in the replay_file_dir directory
        """
        for replay_file in self.replay_files:
            print(f'Parsing {replay_file}')

            client = ReplayClient(
                game_dir=self.game_dir,
                replay_file_dir=self.replay_file_dir,
                replay_file=replay_file)

            client.run_client()

            result = []
            loaded = False
            game_time_count = 0
            prev_game_time = 0

            game_meta_data = self.metadata.parse(replay_file)

            metadata_filename = 'meta' + replay_file.split('.')[0] + '.json'
            with open(metadata_filename, 'w', encoding='UTF-8') as fp:
                json.dump(game_meta_data, fp, ensure_ascii=False)

            while True:
                try:
                    player_data = requests.get(LIVE_CLIENT_DATA_API_ROOT +
                                               'playerlist/', verify=False).json()
                    game_time = requests.get(
                        LIVE_CLIENT_DATA_API_ROOT + 'gamestats/',
                        verify=False).json().get('gameTime')

                    if not loaded:
                        loaded = True

                    try:
                        current_timestamp = {
                            'timestamp': game_time,
                            'player_data': [
                                {key: champ.get(key)
                                 for key in self.player_data_keys}
                                for champ in player_data
                            ]}
                        if 0 < game_time < 30:
                            send_serial('COM7')

                        for player in current_timestamp['player_data']:
                            player['items'] = [
                                {
                                    'itemID': item['itemID'],
                                    'count': item['count']
                                } for item in player['items']
                            ]

                            player['kills'] = player['scores']['kills']
                            player['deaths'] = player['scores']['deaths']
                            player['assists'] = player['scores']['assists']

                            del player['scores']

                        result.append(current_timestamp)
                        print('Current time: {}'.format(game_time))

                        if game_time == prev_game_time:
                            game_time_count += 1
                        else:
                            game_time_count = 0

                        if game_time_count == 3:
                            os.system(
                                "taskkill /f /im \"League of Legends.exe\"")
                            break

                        prev_game_time = game_time

                    except AttributeError:
                        print('Waiting for game to start')

                except requests.exceptions.ConnectionError:
                    if not loaded:
                        print('Waiting for League client')
                    else:
                        break
                sleep(self.interval)

            result_data_filename = 'result' + \
                replay_file.split('.')[0] + '.json'
            with open(result_data_filename, 'w', encoding='UTF-8') as file:
                json.dump(result, file, ensure_ascii=False)
            calc_gold(result_data_filename, 'resources/item.json')

            sleep(10)


def main():
    parser = ReplayParser()
    parser.parse()


if __name__ == '__main__':
    main()
