import os
import sys
import json
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils.terminal_formatter import Style  # noqa
from utils.helpers import parse_integer  # noqa
from utils import log # noqa

logger = log.get_logger('Pomodoro')


class PomodoroService(SocketHandlerMixin):
    """
    Service to setup pomodoro
    """
    def __init__(self):
        super().__init__()
        # Record the spawned process responsible for time tracking and setting off alarm
        self.current_config = None # the config that will be loaded from config file
        self.new_config = None  # the new requested config by user

        # setup config
        dirname = os.path.expanduser('~/.assistant')
        self.config_path = os.path.join(dirname, 'pomodoro.json')

        self.read_config()

    def create_config(self, w=None, b=None, c=None, lb=None):
        return {
            'work_duration': w or 25,
            'break_duration': b or 10,
            'cycles_before_long_break': c or 3,
            'long_break_duration': lb or 30,
        }

    def write_config(self, config):
        with open(self.config_path, 'w') as cf:
            json.dump(self.current_config, cf)

    def read_config(self):
        try:
            with open(self.config_path) as cf:
                self.current_config = json.load(cf)
        except FileNotFoundError:
            # Just create a file
            self.current_config = self.create_config(25, 10, 3, 30)

            self.write_config(self.current_config)

    def display_config(self, config=None):
        return json.dumps(config or self.current_config, indent=4)

    def handle_set(self, args):
        if len(args) != 4:
            return Style.yellow(
                'Usage: pomodoro set <Work> <Break> <Long break after n cycles> <Long Break>\n'
                'NOTE: All times in minutes'
            )
        confirmation = Style.light_red(
            f'The current setup is: {self.display_config()}\n'
            'Enter: `pomodoro confirm` to apply your requested config'
        )
        [work, brk, cycles, long_break] = [parse_integer(x) for x in args]
        self.new_config = self.create_config(work, brk, cycles, long_break)
        return confirmation

    def handle_confirm(self, args):
        config = self.new_config
        if config is None:
            msg = Style.light_red('You did not specify configuration. Nothing updated.')
            config = self.create_config()
        else:
            msg = Style.green(f'The following config has been stored:\n {self.display_config(config)}')
        self.write_config(config)
        # unset new config
        self.current_config = config
        self.new_config = None
        return msg

    def handle_show(self, args):
        return Style.green('Current Config:\n' + self.display_config())

    def handle_start(self, args):
        raise Exception

    def handle_stop(self, args):
        raise Exception


if __name__ == '__main__':
    p = PomodoroService()

    # get port from arg
    port = sys.argv[1]

    # run it
    try:
        p.initialize_and_run(port)
    except Exception:
        print(traceback.format_exc())
