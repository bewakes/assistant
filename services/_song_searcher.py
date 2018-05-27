import requests
import traceback
import urllib
import os
import re
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
        self.songs_dir = os.path.expanduser('~/Music/assistant/')
        self._key = os.environ['API_KEY']
        self._url = 'https://www.googleapis.com/youtube/v3/search?{urlparams}'
        self._base_params = {
            'key': self._key,
            'part': 'snippet',
        }
        self._current_song_url = ""
        self._vlc_pid = None
        self.FILENAME = 'songs'
        self.songs = self.get_songs_paths()

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

    def get_songs_paths(self):
        """
        Return dict of song name and path or url of the song
        """
        # first create dict of songs: youtube url
        path = self._get_path()
        songs = {}
        try:
            with open(path) as f:
                for line in f.readlines():
                    splitted = line.split()
                    songname = ' '.join(splitted[1:])
                    songs[songname] = splitted[0]
        except FileNotFoundError:
            songs = {}
        # Now lookup in ~/Music/assistant/ dir
        # this will override youtube url with local filepath
        # List files in songs_dir
        listing = [
            x for x in os.listdir(self.songs_dir)
            if os.path.isfile(os.path.join(self.songs_dir, x))
        ]
        for f in listing:
            songname = re.match('^(.*)\.mp3$', f).groups(1)[0]
            songs[songname] = os.path.join(self.songs_dir, f)
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
            return (song, self.songs[song])
        # first check if query song exists locally
        result = self.local_result(query)
        if result:
            logger.info('Song found locally..')
            return (query, result)
        else:
            logger.info('Song not found locally..')
            result = self.search_and_get_first_videourl(query)
            self.songs[query] = result
            # append to file
            self.append_song_url_to_local_file(query, result)
            return (query, result)

    def handle_search_playlist(self, args):
        if not isinstance(args, list):
            query = args
        else:
            query = ' '.join(args)
        if query == 'random':
            # shuffle the songs and send list of urls/paths
            songs = list(self.songs.keys())
            random.shuffle(songs)
            return [(x, self.songs[x]) for x in songs]
        return None

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
    # TODO: add searching songs in local directories as well
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
