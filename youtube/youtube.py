import requests
import urllib
import os

YOUTUBE_URL = 'https://www.youtube.com/watch?v={videourl}'

class NoVideoFound(Exception):
    pass

class Youtube():
    def __init__(self):
        self._key = os.environ['API_KEY']
        self._url = 'https://www.googleapis.com/youtube/v3/search?{urlparams}'
        self._base_params = {
            'key':self._key,
            'part':'snippet',
        }

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
        return YOUTUBE_URL.format(videourl=first['id']['videoId'])
