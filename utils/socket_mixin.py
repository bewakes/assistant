import sys
import signal
import socket
import subprocess

from . import log
from .helpers import try_encode

logger = log.get_logger('MIXIN')


class SocketHandlerMixin(object):
    """
    Mixin to provide command handling interface to services
    """
    def __init__(self):
        self._child_pids = {}

        def handle_sigterm(num, frame):
            self.killall()
            sys.exit()

        signal.signal(signal.SIGTERM, handle_sigterm)

    def execute_command(self, command, bg=True):
        """
        Execute command and return pid
        """
        if type(command) == str:
            command = command.split()
        # other wise, it is list(assumption)
        process = subprocess.Popen(command)

        if not bg:
            output, error = process.communicate()

        return process.pid

    def kill_child(self, pid):
        """
        Kill child with given pid
        """
        try:
            self.execute_command("kill -9 "+str(pid))
        except Exception as e:
            print(e)

    def killall(self):
        """
        Kill all child
        """
        try:
            # TODO: check status of _child_pids keys also
            self.execute_command("kill -9 "+' '.join([str(x) for x in self._child_pids.keys()]))
        except Exception as e:
            print(e)

    def handle_killall(self):
        self.killall()

    def handler(self, command, args=[]):
        """
        To be overridden by inheriting class
        - command consists of the socket data sent by assistant(parent) process
        - might need to split up to args
        """
        ###
        # command parsing and handling logic to be implemented by child
        ###
        methodname = 'handle_{}'.format(command)
        logger.info('method name: {}'.format(methodname))
        logger.info('args: {}'.format(args))
        method = self.__getattribute__(methodname)
        return method(args)

    def initialize_and_run(self, port, host=''):
        """
        Initialize the socket and make it listen/respond to commands
        """
        port = int(port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        while True:
            self.sock.listen(5)  # TODO: make this configurable
            conn, addr = self.sock.accept()
            raw_command = conn.recv(1024)
            splitted = raw_command.split()
            command, args = splitted[0], splitted[1:]
            command = command.decode()
            args = list(map(lambda x: x.decode(), args))

            result = self.handler(command, args)

            out = '{}\n'.format(result)
            conn.send(try_encode(out))
            conn.close()
