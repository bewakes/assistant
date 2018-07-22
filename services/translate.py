import sys
import os
import googletrans

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils import log # noqa

logger = log.get_logger('Translate service')


class Translate(SocketHandlerMixin):
    def __init__(self):
        super().__init__()
        self.translator = googletrans.Translator()

    def handle_translate(self, args):
        self.query = ' '.join(args)
        return self.translator.translate(self.query).text


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
