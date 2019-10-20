import re
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils import log  # noqa
from utils.terminal_formatter import Style  # noqa


logger = log.get_logger('Expense service')


class Expense(SocketHandlerMixin):
    """
    Add/View expenses
    """
    ADD_REGEX = re.compile(r'^\W*(?P<category>.*?)\W+(?P<amount>\d+\.{0,1}\d*)'
                           r'\W+(?P<items>.*?)'
                           r'(\W+::(?P<date>.*?)){0,1}'
                           r'(\W+:(?P<description>.*)){0,1}$')

    def __init__(self):
        dirname = os.path.expanduser('~/.assistant')
        self.config_path = os.path.join(dirname, 'expense.json')

        self.config = self._read_config()
        self.token = self.config and self.config.get('token')

    def _read_config(self):
        try:
            with open(self.config_path) as f:
                config = json.load(f)
                return config
        except FileNotFoundError:
            logger.error('Expense config not found')
            return None
        except json.decoder.JSONDecodeError:
            logger.error('Invalid json')
            return None

    def handle_add_token(self, args):
        if not args:
            return Style.red('No token provided')
        token = args[0]
        self.token = token
        data = {'token': token}
        with open(self.config_path, 'w') as f:
            f.write(json.dumps(data, indent=4))
        return Style.green('Token added')

    def handle_add(self, args):
        print(' '.join(args))
        if self.token is None:
            return Style.red('Token not set. Please set token by issuing: "expense add_token <token>"')
        """
        {
            "date":"2019-10-20",
            "description":"",
            "category":"8",
            "cost":45,
            "items":"test",
        }
        """
        match = self.ADD_REGEX.match(' '.join(args))
        if match is None:
            return Style.yellow('Usage: expense add <category> <amount> <comma separated items> [:: <date>] [: <description>]')
        data = {
            "cost": float(match.group('amount')),
            "category": match.group('category'),
            "items": match.group('items'),
            "date": match.group('date'),
            "description": match.group('description'),
        }
        # TODO: validate data: date and category
        print(data)
        return 'something'

if __name__ == '__main__':
    e = Expense()
    port = sys.argv[1]
    try:
        e.initialize_and_run(port)
    except SystemExit:
        pass
    except Exception:
        import traceback
        logger.error(traceback.format_exc())
