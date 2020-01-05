from os import path
from pyperclip import copy

from src.io import (
    readJson, 
    writeJson, 
    updateConfig, 
    deleteAllSong, 
    writeErrorLog, 
    writeSongQueue,
    deleteSongs
)
from src.config import (
    JSON_DOWNLOADED_PATH, 
    JSON_MCONFIG_PATH, 
    DOWN_FOLDER, 
    ERROR_PATH, CMD, 
    SONG_PER_LIST,
    SHORT_URL
)
from src.createThread import (
    thrSong, 
    thrFetchSong, 
)
from src.formatPrint import (
    printHelp, 
    printSongs, 
    clearScreen, 
    printMusicStatus,
)
from src.audio import (
    downloadAudio, 
)
from src import Song
from src.scrapeYoutube import fetchQuery

class Main():
    def __init__(self):
        self.song = Song()
        self.songs = []
        self.downs = []
        self.result = []
        self.last_cmd = None
        self.running = False
        self.musicThread = None

        # this will match key with config.CMD
        # for fast input matching
        self.dict_cmd = {
            'exit':             (lambda x: self._exit()),
            'pause':            (lambda x: self.song.pause_song()),
            'unpause':          (lambda x: self.song.unpause_song()),
            'clear':            (lambda x: self._clear()),
            'songs':            (lambda x: self._songs(x)),
            'downloaded':       (lambda x: self._downloaded(x)),
            'search':           (lambda x: self._search(' '.join(x[1:]))),
            'play':             (lambda x: self._play(x)),
            'volume':           (lambda x: self._volume(x)),
            'help':             (lambda x: printHelp()),
            'next':             (lambda x: self._next()),
            'next_info':        (lambda x: self._next_info()),
            'skip':             (lambda x: self._skip(x)),
            'info':             (lambda x: self._info()),
            'delete_all':       (lambda x: self._delete_all()),
            'previous_info':    (lambda x: self._prev_info()),
            'previous':         (lambda x: self._prev()),
            'play_downloaded':  (lambda x: self._play_down()),
            'queue':            (lambda x: self._queue()),
            'queue_shuffle':    (lambda x: self._queue_shuffle()),
            'copy':             (lambda x: self._copy()),
            'delete':           (lambda x: self._delete(x)),
            'repeat':           (lambda x: self._repeat(x))
        }

    # play song with songInput
    def playSong(self, songInput):
        # check song
        self.song.curSong = downloadAudio(songInput)
        # fetch next songs from page
        thrFetchSong(self.song.curSong['id'])
        # check exist thread
        if self.musicThread == None:
            self.musicThread = thrSong(self.song)
            self.musicThread.daemon = True
            self.musicThread.start()
        else:
            self.song.set_mixer(True)

    # Call this function to run
    def _running(self):
        self.running = True
        while self.running:
            print()
            printMusicStatus(self.song)
            i = input('$ ').strip(' ').split(' ')
            try:
                # if input in array of CMD
                # use that key of CMD to active function in dict_cmd
                for key in CMD:
                    if i[0] in CMD[key]:
                        self.dict_cmd[key](i)
                        break
                else:
                    if i[0] != '':
                        print('Command \'%s\' not found'%(i[0]))
            except Exception as ex:
                writeErrorLog(ex, ' '.join(i))

    # delete all mp3, json
    def _delete_all(self):
        print('Delete all file in json, cookie and audio/')
        # confirm delete
        confirm = input('Confirm (yes/no): ')
        if confirm.lower().strip(' \t') not in ['y', 'yes']:
            return
        if self.song.mixer != None:
            self.song.mixer.unload()
            self.song.reset_all()
            self.musicThread = None
        deleteAllSong()

    def _clear(self):
        clearScreen()
        self.last_cmd = None

    # show song recommended by YT
    def _songs(self, input_):
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
        self.songs = allSong[page * SONG_PER_LIST: page * SONG_PER_LIST + SONG_PER_LIST]
        # print format songs
        # add some note command
        notes = []
        notes.append("Use 'songs <page>' to change page")
        notes.append("Use 'play|p <sID>' to play")
        printSongs(self.songs, page, totalPage, '\n'.join(notes))
        # save last cmd 'songs'
        self.last_cmd = 'sg'

    # show downoaded song
    def _downloaded(self, input_):
        try:
            page = int(input_[1]) - 1
        except:
            page = 0

        self.downs = readJson(JSON_DOWNLOADED_PATH)
        # check file exist
        # if not remove from json
        newDowns = []
        for s in self.downs:
            if path.exists(s['path']):
                newDowns.append(s)

        # check when page to low or high
        m = min(len(self.downs), len(newDowns))
        if page < 0:
            page = 0
        elif page > m:
            page = m
        # not equal => some mp3 have been delete
        # => set downs = newDown and write new download to json
        if len(self.downs) != len(newDowns):
            writeJson(newDowns, JSON_DOWNLOADED_PATH)
            self.downs = newDowns
        #  song each page
        self.downs = self.downs[page * SONG_PER_LIST: page * SONG_PER_LIST + SONG_PER_LIST]
        printSongs(self.downs, page, int(m/SONG_PER_LIST) + 1, "Use 'play|p <sID>' to play")
        self.last_cmd = 'd'

    # search song from sc(
    # rape youtube
    #)
    def _search(self, string):
        # only get first 7
        self.result = fetchQuery(string)[:SONG_PER_LIST]
        printSongs(self.result, 0, 1, "Use 'play|p <sID>' to play")
        self.last_cmd = 's'

    # play song in songs/search/downloaded current page
    def _play(self, input_):
        # check last command used
        # if in ['songs', 'downs', 'search']
        # play song from that list
        if self.last_cmd != None and len(input_) > 1:
            play_cmd = {
                'sg': self.songs,
                'd': self.downs,
                's': self.result
            }
            # play sone from other will stop queue
            if self.song.queue != []:
                self.song.queue = []
            self.playSong(play_cmd[self.last_cmd][int(input_[1])])
        # if pause => unpause
        elif len(input_) == 1 and self.song.isPause:
                self.song.unpause_song()
        else:
            print('Nothing to play')

    # show current volume
    # change volume with num
    def _volume(self, i):
        # print volume level    
        if (len(i) == 1):
            print("Volume:", 
                str(round(float(readJson(JSON_MCONFIG_PATH)['volume']) * 100, 2)) + '%')
        # change volume level
        else:
            updateConfig({'volume': float(i[1]) / 100})
            if self.song.mixer != None:
                self.song.mixer.set_volume(float(i[1]) / 100)

    # play next song
    def _next(self):
        self.song.select_nextSong()
        self.song.next_song()
        self.song.set_mixer(skip=True)

    # show next song info
    def _next_info(self):
        self.song.select_nextSong()
        printSongs([self.song.nextSong], 0, 1, "Use 'next|n' to play")
        self.last_cmd = None

    # skip num seconds of the song
    def _skip(self, i):
        if len(i) < 2:
            print('Add total second want to skip')
            return
        if (self.song.isPlaying or self.song.isPause):
            if self.song.is_skipable(int(i[1])):
                self.song.skip_time(int(i[1]))
            else:
                print('Skip failed')

    # show current song info
    def _info(self):
        printSongs([self.song.curSong], 0, 1)
        self.last_cmd = None

    # shot previous info
    def _prev_info(self):
        if self.song.prevSong != {}:
            printSongs([self.song.prevSong], 0, 1, "Use 'prev' to play")
            self.last_cmd = None
        else:
            print('Previous song: None')

    # play previous song
    def _prev(self):
        if self.song.prevSong != {}:
            self.song.prev_song()
            self.song.set_mixer(skip=True)
        else:
            print('Previous song: None')

    # stop
    def _exit(self):
        self.running = False

    # play all song in downloaded
    def _play_down(self):
        self.songs = readJson(JSON_DOWNLOADED_PATH)
        self.song.queue = self.songs[1:]
        self.playSong(self.songs[0])

    # show queue
    def _queue(self):
        if self.song.queue != []:
            writeSongQueue(self.song)
        else:
            print('Nothing in queue')

    # turn on shuffle queue song
    def _queue_shuffle(self):
        self.song.isShuffle = not self.song.isShuffle
        _a = (lambda x: 'ON' if x else 'OFF')
        print('Queue shuffle:', _a(self.song.isShuffle))

    # copy current song url to clipboard
    def _copy(self):
        if self.song.curSong != {}:
            copy(SHORT_URL + self.song.curSong['id'])
            print('Copied to clipboard')
        else:
            print('Nothing to copy')

    # delete song from downloaded
    def _delete(self, i):
        if len(i) == 1:
            print('Please add sID to delete')
            return
        if self.downs == []:
            print("Use 'downs|d' to get list downloaded")
            return
        
        self.song.isEdit = True
        # check input
        listSong = []
        # turn on edit
        # so thread will not check nextSong when remove curSong 
        # (error when repeat on)
        self.song.isEdit = True
        for sID in i[1:]:
            try:
                song = self.downs[int(sID)]
                # equal current song
                if (    self.song.curSong != {} 
                    and self.song.curSong['id'] == song['id']):
                        self.song.pause_song()
                        self.song.repeatTime = 0
                        self.song.mixer.unload()
                        self.song.curSong = {}
                # equal next song
                if (  self.song.nextSong != {} 
                    and self.song.nextSong['id'] == song['id']):
                        self.song.nextSong = {}
                # # equal previous song
                # if (  self.song.prevSong != {} 
                #     and self.song.prevSong['id'] == song['id']):
                #         self.song.prevSong = {}
                listSong.append(song)
            except:
                print('- Invalid sID:', sID)
        # remove
        deleteSongs(listSong)
        self.song.isEdit = False

    # repeat current song x time
    def _repeat(self, i):
        # repeat unlimit
        if len(i) == 1:
            self.song.repeatTime = -1
        else:
            self.song.repeatTime = int(i[1])
            self.song.nextSong = {}
        self.song.select_nextSong()
