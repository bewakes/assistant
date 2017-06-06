import subprocess
import sys
from handler import SocketMixin
import traceback

class VLC(SocketMixin):
    """
    Service to play songs/urls from commandline
    """
    def __init__(self):
        super().__init__()
        self._player_pid = None
        self._vlc_audio_command = "cvlc -I telnet --telnet-password test --vout none {url} --preferred-resolution 144"

    def _play_audio(self, arg):
        """
        play audio with vlc
        """
        audi_commd = self._vlc_audio_command.format(url=arg)
        process = subprocess.Popen(audi_commd.split())
        self._player_pid = process.pid

        # add pid to child_pids
        self._child_pids[process.pid] = True
        #output, error = process.communicate()


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
    except:
        print(traceback.format_exc())
