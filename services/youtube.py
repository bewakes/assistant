import requests
import urllib
import os
import sys
from handler import SocketMixin

YOUTUBE_URL = 'https://www.youtube.com/watch?v={videourl}&vq={quality}'

class NoVideoFound(Exception):
    pass

class Youtube(SocketMixin):
    """
    Service to query songs and get youtube urls from youtube api
    """
    def __init__(self):
        self._key = os.environ['API_KEY']
        self._url = 'https://www.googleapis.com/youtube/v3/search?{urlparams}'
        self._base_params = {
            'key':self._key,
            'part':'snippet',
        }

        self._current_song_url = ""
        self._vlc_pid = None

    def search(self, queryparam):
        params = dict(self._base_params)
        params['q'] = queryparam
        url = self._url.format(urlparams=urllib.parse.urlencode(params))
        resp = requests.get(url)
        return resp.json()

    def search_and_get_first_videourl(self, queryparam):
        result = self.search(queryparam)
        for x in result['items']:
            if x['id']['kind'] == 'youtube#video' and x['id'].get('videoId'):
                first = x
                break
        else:
            raise NoVideoFound
        return YOUTUBE_URL.format(videourl=first['id']['videoId'], quality='tiny')

    def handle_command(self, command):
        """
        This has been overridden from the mixin
        """
        cmd_args = command.decode('ascii').split()
        cmd = cmd_args[0]
        args = ' '.join(cmd_args[1:])

        # TODO: make the following cleaner, can have multiple commands
        if cmd == 'song_url':
            return self.search_and_get_first_videourl(args)
        elif cmd == 'playlist_url':
            # TODO: complete this
            return ''

if __name__ == '__main__':
    y = Youtube()

    # get port from arg
    port = sys.argv[1]

    # run it
    y.initialize_and_run(port)
