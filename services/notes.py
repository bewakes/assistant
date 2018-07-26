import os
import datetime
import sys
import json
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils.terminal_formatter import Style  # noqa
from utils import log  # noqa

logger = log.get_logger('Notes')


DELIMITER = '_|{}|_ ->'


class NotesService(SocketHandlerMixin):
    """
    Service to take notes
    * First notes are stored alphabetwise
    *Notes are stored/indexed tagwise and datewise
    """
    NOTES_ROOT = os.path.expanduser('~/.assistant/notes/')
    TAGS_DIR = os.path.join(NOTES_ROOT, 'tags/')
    DATES_DIR = os.path.join(NOTES_ROOT, 'dates/')
    COUNTS_FILENAME = 'counts.json'

    def __init__(self):
        super().__init__()
        # try create dirs
        os.system('mkdir -p '+self.NOTES_ROOT)
        os.system('mkdir -p '+self.TAGS_DIR)
        os.system('mkdir -p '+self.DATES_DIR)
        # get count_data
        self.count_filepath = os.path.join(
            self.NOTES_ROOT, self.COUNTS_FILENAME
        )
        self.count_data = {}
        # if not count file exist, create empty one
        if not os.path.exists(self.count_filepath):
            with open(self.count_filepath, 'w') as f:
                f.write(json.dumps(self.count_data))
        else:
            # if exists, load data
            with open(self.count_filepath) as f:
                try:
                    self.count_data = json.load(f)
                except Exception as e:
                    logger.warn("can't read count json properly. re creating")
                    with open(self.count_filepath, 'w') as f:
                        f.write(json.dumps(self.count_data))

    def update_count_data(self):
        with open(self.count_filepath, 'w') as f:
            f.write(json.dumps(self.count_data, indent=4))

    def handle_add(self, args):
        """
        @args: list of args
        Save note to tags if present, else to miscellaneous tag
        """
        args = ' '.join(args)
        splitted = args.split(':')
        if len(splitted) < 2:
            tags = ['miscellaneous']
            note = args
        else:
            tags = splitted[0].strip().split()
            note = ''.join(splitted[1:])
        note = note.strip()
        if not note:
            return Style.red('empty note')
        first_char = note[0].lower()
        # try to create directory
        filepath = '{}{}'.format(self.NOTES_ROOT, first_char)

        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        delimiter = DELIMITER.format(now)

        # now write to files
        with open(filepath, 'a') as file:
            file.write(delimiter + note)
            file.write('\n')
        # increment counter and write to count file
        self.count_data[first_char] = self.count_data.get(first_char, 0) + 1
        self.update_count_data()

        indexed_content = '{}{} {}'.format(
            first_char,
            self.count_data[first_char],
            now
        )
        # also add to tags
        for tag in tags:
            tagpath = os.path.join(self.TAGS_DIR, tag)
            with open(tagpath, 'a') as f:
                f.write(indexed_content + '\n')

        # add to date folder
        datepath = os.path.join(self.DATES_DIR, now[:10])
        with open(datepath, 'a') as f:
            f.write(indexed_content + '\n')

        return Style.green('Note added to the following tags: '+' '.join(tags))


if __name__ == '__main__':
    n = NotesService()

    # get port from arg
    port = sys.argv[1]

    # run it
    try:
        n.initialize_and_run(port)
    except Exception as e:
        print(traceback.format_exc())
