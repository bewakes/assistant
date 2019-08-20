import sys
import os
import json
import requests
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils import log # noqa
from utils.terminal_formatter import Style


logger = log.get_logger('Meaning service')


class Meaning(SocketHandlerMixin):
    """
    Find meanings of query. Uses Oxford api
    """
    def __init__(self):
        super().__init__()
        self.url = 'https://od-api.oxforddictionaries.com:443/api/v2/entries/{}/{}'  # noqa
        self.app_id = os.environ.get('OXFORD_APP_ID', '')
        self.app_key = os.environ.get('OXFORD_APP_KEY', '')
        self.query = None
        self.FILENAME = 'meanings.json'
        self.meanings = self.read_meanings()

    def _get_path(self):
        dirname = os.path.expanduser('~/.assistant')
        path = os.path.join(dirname, self.FILENAME)
        return path

    def read_meanings(self):
        path = self._get_path()
        try:
            with open(path) as f:
                return json.loads(f.read())
        except FileNotFoundError:
            return {}

    def update_meanings(self, data):
        meanings = self.read_meanings()
        meanings[self.query.lower()] = data
        path = self._get_path()
        with open(path, 'w') as f:
            f.write(json.dumps(meanings, indent=2))
        self.meanings = meanings

    def handle_meaning(self, args):
        self.query = ' '.join(args)
        if self.meanings.get(self.query.lower()):
            logger.info("returning from local file")
            return self.display_meaning_data(self.meanings[self.query.lower()])

        language = 'en-us'
        url = self.url.format(
            language, self.query.lower()
        )
        data = {}
        r = requests.get(
            url,
            headers={'app_id': self.app_id, 'app_key': self.app_key}
        )
        logger.info("Meaning: {}".format(r))
        if r.status_code < 200 or r.status_code > 299:
            return self.display_meaning_data({})
        raw_data = r.json()
        logger.info(raw_data)
        for result in raw_data['results']:
            for lex_entry in result['lexicalEntries']:
                category = lex_entry['lexicalCategory']['id']
                for entry in lex_entry['entries']:
                    meanings = []
                    examples = []
                    sense = entry['senses'][0]
                    for sense in entry['senses']:
                        try:
                            meanings.append(sense['definitions'][0])
                        except KeyError:
                            continue
                        examples = [
                            x['text'] for x in sense.get('examples', [])
                        ]
                    info = {
                        'meanings': meanings,
                        'examples': examples
                    }
                    data[category] = data.get(category, []) + [info]
        # update meanings
        self.update_meanings(data)
        return self.display_meaning_data(data)

    def display_meaning_data(self, data):
        s = '{}\n'.format(Style.bold(self.query.upper()))
        if not data:
            return s + Style.red("Sorry, I don't know it now.")
        for k, v in data.items():
            s += Style.green(k) + "\n"
            for m in v[0]['meanings']:
                s += "- " + m + "\n"
            for e in v[0]['examples']:
                s += Style.yellow('  "{}"'.format(e))+"\n"
        return s


if __name__ == '__main__':
    m = Meaning()
    port = sys.argv[1]
    try:
        m.initialize_and_run(port)
    except SystemExit:
        pass
    except Exception:
        logger.error(traceback.format_exc())
