import subprocess
import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils import log  # noqa
from utils.helpers import pipe_commands, get_commands, is_url  # noqa
from services._song_searcher import SongSearcher  # noqa
from services.song_download import SongDownloader  # noqa


logger = log.get_logger('VLC Service')


class VLC(SocketHandlerMixin):
    """
    Service to play songs/urls from commandline
    """
    def __init__(self):
        super().__init__()
        self._player_pid = None
        self._vlc_audio_command = "cvlc -I telnet --telnet-password test --no-video".split()  # noqa  # add url
        # self._vlc_audio_command = "cvlc -I oldrc --rc-unix /tmp/vlc.sock --no-video {url} --preferred-resolution 144"  # noqa
        self.pause_command = 'echo -e test\npause\nquit\n'
        # self.pause_command = 'echo pause'
        # self.netcat_command = 'nc -U /tmp/vlc.sock -q 0'
        self.is_playing = 'echo -e test\r\nis_playing\r\nquit\r\n'
        self.netcat_command = 'nc localhost 4212'
        self.current_playlist = []
        self.current_index = None
        self.playing = False
        self.searcher = SongSearcher()
        self.downloader = SongDownloader()

    def _play_audio(self, path_or_location):
        """
        play audio with vlc
        """
        url = path_or_location.replace('https', 'http')
        audi_commd = self._vlc_audio_command + [url]
        logger.info('VLC command: {}'.format(audi_commd))
        process = subprocess.Popen(audi_commd)
        self._player_pid = process.pid
        logger.info("vlc pid " + str(process.pid))

        # add pid to child_pids
        self._child_pids[process.pid] = True

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
        if args[0] == 'next':
            return self.handle_next(args)
        if args[0] == 'previous':
            return self.handle_previous(args)
        song_query = ' '.join(args)
        logger.info("Searching song.." + song_query)
        song, songpath = self.searcher.handle_search(song_query)
        logger.info("Song path found " + songpath)
        if not songpath:
            return "No song found"
        self.current_playlist = [(song, songpath)]
        self.current_index = 0
        # kill children
        self.handle_killall()
        # check if songpath is a file path, if not download it
        if is_url(songpath):
            logger.info("song not found locally, downloading")
            r = self.downloader.download_url(songpath, song)
            logger.info(r)
        self._play_audio(songpath)
        return "Playing {}".format(song)

    def handle_playlist(self, args):
        # first handle random playlist
        playlist_query = ' '.join(args)
        logger.info("PLAYLIST QUERY: " + playlist_query)
        songspaths = self.searcher.handle_search_playlist(playlist_query)
        logger.info(songspaths)
        self.current_playlist = songspaths
        self.current_index = 0
        self.handle_killall()
        self._play_audio(songspaths[0][1])
        return "Playing {}".format(songspaths[0][0])

    def handle_repeat(self, args):
        self.handle_killall()
        song = self.current_playlist[self.current_index]
        self._play_audio(song[1])
        return 'Playing {}'.format(song[0])

    def handle_next(self, args):
        msg = None
        if self.current_index is None or not self.current_playlist:
            msg = "Nothing is being played"
        elif self.current_index >= len(self.current_playlist) - 1:
            msg = "End of playlist"
        elif self.current_index < len(self.current_playlist) - 1:
            self.current_index += 1
            msg = "Playing " + self.current_playlist[self.current_index][0]
            self.handle_killall()
            self._play_audio(self.current_playlist[self.current_index][1])
        else:
            msg = "Something is not right"
            # TODO: format
        return msg

    def handle_previous(self, args):
        msg = None
        if self.current_index is None or not self.current_playlist:
            msg = "Nothing is being played"
        elif self.current_index == 0:
            msg = "Beginning of playlist"
        elif self.current_index > 0:
            self.current_index -= 1
            msg = "Playing " + self.current_playlist[self.current_index][0]
            self.handle_killall()
            self._play_audio(self.current_playlist[self.current_index][1])
        else:
            msg = "Something is not right"
            # TODO: format
        return msg


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
