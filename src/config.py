# max song per list
SONG_PER_LIST = 6

# base url
SHORT_URL = 'https://youtu.be/'
BASE_URL = 'https://www.youtube.com/watch?v='
QUERY_URL = 'https://www.youtube.com/results?search_query='

# json save all the song have been clicked
JSON_NAME_PATH = 'json/link.json'
JSON_PLAYLIST_PATH = 'json/playlist.json'
JSON_DOWNLOADED_PATH = 'json/downloaded.json'
JSON_MCONFIG_PATH = 'json/music-config.json'

# cookie for better recomend song
COOKIE_PATH = 'cookie.txt'

# error file
ERROR_PATH = 'error.log'

# json format
JSON_FORMAT = ['id', 'title', 'time', 'channel', 'views']

# audio download folder
DOWN_FOLDER = 'audio/'

# download option
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'outtmpl':  DOWN_FOLDER+'%(title)s-%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }],
    'cookiefile': COOKIE_PATH,
    'quiet': True
}

# list error number will not print info
ERROR_HIDE = [
    '[Errno 11001]', # No internet: Failed to establish a new connection
]

# CMD LIST
# if input have more than 1 word, it will show search
CMD = {
    'exit':                 ['exit', 'X'],
    'pause':                ['pause', 'P'],
    'unpause':              ['unpause'],
    'clear':                ['clear', 'cls'],
    'songs':                ['songs'],
    'downloaded':           ['downloaded', 'downs', 'd'],
    'search':               ['search', 's'],
    'play':                 ['play', 'p'],
    'volume':               ['volume', 'v'],
    'help':                 ['help', 'h'],
    'next':                 ['next', 'n'],
    'next_info':            ['nexti', 'ni', 'nextinfo'],
    'skip':                 ['skip'],
    'info':                 ['info', 'i'],
    'delete_all':           ['delete-all'],
    'previous':             ['prev'],
    'previous_info':        ['previ'],
    'play_downloaded':      ['pd', 'playdowns', 'playdownloaded'],
    'queue':                ['queue', 'q'],
    'queue_shuffle':        ['qsf', 'qshuffle'],
    'copy':                 ['copy', 'cp'], # copy current song url
    'delete':               ['delete', 'del'],
    'repeat':               ['repeat', 're'],
}