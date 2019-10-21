import re
import sys
import os
import json
from datetime import datetime
from dateutil import tz

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils import log  # noqa
from utils.terminal_formatter import Style  # noqa
from utils import http  # noqa
from utils.helpers import (  # noqa
    parse_iso_date,
    return_on_exception,
    parse_duration,
)


logger = log.get_logger('Expense service')


ADD_REGEX = re.compile(r'^\W*(?P<category>.*?)\W+(?P<amount>\d+\.{0,1}\d*)'
                       r'(\W+items\W+(?P<items>.*?)){0,1}'
                       r'(\W+::\W*(?P<date>.*?)){0,1}'
                       r'(\W+:\W*(?P<description>.*)){0,1}$')

SHOW_REGEX = re.compile(r'.*for\W+(?P<duration>.*)$')

BASE_URL = 'https://expenses.bewakes.com/'
# BASE_URL = 'http://localhost:8000/'
IDENTITY_URL = f'{BASE_URL}identity/'
CATEGORY_URL = f'{BASE_URL}categories/'
EXPENSES_URL = f'{BASE_URL}expense/'

SHOW_USAGE_TEXT = 'Usage: expense show [categories|(expenses [for YYYY-MM-DD])]'


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
        if self.token is None:
            return Style.red('Token not set. Please set token by issuing: "expense add_token <token>"')

        match = ADD_REGEX.match(' '.join(args))
        if match is None:
            return Style.yellow('Usage: expense add <category> <amount> items <comma separated items> [:: <date>] [: <description>]')

        date = self.validate_date(match.group('date'))
        category = self.validate_category(match.group('category'))
        items = match.group('items')
        description = match.group('description')

        data = {
            "cost": float(match.group('amount')),
            "date": date or datetime.utcnow().strftime('%Y-%m-%d'),
            "category": category,
        }
        if items:
            data['items'] = items
        if description:
            data['description'] = description

        print('calling http post')
        response = http.post(EXPENSES_URL, data, self.get_token_header())
        if response.status_code == 201:
            return Style.green(f'Expense of Rs.{data["cost"]} added for {data["date"]}.')
        elif response.status_code == 403:
            raise Exception('Maybe CSRF Failed')
        elif response.status_code == 400:
            data = response.json()
            raise Exception(f'Invalid {data.keys()[0]}.')
        else:
            raise Exception(f'Unexpected Error: {response.text[:100]}')

    @return_on_exception
    def handle_show(self, args):
        if not args:
            return self.show_expenses(args)

        if args[0].lower() == 'categories':
            categories = self.get_categories()
            cat_str = '\n'.join([Style.green(x) for x in categories.keys()])
            return f'Categories:\n{cat_str}'
        elif args[0].lower() == 'expenses':
            return self.show_expenses(args)
        elif args[0].lower() == 'summary':
            return self.show_expenses(args)
        else:
            raise Exception('Usage: expense show categoies|expenses')

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

    def validate_category(self, category):
        identity = self.identity
        if identity is None:
            return Style.red('Invalid token set.')

        categories = self.get_categories()

        category_lower = category.lower()
        if category_lower not in categories:
            raise Exception(f'Category "{category}" not found.')

        # Return id
        return categories[category_lower]

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

    def get_categories(self):
        if hasattr(self, '_categories'):
            return self._categories
        default_organization = self.identity['default_organization']
        response = http.get(
            CATEGORY_URL,
            {'organization': default_organization['id']},
            self.get_token_header()
        )
        if response.status_code == 200:
            self._categories = {
                x['name'].lower(): x['id']
                for x in response.json()
            }
            return self._categories
        raise Exception('ERROR: ' + response.text[:100])

    def get_expenses(self, data):
        data['organization'] = self.identity['default_organization']['id']
        response = http.get(EXPENSES_URL, data, self.get_token_header())

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Error: ' + response.text[:100])

    def show_expenses(self, args):
        data = {}

        if args and args[0] == 'summary':
            data['individual'] = 'true'
            match = SHOW_REGEX.match(' '.join(args[1:]))
            duration_str = match and match.group('duration')
            if not duration_str:
                duration, n = 'week', 1
            else:
                duration, n = parse_duration(duration_str)
            data['duration'] = duration
            data['n'] = n

            expenses = self.get_expenses(data)
            return self.get_summary_string(expenses)

        """
        params = args[1:]
        if params and params[0] == 'for':
            if not params[1:]:
                raise Exception(SHOW_USAGE_TEXT)
            data['forDate'] = params[1]
        """

        expenses = self.get_expenses(data)

        header = Style.yellow(f"\n{'Date'.ljust(15)}Total\n")
        header += Style.yellow('='*len(header)) + '\n'

        expense_data = ''
        for expense in expenses:
            expense_data += Style.green(f"{expense['date'].ljust(15)}{expense['total']}") + '\n'
        return f'{header}{expense_data}'

    def get_summary_string(self, expenses):
        categories_reverse_map = {v: k for k, v in self.get_categories().items()}
        header = Style.yellow(f"\n{'Date'.ljust(15)}{'Category'.ljust(20)}{'Price'.ljust(10)}{'Items'.ljust(25)}{'Description'.ljust(25)}\n")
        header += Style.yellow('='*len(header)) + '\n'

        print_colors = [Style.green, Style.magenta]
        color_index = 0
        curr_date = None

        summary_string = ''
        for expense in expenses:
            date = expense['date']

            if curr_date is not None and date != curr_date:
                color_index = (color_index + 1) % 2
            curr_date = date

            category = categories_reverse_map[expense['category']]
            price = expense['cost']
            items = expense['items'] or '---'
            description = expense['description'] or '---'

            summary_string += print_colors[color_index](
                f'{date.ljust(15)}{category.ljust(20)}'
                f'{str(price).ljust(10)}{items.ljust(25) if len(items) < 25 else (items[:21] + "...").ljust(25)}'
                f'{description.ljust(25)}\n'
            )
        return f'{header}{summary_string}'


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
