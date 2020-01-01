# base url
BASE_URL = 'https://www.youtube.com'
QUERY_URL = 'https://www.youtube.com/results?search_query='

# id of element of youtube recommend
ID_REC = 'watch7-sidebar-modules'

# json save all the song have been clicked
JSON_NAME_PATH = 'json/link.json'
JSON_PLAYLIST_PATH = 'json/playlist.json'
JSON_DOWNLOADED_PATH = 'json/downloaded.json'
JSON_MCONFIG_PATH = 'json/music-config.json'
JSON_COOKIE_PATH = 'json/cookie.json'

# error file
ERROR_PATH = 'error.log'

# json format
JSON_FORMAT = ['url', 'title', 'time', 'channel', 'views']

# audio download folder
DOWN_FOLDER = 'audio'

# download option
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }],
}