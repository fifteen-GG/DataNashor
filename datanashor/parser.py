import base64
import os
import requests
import json
import serial
from requests.adapters import HTTPAdapter, Retry
from requests.packages import urllib3

from datanashor.utils.calc_gold import calc_gold
from datanashor.metadata import MetaDataParser
from datanashor.client import ReplayClient
from datanashor.utils.send_serial import send_serial

from time import sleep


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


LIVE_CLIENT_DATA_API_ROOT = 'https://127.0.0.1:2999/liveclientdata/'


class ReplayParser():
    """
    Replay Parser class for parsing League of Legends replay files (.rofl)

    replay_file_dir: Directory of League of Legends replay files. Defaults to C:/Users/username/Documents/League of Legends/Replays
    game_dir: Directory of League of Legends game files. Defaults to C:/Riot Games/League of Legends
    interval: Interval between each request to the Live Client Data API. Defaults to 0.8 seconds
    player_data_keys: Keys to parse from Live Client Data API. Defaults to ['summonerName', 'championName', 'isDead', 'level', 'scores', 'items', 'team']
    serial_port: Serial port for sending data to Arduino. Defaults to None
    delete: Delete replay files after parsing. Defaults to True
    current_game_version: Current game version. Defaults to None. ex) '12.20'
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
            ],
            serial_port=None,
            delete=True,
            train=False,
            train_api_root=None,
            current_game_version=None,
    ):

        self.replay_file_dir = replay_file_dir
        self.game_dir = game_dir
        self.interval = interval
        self.replay_files = os.listdir(replay_file_dir)
        self.metadata = MetaDataParser(replay_file_dir)
        self.player_data_keys = player_data_keys
        self.serial_port = serial_port
        self.delete = delete
        self.train = train
        self.train_api_root = train_api_root
        self.game_version = current_game_version

        if train and not train_api_root:
            raise ValueError(
                'train_api_root must be specified if train is true.')
        if not current_game_version:
            raise ValueError(
                'you must specify the current game version. ex) 12.20')

    def parse(self):
        """
        Parse all replay files in the replay_file_dir directory
        """
        while True:
            try:
                game_meta_data, game_version = self.metadata.parse(
                    self.replay_files[0])
            except IndexError:
                print('There are no more replay files left to parse.')
                break

            if game_version[:5] != self.game_version:
                print(
                    f'{self.replay_files[0]} file\'s game version is {game_version[:5]}. Skipping...')
                if self.delete:
                    os.remove(os.path.join(
                        self.replay_file_dir, self.replay_files[0]))
                    self.replay_files = os.listdir(self.replay_file_dir)
                else:
                    del self.replay_files[0]
                continue

            print(f'Parsing {self.replay_files[0]}')

            client = ReplayClient(
                game_dir=self.game_dir,
                replay_file_dir=self.replay_file_dir,
                replay_file_name=self.replay_files[0])

            client.run_client()

            result = []
            loaded = False
            game_time_count = 0
            prev_game_time = 0

            metadata_filename = 'meta_' + \
                self.replay_files[0].split('.')[0] + '.json'
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
                        try:
                            if 0 < game_time < 30:
                                send_serial(self.serial_port)
                        except serial.serialutil.SerialException:
                            pass

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

            result_data_filename = 'result_' + \
                self.replay_files[0].split('.')[0] + '.json'
            with open(result_data_filename, 'w', encoding='UTF-8') as file:
                json.dump(result, file, ensure_ascii=False)
            calc_gold(result_data_filename, 'item.json')

            if self.train:
                result_file = open(result_data_filename, 'rb')
                meta_file = open(metadata_filename, 'rb')

                s = requests.Session()

                retries = Retry(total=10,
                                backoff_factor=1,
                                status_forcelist=[400, 404, 500, 502, 503, 504])
                s.mount('http://', HTTPAdapter(max_retries=retries))

                s.post(self.train_api_root, files={
                    'result_file': result_file,
                    'meta_file': meta_file
                })
                result_file.close()
                meta_file.close()
                os.remove(result_data_filename)
                os.remove(metadata_filename)

            if self.delete:
                os.remove(os.path.join(
                    self.replay_file_dir, self.replay_files[0]))
                self.replay_files = os.listdir(self.replay_file_dir)
            else:
                del self.replay_files[0]
            sleep(10)

            if not self.replay_files:
                print('There are no more replay files left to parse.')
                break

    def get_client_metadata(self):
        '''
        Returns the client metadata.
        League of Legends client must be running.
        NOTE: by client, it does not means the replay client, but the actual game client.
        '''
        try:
            raw_metadata = open(self.game_dir + '\\lockfile',
                                'r').read().split(':')
            metadata = {
                "port": raw_metadata[2],
                "token": str(base64.b64encode(f'riot:{raw_metadata[3]}'.encode('utf-8')), encoding='utf-8'),
            }

            return metadata
        except FileNotFoundError:
            raise FileNotFoundError(
                'lockfile not found. Is the client running?')


def main():
    parser = ReplayParser()
    parser.parse()


if __name__ == '__main__':
    main()
