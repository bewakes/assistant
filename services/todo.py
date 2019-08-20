import os
import sys
import datetime
import json
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils.terminal_formatter import Style  # noqa
from utils import log  # noqa

logger = log.get_logger('Notes')


class TodoService(SocketHandlerMixin):
    """
    Service to store todos
    """
    TODOS_ROOT = os.path.expanduser('~/.assistant/todos/')
    DATES_DIR = os.path.join(TODOS_ROOT, 'dates/')
