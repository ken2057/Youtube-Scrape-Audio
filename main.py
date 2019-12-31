import os, time, platform
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import threading
# ------------------------------------------------------------------------------
from src.IO import readJson, updateConfig
from src.CreateThread import download, fetchSong, newThread, thrSong
from src.audio import downloadAudio, playSound, getSongId, Song
from src.config import JSON_DOWNLOADED_PATH, JSON_MCONFIG_PATH
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
# ------------------------------------------------------------------------------
# function
# ------------------------------------------------------------------------------
def clearScreen():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

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

def printSongs(listSong, page, totalPage):
    clearScreen()
    print('-'*5)
    for i, s in enumerate(listSong, 0):
        print('id: ', i)
        print(s['title'])
        print(s['time'])
        print(s['channel'])
        print(s['views'])
        print('-'*5)
    print("Current page: %s/%s"%(page + 1, totalPage))

def pause():
    song.pause = True
    song.playing = False
    song.mixer.pause()

def unpause():
    song.pause = False
    song.playing = True
    song.mixer.unpause()  
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
        elif i[0] == 'play':
            if len(songs) != 0:
                playSong(songs[int(i[1])])
            else:
                print('Nothing to play')
        # play song downloaded
        elif i[0] == 'playd':
            if len(downs) != 0:
                playSong(downs[int(i[1])])
        elif i[0] == 'volume':
            if (len(i) == 1):
                print('Volume: ', readJson(JSON_MCONFIG_PATH)['volume'])
            elif song.mixer != None:
                updateConfig({'volume': float(i[1])})
                song.mixer.set_volume(float(i[1]))
        elif i[0] == 'downs':
            downs = readJson(JSON_DOWNLOADED_PATH)
            printSongs(downs, 0, 1)
        # final 
        elif i[0] != '':
            print('Command \'%s\' not exists'%(i[0]))
        
    except Exception as ex:
        print('error:', ex)
    print()
