import base64
import subprocess
import os


class ReplayClient():
    """
    League of Legend replay Client class
    Opens a League of Legends client and returns a process object
    """

    def __init__(self, game_dir, replay_file_dir, replay_file_name):
        self.game_dir = game_dir
        self.replay_dir = replay_file_dir
        self.replay_file_name = replay_file_name

    def run_client(self):
        process = subprocess.Popen(
            [
                self.game_dir + '\\Game\\League of Legends.exe',
                os.path.join(self.replay_dir, self.replay_file_name),
                '-GameBaseDir=' + self.game_dir,
                '-Region=KR',  # TODO set region dynamically
                '-PlatformID=KR',
                '-Locale=ko_KR',
                '-SkipBuild',
                '-EnableCrashpad=true',
                '-EnableLNP',
                '-UseDX11=1:1',
                '-UseMetal=0:1',
                '-UseNewX3D',
                '-UseNewX3DFramebuffers',
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.game_dir + r'\Game'
        )

        return process

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
