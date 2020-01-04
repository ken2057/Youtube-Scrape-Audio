import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# ------------------------------------------------------------------------------
from src.io import readJson, updateConfig, writeJson, deleteAllSong, writeErrorLog, getInDownloaded, writeSongQueue
from src.config import JSON_DOWNLOADED_PATH, JSON_MCONFIG_PATH, DOWN_FOLDER, ERROR_PATH, CMD, SONG_PER_LIST
from src.createThread import thrDownload, thrFetchSong, newThread, thrSong, thrWriteJson
from src.formatPrint import clearScreen, printSongs, printHelp, printMusicStatus
from src.audio import downloadAudio, playSound
from src.scrapeYoutube import fetchQuery
from src.utils import getSongId
from src.object import Song
# ------------------------------------------------------------------------------
# TEMP
# ------------------------------------------------------------------------------
URL = 'https://www.youtube.com/watch?v=dCdxj-3IrWM'
URL_PLAYLIST = 'https://www.youtube.com/watch?v=qz7tCZE_3wA&list=RDqz7tCZE_3wA&start_radio=1'
QUERY_URL = 'https://www.youtube.com/results?search_query=y%C3%AAu+ch%C3%A2u+d%C6%B0%C6%A1ng'
# ------------------------------------------------------------------------------
# Global Varible
# ------------------------------------------------------------------------------
song = Song()
songs = readJson()[0:SONG_PER_LIST]
downs = readJson(JSON_DOWNLOADED_PATH)
result = []
last_cmd = None
running = True
# ------------------------------------------------------------------------------
# function
# ------------------------------------------------------------------------------

# play song with songInput
def playSong(songInput):
    global song
    # check does downloaded
    songInput = getInDownloaded(songInput)
    # check song
    downloadAudio(songInput)
    # fetch next songs from page
    thrFetchSong(songInput['url'])
    # start
    song.reset_all()
    song.curSong = songInput
    musicThread = thrSong(song)
    musicThread.daemon = True
    musicThread.start()

# delete all mp3, json
def _delete_all():
    print('Delete all file in audio/')
    # confirm delete
    confirm = input('Confirm (yes/no): ')
    if confirm.lower().strip(' \t') not in ['y', 'yes']:
        return
    if song.mixer != None:
        song.mixer.unload()
        song.reset_all()
    deleteAllSong()

# show song recommended by YT
def _songs(input_):
    global last_cmd, songs
    try:
        page = int(input_[1]) - 1
    except:
        page = 0
    # read json
    allSong = readJson()
    # check when input page too low or high
    totalPage = int(len(allSong) / SONG_PER_LIST) + 1
    if page < 0 or page > totalPage:
        return
    # renew songs
    songs = allSong[page * SONG_PER_LIST: page * SONG_PER_LIST + SONG_PER_LIST]
    # print format songs
    # add some note command
    notes = []
    notes.append("Use 'songs <page>' to change page")
    notes.append("Use 'play|p <sID>' to play")
    printSongs(songs, page, totalPage, '\n'.join(notes))
    # save last cmd 'songs'
    last_cmd = 'sg'

# show downoaded song
def _downloaded(input_):
    global downs, last_cmd
    try:
        page = int(input_[1]) - 1
    except:
        page = 0

    downs = readJson(JSON_DOWNLOADED_PATH)
    # check file exist
    # if not remove from json
    newDowns = []
    for s in downs:
        if os.path.exists(s['path']):
            newDowns.append(s)

    # check when page to low or high
    m = min(len(downs), len(newDowns))
    if page < 0:
        page = 0
    elif page > m:
        page = m
    # not equal => some mp3 have been delete
    # => set downs = newDown and write new download to json
    if len(downs) != len(newDowns):
        writeJson(newDowns, JSON_DOWNLOADED_PATH)
        downs = newDowns
    #  song each page
    downs = downs[page * SONG_PER_LIST: page * SONG_PER_LIST + SONG_PER_LIST]
    printSongs(downs, page, int(m/SONG_PER_LIST) + 1, "Use 'play|p <sID>' to play")
    last_cmd = 'd'

# search song from scrape youtube
def _search(string):
    global last_cmd, result
    # only get first 7
    result = fetchQuery(' '.join(string))[:7]
    printSongs(result, 0, 1, "Use 'play|p <sID>' to play")
    last_cmd = 's'

# play song in songs/search/downloaded current page
def _play(input_):
    global last_cmd
    # check last command used
    # if in ['songs', 'downs', 'search']
    # play song from that list
    if last_cmd != None and len(input_) > 1:
        play_cmd = {
            'sg': songs,
            'd': downs,
            's': result
        }
        # play sone from other will stop queue
        if song.queue != []:
            song.queue = []
        playSong(play_cmd[last_cmd][int(input_[1])])
    # if pause => unpause
    elif len(input_) == 1 and song.isPause:
            song.unpause_song()
    else:
        print('Nothing to play')

# show current volume
# change volume with num
def _volume(i):
    if (len(i) == 1):
        print("Volume:",str(round(float(readJson(JSON_MCONFIG_PATH)['volume']) * 100, 2))+'%')
    else:
        updateConfig({'volume': float(i[1]) / 100})
        if song.mixer != None:
            song.mixer.set_volume(float(i[1]) / 100)

# play next song
def _next():
    if song.nextSong == {}:
        song.select_nextSong()
    song.next_song()
    song.set_mixer(skip=True)

# show next song info
def _next_info():
    global last_cmd

    if song.curSong != {}:
        song.select_nextSong()
        printSongs([song.nextSong], 0, 1, "Use 'next|n' to play")
        last_cmd = None
    else:
        print('Next song: None')

# skip num seconds of the song
def _skip(num):
    if song.isPlaying and song.is_skipable(num):
        song.skip_time(num)
    else:
        print('Skip failed')

# show current song info
def _info():
    global last_cmd

    printSongs([song.curSong], 0, 1)
    last_cmd = None

# shot previous info
def _prev_info():
    global last_cmd
    if song.prevSong != {}:
        printSongs([song.prevSong], 0, 1, "Use 'prev' to play")
        last_cmd = None

# play previous song
def _prev():
    if song.prevSong != {}:
        song.prev_song()
        song.set_mixer(skip=True)
    else:
        print('Next song: None')

# stop
def _exit():
    global running
    running = False

# play all song in downloaded
def _play_down():
    songs = readJson(JSON_DOWNLOADED_PATH)
    song.queue = songs[1:]
    playSong(songs[0])

# show queue
def _queue():
    if song.queue != []:
        writeSongQueue(song)
    else:
        print('Nothing in queue')

# turn on shuffle queue song
def _queue_shuffle():
    song.isShuffle = not song.isShuffle
    _a = (lambda x: 'ON' if x else 'OFF')
    print('Queue shuffle:', _a(song.isShuffle))

# ------------------------------------------------------------------------------
# RUNNING
# ------------------------------------------------------------------------------

def main(dict_cmd):
    while running:
        print()
        printMusicStatus(song)
        i = input('$ ').strip(' ').split(' ')
        try:
            # if input in array of CMD
            # use that key of CMD to active function in dict_cmd
            for key in CMD:
                if i[0] in CMD[key]:
                    dict_cmd[key](i)
                    break
            else:
                if i[0] != '':
                    print('Command \'%s\' not found'%(i[0]))
        except Exception as ex:
            writeErrorLog(str(ex), 'main', ' '.join(i))

if __name__ == '__main__':
    # this dict match with config.CMD
    dict_cmd = {
        'exit': (lambda x: _exit()),
        'pause': (lambda x: song.pause_song()),
        'unpause': (lambda x: song.unpause_song()),
        'clear': (lambda x: clearScreen()),
        'songs': (lambda x: _songs(x)),
        'downloaded': (lambda x: _downloaded(x)),
        'search': (lambda x: _search(' '.join(x[1:]))),
        'play': (lambda x: _play(x)),
        'volume': (lambda x: _volume(x)),
        'help': (lambda x: printHelp()),
        'next': (lambda x: _next()),
        'next_info': (lambda x: _next_info()),
        'skip': (lambda x: _skip(int(x[1]))),
        'info': (lambda x: _info()),
        'delete_all': (lambda x: _delete_all()),
        'previous_info': (lambda x: _prev_info()),
        'previous': (lambda x: _prev()),
        'play_downloaded': (lambda x: _play_down()),
        'queue': (lambda x: _queue()),
        'queue_shuffle': (lambda x: _queue_shuffle())
    }

    main(dict_cmd)
