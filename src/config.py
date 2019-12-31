# base url
BASE_URL = 'https://www.youtube.com'

# id of element of youtube recommend
ID_REC = 'watch7-sidebar-modules'

# json save all the song have been clicked
JSON_NAME_PATH = 'data/link.json'
JSON_PLAYLIST_PATH = 'data/playlist.json'
JSON_DOWNLOADED_PATH = 'data/downloaded.json'
JSON_MCONFIG_PATH = 'music-config.json'

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

#
DEFAULT_VOLUME = 0.05