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
    'exit':                 ['exit', 'X'],                              # exit
    'pause':                ['pause', 'P'],                             # pause song
    'unpause':              ['unpause'],                                # unpause song
    'clear':                ['clear', 'cls'],                           # clear screen
    'songs':                ['songs'],                                  # show songs recommend by Youtube
    'downloaded':           ['downloaded', 'downs', 'd'],               # show downloaed song
    'search':               ['search', 's'],                            # search based from Youtube
    'play':                 ['play', 'p'],                              # play song with sID
    'volume':               ['volume', 'v'],                            # show/change volume
    'help':                 ['help', 'h'],                              # show help
    'next':                 ['next', 'n'],                              # play next song
    'next_info':            ['nexti', 'ni', 'nextinfo'],                # next song info
    'skip':                 ['skip'],                                   # skip x time of current song
    'info':                 ['info', 'i'],                              # info curent song
    'delete_all':           ['delete-all'],                             # delete all json, mp3
    'previous':             ['prev'],                                   # play previous song
    'previous_info':        ['previ'],                                  # show previous song info
    'play_downloaded':      ['pd', 'playdowns', 'playdownloaded'],      # play all in downloaded
    'queue':                ['queue', 'q'],                             # show queue
    'queue_shuffle':        ['qsf', 'qshuffle'],                        # on/off shuffle queue
    'copy':                 ['copy', 'cp'],                             # copy current song url
    'delete':               ['delete', 'del'],                          # delete song/songs
    'repeat':               ['repeat', 're'],                           # repeat/unrepeat curent song
    'set_next':             ['setnext', 'setn'],                        # set next song
    'queue_add':            ['qadd', 'qa'],                         # add song to queue
    'queue_remove':         ['qremove', 'qr'],                      # remove song in queue
}