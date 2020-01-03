import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# ------------------------------------------------------------------------------
from src.CreateThread import thrDownload, thrFetchSong, newThread, thrSong, thrWriteJson
from src.config import JSON_DOWNLOADED_PATH, JSON_MCONFIG_PATH, DOWN_FOLDER, ERROR_PATH
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
song.stop = True
musicThread = newThread()
songs = readJson()[0:5]
downs = readJson(JSON_DOWNLOADED_PATH)
result = []
last_cmd = None
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

def getDownload(input_):
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
    printSongs(downs, page, int(m/5) + 1, "Use 'playd|pd <sID>' to play")
    last_cmd = 'd'

def recommend_song(input_):
    global last_cmd, songs
    try:
        page = int(input_[1]) - 1
    except:
        page = 0
    # read json
    allSong = readJson()
    # check when input page too low or high
    totalPage = int(len(allSong) / 5)
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

def check_play(input_):
    global last_cmd
    
    if last_cmd != None and len(input_) == 2:
        play_cmd = {
            'sg': songs,
            'd': downs,
            's': result
        }
        playSong(play_cmd[last_cmd][int(input_[1])])
        last_cmd = None
    elif len(input_) == 1 and song.isPause:
            song.unpause_song()
    else:
        print('Nothing to play')
        

# ------------------------------------------------------------------------------
# RUNNING
# ------------------------------------------------------------------------------
while True:
    print()
    printMusicStatus(song)
    #
    i = input('$ ').strip(' ').split(' ')
    i[0] = i[0].lower()
    try:
        # exit
        if 'exit' in i:
            break
        # pause
        elif 'pause' == i[0]:
            song.pause_song()
        # unpause
        # when 'unpause' or input is 'play' and while paUse
        elif 'unpause' == i[0] or (len(i) == 1 and song.isPause and i[0] == 'play'):
            song.unpause_song()
        # play
        elif 'get' == i[0]:
            thrDownload(i[1])
        # clear/cls
        elif i[0] in ['cls', 'clear']:
            clearScreen()
        # getlist song recommended
        elif i[0] == 'songs':
            recommend_song(i)
        # get downloaded list
        elif i[0] in ['downs', 'd']:
            getDownload(i)
        # get search list
        elif i[0] in ['s', 'search']:
            # only get first 7
            result = fetchQuery(' '.join(i[1:]))[:7]
            printSongs(result, 0, 1, "Use 'plays|ps <sID>' to play")
            last_cmd = 's'
        # play song in list
        elif i[0] in ['play', 'p']:
            check_play(i)
        # change volume
        elif i[0] in ['volume', 'v']:
            if (len(i) == 1):
                print("Volume:",str(round(float(readJson(JSON_MCONFIG_PATH)['volume']) * 100, 2))+'%')
            else:
                updateConfig({'volume': float(i[1]) / 100})
                if song.mixer != None:
                    song.mixer.set_volume(float(i[1]) / 100)
        # help
        elif i[0] in ['h', 'help']:
            printHelp()
        # next song
        elif i[0] in ['n', 'next']:
            if song.nextSong != {}:
                song.next_song()
                song.set_mixer(skip=True)
            else:
                print('Next song: None')
        # next song info
        elif i[0] in ['ni', 'nexti']:
            if song.curSong != {}:
                song.select_nextSong()
                printSongs([song.nextSong], 0, 1, "Use 'next|n' to play")
                last_cmd = None
            else:
                print('Next song: None')
        # skip x seconds
        elif i[0] == 'skip':
            if song.isPlaying and song.is_skipable(int(i[1])):
                song.skip_time(int(i[1]))
            else:
                print('Skip failed')
        # current song info
        elif i[0] == 'info':
            printSongs([song.curSong], 0, 1)
            last_cmd = None
        elif i[0] == 'delete-all':
            delete_all()
        # final 
        elif i[0] != '':
            print('Command \'%s\' not found'%(i[0]))
        
    except Exception as ex:
        writeErrorLog(str(ex), 'main', ' '.join(i))
