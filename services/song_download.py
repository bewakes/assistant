import sys
import os
import re
import traceback
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils.helpers import pipe_commands, pipe_commands_bg  # noqa
from services._song_searcher import SongSearcher  # noqa
from utils import log  # noqa

logger = log.get_logger('Song DL service')


class SongDownloader(SocketHandlerMixin):
    """
    Service to download songs
    """
    DOWNLOAD_PATH = os.path.expanduser('~/Music/assistant/')

    def __init__(self):
        super().__init__()
        self.download_command = "youtube-dl {url} --extract-audio --audio-format mp3 -o '{dir}%(id)s.%(ext)s'".format(  # noqa
            dir=SongDownloader.DOWNLOAD_PATH, url='{url}'
        )
        #self.rename_command = 'mv '+path+'{video_id}.mp3 '+path+'{songname}.mp3'  # noqa
        self.searcher = SongSearcher()
        self.downloader_pid = None

    def _get_rename_command(self, video_id, song_name):
        rename_command = 'mv {}{}.mp3 "{}{}.mp3"'.format(
            SongDownloader.DOWNLOAD_PATH,
            video_id,
            SongDownloader.DOWNLOAD_PATH,
            song_name
        )
        return rename_command

    def download_url(self, url, song):
        video_id = re.match('.*=(.*)$', url).groups(1)[0]
        dl_command = self.download_command.format(url=url)
        rename_command = self._get_rename_command(video_id, song)
        cmd = '{} > /dev/null && {}'.format(dl_command, rename_command)
        subprocess.Popen(cmd, shell=True)
        return "Song Download is in progress."

    @staticmethod
    def is_url(string):
        return re.match('[a-z]+://.+', string)

    def handle_download(self, args):
        """Args contains song"""
        if not args:
            return "No song provided"  # TODO: format color
        song = ' '.join(args)
        song, url = self.searcher.handle_search(song)
        return self.download_url(url, song)


if __name__ == '__main__':
    d = SongDownloader()
    port = sys.argv[1]
    try:
        d.initialize_and_run(port)
    except SystemExit:
        pass
    except Exception:
        logger.error(traceback.format_exc())
