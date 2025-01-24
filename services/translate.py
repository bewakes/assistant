import sys
import os
import googletrans

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.socket_mixin import AssistantService  # noqa
from utils import log # noqa
from utils.terminal_formatter import Style  # noqa

logger = log.get_logger('Translate service')

LANGUAGE_CODE_MAP = {
    'german': 'de',
    'spanish': 'es',
    'french': 'fr',
    'nepali': 'np',
}

LANGUAGE_CODE_REVERSE = {v: k for k, v in LANGUAGE_CODE_MAP.items()}


class Translate(AssistantService):
    def __init__(self):
        super().__init__()
        self.translator = googletrans.Translator()

    def handle_translate(self, args):
        self.query = ' '.join(args)
        translated = self.translator.translate(self.query)
        source = LANGUAGE_CODE_REVERSE.get(translated.src, translated.src).title()
        return Style.green(source + ': ') + Style.yellow(translated.text)

    def handle_translateto(self, args):
        if len(args) < 2:
            return 'Usage: translateto <language> <text>'
        lang = LANGUAGE_CODE_MAP.get(args[0], 'en')
        self.query = ' '.join(args[1:])
        return self.translator.translate(self.query, dest=lang).text


if __name__ == '__main__':
    m = Translate()
    port = sys.argv[1]
    try:
        m.initialize_and_run(port)
    except SystemExit:
        pass
    except Exception:
        import traceback
        logger.error(traceback.format_exc())
