import os, time
from datetime import datetime
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# ------------------------------------------------------------------------------
from src.CreateThread import thrDownload, thrFetchSong, newThread, thrSong, thrWriteJson, thrWriteNext
from src.formatPrint import clearScreen, printSongs, printHelp, printMusicStatus
from src.config import JSON_DOWNLOADED_PATH, JSON_MCONFIG_PATH, DOWN_FOLDER, ERROR_PATH
from src.IO import readJson, updateConfig, writeJson, deleteAllSong
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
    time.sleep(1)
    song.nextSong = readJson()[0]

def getDownload(page):
    global downs
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
        elif 'unpause' == i[0] or (len(i) == 1 and song.pause and i[0] == 'play'):
            song.unpause_song()
        # play
        elif 'get' == i[0]:
            thrDownload(i[1])
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
            totalPage = int(len(allSong) / 5)
            if page < 0 or page > totalPage:
                continue
            # renew songs
            songs = allSong[page * 5: page * 5 + 5]
            # print format songs
            # add some note command
            notes = []
            notes.append("Use 'songs <page>' to change page")
            notes.append("Use 'play|p <sID>' to play")
            printSongs(songs, page, totalPage, '\n'.join(notes))
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
        elif i[0] in ['volume', 'v']:
            if (len(i) == 1):
                print("Volume:",str(round(float(readJson(JSON_MCONFIG_PATH)['volume']) * 100, 2))+'%')
            else:
                updateConfig({'volume': float(i[1]) / 100})
                if song.mixer != None:
                    song.mixer.set_volume(float(i[1]) / 100)
        # get downloaded list
        elif i[0] in ['downs', 'd']:
            try:
                page = int(i[1]) - 1
            except:
                page = 0
            getDownload(page)
        # search
        elif i[0] in ['s', 'search']:
            # only get first 7
            result = fetchQuery(' '.join(i[1:]))[:7]
            printSongs(result, 0, 1, "Use 'plays|ps <sID>' to play")
        # help
        elif i[0] in ['h', 'help']:
            printHelp()
        # next song
        elif i[0] in ['n', 'next']:
            if song.nextSong != {}:
                song.next_song()
                song.set_mixer(skip=True)
                time.sleep(1)
                song.nextSong = readJson()[0]
            else:
                print('Next song: None')
        # next song info
        elif i[0] in ['ni', 'nexti']:
            if song.nextSong != {}:
                song.select_nextSong()
                printSongs([song.nextSong], 0, 1, "Use 'next|n' to play")
            else:
                print('Next song: None')
        # skip x seconds
        elif i[0] == 'skip':
            if song.playing and song.is_skipable(int(i[1])):
                song.skip_time(int(i[1]))
            else:
                print('Skip failed')
        # current song info
        elif i[0] == 'info':
            printSongs([song.curSong], 0, 1)
        elif i[0] == 'delete-all':
            print('Delete all file in audio/')
            # confirm delete
            confirm = input('Confirm (yes/no): ')
            if confirm.lower().strip(' \t') not in ['y', 'yes']:
                continue
            if song.mixer != None:
                song.mixer.unload()
                song.reset_all()
            deleteAllSong()
        # final 
        elif i[0] != '':
            print('Command \'%s\' not found'%(i[0]))
        
    except Exception as ex:
        print('error:', ex)
        # write error to file
        lines = []
        lines.append('Time: ' + datetime.now().__str__())
        lines.append("Input: '" + ' '.join(i) + "'")
        lines.append('Error: ' + str(ex) + '\n')
        thrWriteNext('\n'.join(lines), ERROR_PATH)
