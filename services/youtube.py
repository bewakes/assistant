import requests
import urllib
import os
import sys
import subprocess

import socket

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
        self._vlc_command = "cvlc --vout none {url}"

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
        return YOUTUBE_URL.format(videourl=first['id']['videoId'])

    def _play_with_vlc(self, video_url):
        command = self._vlc_command.format(url=video_url)
        process = subprocess.Popen(command.split())#, stdout=IPE)
        self._vlc_pid = process.pid
        output, error = process.communicate()

    def play_song(self, songname):
        print("SONG", songname)
        url = self.search_and_get_first_videourl(songname)
        self._play_with_vlc(url)

if __name__ == '__main__':
    y = Youtube()
    y.play_song(' '.join(sys.argv[1:]))
    port = int(sys.argv[1])
    assert False

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))
    s.listen(5) # number of unaccepted connections allowed before none accpted is 5
    conn, addr = s.accept()

    with conn:
        while True:
            songname = conn.recv(1024)
            print(songname)
            conn.send(y.search_and_get_first_videourl(songname).encode())

