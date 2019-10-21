import re
import sys
import os
import json
from dateutil import tz

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils import log  # noqa
from utils.terminal_formatter import Style  # noqa
from utils import http  # noqa
from utils.helpers import (  # noqa
    parse_iso_date,
    return_on_exception,
)


logger = log.get_logger('Expense service')


ADD_REGEX = re.compile(r'^\W*(?P<category>.*?)\W+(?P<amount>\d+\.{0,1}\d*)'
                       r'(\W+items\W+(?P<items>.*?)){0,1}'
                       r'(\W+::\W*(?P<date>.*?)){0,1}'
                       r'(\W+:\W*(?P<description>.*)){0,1}$')

BASE_URL = 'https://expenses.bewakes.com/'
IDENTITY_URL = f'{BASE_URL}identity/'
CATEGORY_URL = f'{BASE_URL}categories/'
EXPENSES_URL = f'{BASE_URL}expense/'


class Expense(SocketHandlerMixin):
    """
    Add/View expenses
    """
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

    @return_on_exception
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
        match = ADD_REGEX.match(' '.join(args))
        if match is None:
            return Style.yellow('Usage: expense add <category> <amount> <comma separated items> [:: <date>] [: <description>]')
        print(match)

        date = self.validate_date(match.group('date'))
        category = match.group('category')
        items = match.group('items')
        description = match.group('description')

        data = {
            "cost": float(match.group('amount')),
            "date": date,
            "category": category,
        }
        if items:
            data['items'] = items
        if description:
            data['description'] = description

        print(data)
        return Style.green('So far so good')

    def validate_date(self, date):
        if date is None:
            return None

        # Validate Category
        parsed_date = parse_iso_date(date)
        if parsed_date is None:
            raise Exception(f'Invalid date \'{date}\'. Should be in YYYY-MM-DD format.')

        # Convert date to utc, first get local date
        localdate = parsed_date.astimezone(tz.gettz())
        return localdate.astimezone(tz.tzutc()).strftime('%Y-%m-%d')

    def validate_category(self, data):
        print(' in validate category')
        identity = self.identity
        if identity is None:
            return Style.red('Invalid token set.')

        default_organization = identity['default_organization']
        pass

    def get_token_header(self):
        return {'Authorization': f'Token {self.token}'}

    @property
    def identity(self):
        if hasattr(self, '_identity'):
            return self._identity

        response = http.get(IDENTITY_URL, {}, self.get_token_header())
        if response.status_code == 200:
            self._identity = response.json()
            return self._identity
        else:
            return None


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
