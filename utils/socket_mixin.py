import sys
import signal
import socket
import subprocess
import traceback

from . import log
from .helpers import try_encode

logger = log.get_logger('MIXIN')


class SocketHandlerMixin(object):
    """
    Mixin to provide command handling interface to services
    """
    def __init__(self):
        self.services_ports_file = '/tmp/services-ports'  # TODO: make static
        self._child_pids = {}

        def handle_sigterm(num, frame):
            self.killall()
            sys.exit()

        signal.signal(signal.SIGTERM, handle_sigterm)

    def get_services_ports(self):
        services_ports = {}
        with open(self.services_ports_file) as f:
            services_ports = dict([line.split() for line in f.readlines()])
        return services_ports

    def execute_command(self, command, bg=True, ignore_result=True):
        """
        Execute command and return pid
        """
        if type(command) == str:
            command = command.split()
        # other wise, it is list(assumption)
        if ignore_result:
            process = subprocess.Popen(
                command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
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
            child_pids = ' '.join([str(x) for x in self._child_pids.keys()])
            self.execute_command("kill -9 " + child_pids)
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

    def communicate(self, service, command):
        """
        @service: name of service
        @command: string of command
        """
        services_ports = self.get_services_ports()
        logger.info("services and ports: {}".format(str(services_ports)))
        port = services_ports.get(service)
        if not port:
            logger.warn("service {} doesnot exist for communication".format(
                service
            ))
            return ''
        sock = socket.socket()
        sock.connect(('localhost', port))
        output = ''
        while True:
            sock.send(command+"\r\n")
            r = sock.recv()
            r = r.decode('ascii')
            output += r+"\n"
            if r == '$$':
                break
        return output

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
            args = [x.decode() for x in args]

            try:
                result = self.handler(command, args)
            except Exception:
                logger.info(traceback.format_exc())
                # kill all the child processes
                self.handle_killall()
                result = 'Error occured. Please check log at /tmp/assistant.log.'  # noqa

            out = '{}\n'.format(result)
            conn.send(try_encode(out))
            conn.close()
