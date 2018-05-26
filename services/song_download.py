import sys
import os
import re
import traceback
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils.helpers import pipe_commands  # noqa
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
        self.download_command = "youtube-dl {url} --extract-audio --audio-format mp3 -o {dir}%(id)s.%(ext)s".format(  # noqa
            dir=SongDownloader.DOWNLOAD_PATH, url='{url}'
        )
        path = SongDownloader.DOWNLOAD_PATH
        self.rename_command = 'mv '+path+'{video_id}.mp3 '+path+'{songname}.mp3'  # noqa
        self.searcher = SongSearcher()
        self.downloader_pid = None

    @staticmethod
    def is_url(string):
        return re.match('[a-z]+://.+', string)

    def handle_download(self, args):
        if not args:
            return "No song provided"  # TODO: format color
        url = ' '.join(args)
        if not self.is_url(url):
            logger.info("Getting url for song {}".format(url))
            url = self.searcher.handle_search(url)
            logger.info("obtained url: {}".format(url))
            # TODO: check if file path returned and not download in that case
        video_id = re.match('.*=(.*)$', url).groups(1)[0]
        command = self.download_command.format(url=url)
        subprocess.Popen(command.split(), stdout=subprocess.DEVNULL)
        logger.info('downloading: {}'.format(command))
        return "Downloading.."


if __name__ == '__main__':
    d = SongDownloader()
    port = sys.argv[1]
    try:
        d.initialize_and_run(port)
    except SystemExit:
        pass
    except Exception:
        logger.error(traceback.format_exc())
