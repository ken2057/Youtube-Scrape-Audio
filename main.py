import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# ------------------------------------------------------------------------------
from src.CreateThread import thrDownload, thrFetchSong, newThread, thrSong, thrWriteJson
from src.config import JSON_DOWNLOADED_PATH, JSON_MCONFIG_PATH, DOWN_FOLDER, ERROR_PATH, CMD
from src.formatPrint import clearScreen, printSongs, printHelp, printMusicStatus
from src.IO import readJson, updateConfig, writeJson, deleteAllSong, writeErrorLog
from src.audio import downloadAudio, playSound
from src.utils import getSongId
from src.ScrapeYoutube import fetchQuery
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
songs = readJson()[0:5]
downs = readJson(JSON_DOWNLOADED_PATH)
result = []
last_cmd = None
running = True
# ------------------------------------------------------------------------------
# function
# ------------------------------------------------------------------------------
def playSong(songInput):
    global song
    # check song
    downloadAudio(songInput)
    # fetch next songs from page
    thrFetchSong(songInput['url'])
    # start
    song = Song()
    song.curSong = songInput
    musicThread = thrSong(song)
    musicThread.daemon = True
    musicThread.start()

def delete_all():
    print('Delete all file in audio/')
    # confirm delete
    confirm = input('Confirm (yes/no): ')
    if confirm.lower().strip(' \t') not in ['y', 'yes']:
        return
    if song.mixer != None:
        song.mixer.unload()
        song.reset_all()
    deleteAllSong()

def _songs(input_):
    global last_cmd, songs
    try:
        page = int(input_[1]) - 1
    except:
        page = 0
    # read json
    allSong = readJson()
    # check when input page too low or high
    totalPage = int(len(allSong) / 5) + 1
    if page < 0 or page > totalPage:
        return
    # renew songs
    songs = allSong[page * 5: page * 5 + 5]
    # print format songs
    # add some note command
    notes = []
    notes.append("Use 'songs <page>' to change page")
    notes.append("Use 'play|p <sID>' to play")
    printSongs(songs, page, totalPage, '\n'.join(notes))
    # save last cmd 'songs'
    last_cmd = 'sg'

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
        if os.path.exists(DOWN_FOLDER+'/'+getSongId(s['url'])+'.mp3'):
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
    # 5 song each page
    downs = downs[page * 5: page * 5 + 5]
    printSongs(downs, page, int(m/5) + 1, "Use 'play|p <sID>' to play")
    last_cmd = 'd'

def _search(string):
    global last_cmd, result
    # only get first 7
    result = fetchQuery(' '.join(string))[:7]
    printSongs(result, 0, 1, "Use 'play|p <sID>' to play")
    last_cmd = 's'

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
        playSong(play_cmd[last_cmd][int(input_[1])])
        last_cmd = None
    # if pause => unpause
    elif len(input_) == 1 and song.isPause:
            song.unpause_song()
    else:
        print('Nothing to play')

def _volume(i):
    if (len(i) == 1):
        print("Volume:",str(round(float(readJson(JSON_MCONFIG_PATH)['volume']) * 100, 2))+'%')
    else:
        updateConfig({'volume': float(i[1]) / 100})
        if song.mixer != None:
            song.mixer.set_volume(float(i[1]) / 100)

def _next():
    if song.nextSong == {}:
        song.select_nextSong()
    song.next_song()
    song.set_mixer(skip=True)

def _next_info():
    global last_cmd

    if song.curSong != {}:
        song.select_nextSong()
        printSongs([song.nextSong], 0, 1, "Use 'next|n' to play")
        last_cmd = None
    else:
        print('Next song: None')

def _skip(num):
    if song.isPlaying and song.is_skipable(num):
        song.skip_time(num)
    else:
        print('Skip failed')

def _info():
    global last_cmd

    printSongs([song.curSong], 0, 1)
    last_cmd = None

def _prev_info():
    global last_cmd

    if song.prevSong != {}:
        printSongs([song.prevSong], 0, 1, "Use 'prev' to play")
        last_cmd = None

def _prev():
    if song.prevSong != {}:
        song.prev_song()
        song.set_mixer(skip=True)
    else:
        print('Next song: None')

def _exit():
    global running
    running = False
# ------------------------------------------------------------------------------
# RUNNING
# ------------------------------------------------------------------------------

def main(dict_cmd):
    while running:
        print()
        printMusicStatus(song)
        i = input('$ ').strip(' ').split(' ')
        try:
            for key in CMD:
                if i[0] in CMD[key]:
                    dict_cmd[key](i)
                    break
            else:
                print('Command \'%s\' not found'%(i[0]))
            
        except Exception as ex:
            writeErrorLog(str(ex), 'main', ' '.join(i))

if __name__ == '__main__':
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
        'delete_all': (lambda x: delete_all()),
        'previous_info': (lambda x: _prev_info()),
        'previous': (lambda x: _prev())
    }

    main(dict_cmd)