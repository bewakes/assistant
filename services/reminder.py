import os
import hashlib
import subprocess
import datetime
import sys
import json
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils.terminal_formatter import Style  # noqa
from utils import log  # noqa

logger = log.get_logger('Reminder')


class ReminderService(SocketHandlerMixin):
    """
    Service to get reminder and send notifications to user periodically
    sample command: reminder set every n hours|minutes|days "Do this"
    """
    VALID_TIMES = [
        'hours', 'hour', 'mins', 'min',
        'minutes', 'minute', 'days', 'day'
    ]

    def __init__(self):
        super().__init__()
        self.invalid_msg = Style.red("Invalid command. SAMPLE:") +\
            Style.yellow("reminder set every 5 hours my task")

        self.user = subprocess.check_output(['whoami']).decode('ascii').strip()

    def get_curr_jobs(self):
        out = subprocess.check_output(['cat', '/var/spool/cron/'+self.user])
        jobs = [x for x in out.decode('ascii').split('\n') if x.strip() != '']
        return jobs

    def get_current_reminders(self):
        jobs = self.get_curr_jobs()
        return [x for x in jobs if ' # ASSISTANT' in x]

    def handle_show(self, args):
        curr = self.get_current_reminders()
        texts = ['- ' + x.split('dunstify')[1] for x in curr]
        return Style.green('Your reminders:\n') +\
            Style.green('\n'.join(texts))

    def handle_remove(self, args):
        # hash of the reminder
        if not len(args) == 1:
            return Style.red("Just provide the hash of the reminder.")
        hash = args[0].strip()
        curr = self.get_curr_jobs()
        filtered = [x for x in curr if ' # ASSISTANT '+hash in x]
        if not filtered:
            return Style.red("No such reminder found")
        # now remove
        newjobs = [x for x in curr if ' # ASSISTANT ' + hash not in x]
        self.update_cron(newjobs)
        return Style.green("Removed the reminder")

    def handle_set(self, args):
        """
        @args: list of args
        """
        if not len(args) >= 4 or args[0] != 'every':
            return self.invalid_msg
        # parse number
        timeval = args[1]
        try:
            int(timeval)
        except ValueError:
            return self.invalid_msg
        # check interval
        interval = args[2]
        if interval not in self.VALID_TIMES:
            return Style.red(
                "Invalid interval '{}'. Supported intervals are: {}".
                format(interval, str(self.VALID_TIMES))
            )
        # everything okay
        msg = ' '.join(args[3:])
        timestr = "{} {} {} * *"
        m = h = d = "*"
        if "min" in interval:
            m = "*/"+timeval
        elif "hour" in interval:
            m = "0"
            h = "*/"+timeval
        elif "day" in interval:  # this does not seem very useful
            m = h = "0"
            d = "*/"+timeval
        timestr = timestr.format(m, h, d)
        cronentry = '{} DISPLAY=:0.0 dunstify REMINDER "{}"'.format(
            timestr, msg
        )
        # hash and get first 6 hex
        hashed = hashlib.md5(cronentry.encode()).hexdigest()[:4]
        cronentry += " # ASSISTANT "+hashed
        jobs = self.get_curr_jobs()
        jobs.append(cronentry)
        # update cron
        try:
            self.update_cron(jobs)
        except Exception as e:
            return Style.green("Reminder could not be set: " + e)
        return Style.green('Your new reminder has been set!')

    def update_cron(self, jobs):
        # write to a tempfile
        with open('/tmp/assistant.cron', 'w') as f:
            f.write('\n'.join(jobs))
            f.write('\n')
        os.system('crontab /tmp/assistant.cron')


if __name__ == '__main__':
    r = ReminderService()

    # get port from arg
    port = sys.argv[1]

    # run it
    try:
        r.initialize_and_run(port)
    except Exception as e:
        print(traceback.format_exc())
