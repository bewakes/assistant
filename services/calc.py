import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils import log  # noqa
from utils.terminal_formatter import Style


logger = log.get_logger('Calculator service')


class Calculator(SocketHandlerMixin):
    def __init__(self):
        super().__init__()

    def handle_calc(self, args):
        expression = ''.join(args)
        try:
            return Style.green(str(eval(expression)))
        except Exception as e:
            return Style.red(''.join(e.args))


if __name__ == '__main__':
    c = Calculator()
    port = sys.argv[1]
    try:
        c.initialize_and_run(port)
    except SystemExit:
        pass
    except Exception:
        logger.error(traceback.format_exc())
