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
