import requests
import traceback
import urllib
import os
import sys
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils import log  # noqa

logger = log.get_logger('Youtube Search')

YOUTUBE_URL = 'https://www.youtube.com/watch?v={videourl}'


class NoVideoFound(Exception):
    pass


class Youtube(SocketHandlerMixin):
    """
    Service to query songs and get youtube urls from youtube api
    """
    def __init__(self):
        self._key = os.environ['API_KEY']
        self._url = 'https://www.googleapis.com/youtube/v3/search?{urlparams}'
        self._base_params = {
            'key': self._key,
            'part': 'snippet',
        }

        self._current_song_url = ""
        self._vlc_pid = None
        self.FILENAME = 'songs'
        self.songs = self.get_local_songs()

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
            logger.warn("Could not get Youtube search result for '{}'".format(
                queryparam))
            return ""
        return YOUTUBE_URL.format(
            videourl=first['id']['videoId'],
            quality='tiny'
        )

    def _get_path(self):
        dirname = os.path.expanduser('~/.assistant')
        path = os.path.join(dirname, self.FILENAME)
        return path

    def get_local_songs(self):
        path = self._get_path()
        songs = {}
        try:
            with open(path) as f:
                for line in f.readlines():
                    splitted = line.split()
                    songname = ' '.join(splitted[1:])
                    songs[songname] = splitted[0]
        except FileNotFoundError:
            return {}
        return songs

    def append_song_url_to_local_file(self, query, url):
        with open(self._get_path(), 'a') as f:
            f.write('{} {}\n'.format(url, query))

    def local_result(self, query):
        # TODO: a bit more sophisticated. This is too naive
        for song in self.songs.keys():
            if set(song.split()) == set(query.split()):
                return self.songs[song]
        return None

    def handle_search(self, args):
        if not isinstance(args, list):
            query = args
        else:
            query = ' '.join(args)
        logger.info("QUERY: " + query)
        if query == 'random':
            song = random.choice(list(self.songs.keys()))
            return self.songs[song]
        # first check if query song exists locally
        result = self.local_result(query)
        if result:
            logger.info('Song found locally..')
            return result
        else:
            logger.info('Song not found locally..')
            result = self.search_and_get_first_videourl(query)
            self.songs[query] = result
            # append to file
            self.append_song_url_to_local_file(query, result)
            return result

    def handle_playlist(self, args):
        # TODO: implement
        return ""

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


class SongSearcher(Youtube):
    """Same as Youtube for now as it uses youtube search.
    """
    # TODO: add searching in local file as well
    pass

if __name__ == '__main__':
    y = Youtube()

    # get port from arg
    port = sys.argv[1]

    # run it
    try:
        y.initialize_and_run(port)
    except:
        print(traceback.format_exc())
