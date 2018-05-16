import sys
import signal
import socket
import subprocess


class SocketMixin(object):
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

    def handle_command(self, command):
        """
        To be overridden by inheriting class
        - command consists of the socket data sent by assistant(parent) process
        - might need to split up to args
        """
        ###
        # command parsing and handling logic to be implemented by child
        ###
        return ""

    def initialize_and_run(self, port, host=''):
        """
        Initialize the socket and make it listen/respond to commands
        """
        port = int(port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(5) # TODO: make this configurable

        while True:
            conn, addr = self.sock.accept()
            command = conn.recv(1024)

            if command.split()[0] == 'killall':
                self.killall()
                result = "Murdered all of 'em"
            else:
                result = self.handle_command(command)

            conn.send('{}\n'.format(result).encode('ascii'))
