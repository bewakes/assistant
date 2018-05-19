import subprocess
import sys
from _socket_mixin import SocketHandlerMixin
import traceback

import _log

logger = _log.get_logger('VLC Service')


class VLC(SocketHandlerMixin):
    """
    Service to play songs/urls from commandline
    """
    def __init__(self):
        super().__init__()
        self._player_pid = None
        self._vlc_audio_command = "cvlc -I telnet --telnet-password test --no-video {url} --preferred-resolution 144"  # noqa

    def _play_audio(self, arg):
        """
        play audio with vlc
        """
        audi_commd = self._vlc_audio_command.format(url=arg)
        logger.info('VLC command: {}'.format(audi_commd))
        process = subprocess.Popen(audi_commd.split())
        self._player_pid = process.pid

        # add pid to child_pids
        self._child_pids[process.pid] = True
        # output, error = process.communicate()

    def handle_command(self, command):
        """
        This has been overridden from mixin
        """
        try:
            cmd_args = command.decode('ascii').split()
            cmd = cmd_args[0]
            args = ' '.join(cmd_args[1:])

            if cmd == 'audio':
                if self._player_pid:
                    self.kill_child(self._player_pid)
                    del self._child_pids[self._player_pid]
                    self._player_pid = None

                self._play_audio(args)
            elif cmd == 'killall':
                self.killall()
        except Exception as e:
            print(traceback.format_exc())

        return "Playing"


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
