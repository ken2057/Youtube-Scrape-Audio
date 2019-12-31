import os, time
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# ------------------------------------------------------------------------------
from src.IO import readJson, updateConfig, writeJson
from src.CreateThread import download, fetchSong, newThread, thrSong, thrWriteJson
from src.audio import downloadAudio, playSound, getSongId, Song, getSongId
from src.config import JSON_DOWNLOADED_PATH, JSON_MCONFIG_PATH, DOWN_FOLDER
from src.ScrapeYoutube import fetchQuery
from src.formatPrint import clearScreen, printSongs, printHelp
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
# ------------------------------------------------------------------------------
# function
# ------------------------------------------------------------------------------
def playSong(songInput):
    global song
    # check song
    downloadAudio(songInput)
    # fetch song from page
    fetchSong(songInput['url'])
    # start
    song = Song()
    song.title = songInput['title']
    musicThread = thrSong(songInput, song)
    musicThread.start()
    time.sleep(1)

def pause():
    song.pause = True
    song.playing = False
    song.mixer.pause()

def unpause():
    song.pause = False
    song.playing = True
    song.mixer.unpause()  

def getDownload():
    global downs
    downs = readJson(JSON_DOWNLOADED_PATH)

    # check file exist
    # if not remove from json
    oldLen = len(downs)
    newDowns = []
    for s in downs:
        if os.path.exists(DOWN_FOLDER+'/'+getSongId(s['url'])+'.mp3'):
            newDowns.append(s)
    if len(downs) != len(newDowns):
        writeJson(newDowns, JSON_DOWNLOADED_PATH)
        downs = newDowns
    printSongs(downs, 0, 1)
# ------------------------------------------------------------------------------
# RUNNING
# ------------------------------------------------------------------------------
while True:
    if song.title != 'None':
        status = ''
        if song.playing:
            status = 'Playing: '
        elif song.pause:
            status = 'Pause: '
        print(status, song.title)
    #
    i = input('$ ').strip(' ').split(' ')
    i[0] = i[0].lower()
    try:
        # exit
        if 'exit' in i:
            break
        # pause
        elif 'pause' == i[0]:
            pause()
        # unpause
        # when 'unpause' or input is 'play' and while pausing
        elif 'unpause' == i[0] or (len(i) == 1 and song.pause and i[0] == 'play'):
            unpause()
        # play
        elif 'get' == i[0]:
            download(i[1])
        # clear/cls
        elif i[0] in ['cls', 'clear']:
            clearScreen()
        # list song
        elif i[0] == 'songs':
            try:
                page = int(i[1]) - 1
            except:
                page = 0
            # read json
            allSong = readJson()
            # check when input page too low or high
            totalPage = int(len(allSong) / 5) + 1
            if page < 0 or page > totalPage:
                continue
            # renew songs
            songs = allSong[page * 5: page * 5 + 5]
            # print format songs
            printSongs(songs, page, totalPage)
        # play song in list
        elif i[0] in ['play', 'p']:
            if len(songs) != 0:
                playSong(songs[int(i[1])])
            else:
                print('Nothing to play')
        # play song downloaded
        elif i[0] in ['playd', 'pd']:
            if len(downs) != 0:
                playSong(downs[int(i[1])])
        # play song from result query
        elif i[0] in ['plays', 'ps']:
            if len(result) != 0:
                playSong(result[int(i[1])])
        # change volume
        elif i[0] == 'volume':
            if (len(i) == 1):
                print('Volume: ', readJson(JSON_MCONFIG_PATH)['volume'])
            elif song.mixer != None:
                updateConfig({'volume': float(i[1])})
                song.mixer.set_volume(float(i[1]))
        # get downloaded list
        elif i[0] in ['downs', 'd']:
            getDownload()
        # search
        elif i[0] in ['s', 'search']:
            # only get first 8
            result = fetchQuery(' '.join(i[1:]))[:8]
            printSongs(result, 0, 1)
        # help
        elif i[0] in ['h', 'help']:
            printHelp()
        # final 
        elif i[0] != '':
            print('Command \'%s\' not found'%(i[0]))
        
    except Exception as ex:
        print('error:', ex)
    print()
