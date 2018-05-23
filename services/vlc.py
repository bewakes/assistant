import subprocess
import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils import log  # noqa
from utils.helpers import pipe_commands, get_commands  # noqa
from services._song_searcher import SongSearcher  # noqa


logger = log.get_logger('VLC Service')


class VLC(SocketHandlerMixin):
    """
    Service to play songs/urls from commandline
    """
    def __init__(self):
        super().__init__()
        self._player_pid = None
        self._vlc_audio_command = "cvlc -I telnet --telnet-password test --no-video {url} --preferred-resolution 144"  # noqa
        self.pause_command = 'echo -e test\npause\nquit\n'
        self.netcat_command = 'nc localhost 4212'
        self.playing = False
        self.searcher = SongSearcher()

    def _play_audio(self, path_or_location):
        """
        play audio with vlc
        """
        url = path_or_location.replace('https', 'http')
        audi_commd = self._vlc_audio_command.format(url=url)
        logger.info('VLC command: {}'.format(audi_commd))
        process = subprocess.Popen(audi_commd.split())
        self._player_pid = process.pid

        # add pid to child_pids
        self._child_pids[process.pid] = True
        # output, error = process.communicate()

    def handle_pause(self, args):
        pipe_commands(
            get_commands([self.pause_command, self.netcat_command])
        )
        self.playing = False
        return "Paused"

    def handle_resume(self, args):
        logger.info('handle resume')
        if not self.playing:
            # same command as pause
            pipe_commands(
                get_commands([self.pause_command, self.netcat_command])
            )
        return "Resumed"

    def handle_play(self, args):
        # TODO: for video, for now only audio
        if not args:
            # means play the paused
            output = self.handle_resume(args)
            return output
        song_query = ' '.join(args)
        logger.info("Searching song.." + song_query)
        songpath = self.searcher.handle_search(song_query)
        logger.info("Song path found " + songpath)
        if not songpath:
            return "No song found"
        # kill children
        self.handle_killall()
        self._play_audio(songpath)
        return "Playing {}".format(song_query)

    def handle_playlist(self, args):
        pass


if __name__ == '__main__':
    v = VLC()
    # get port from arg
    port = sys.argv[1]
    try:
        # run it
        v.initialize_and_run(port)
    except SystemExit:
        pass
    except Exception:
        print(traceback.format_exc())
