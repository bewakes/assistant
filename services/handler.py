import socket

class SocketMixin(object):
    """
    Mixin to provide command handling interface to services
    """
    def __init__(self):
        pass

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
            result = self.handle_command(command)
            conn.send('{}\n'.format(result).encode('ascii'))
