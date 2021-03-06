from os import path
from pyperclip import copy
from re import search

from src.io import (
    readJson, 
    writeJson, 
    updateConfig, 
    deleteAll, 
    writeErrorLog, 
    deleteSongs,
    getFilesInFolder,
    createPlaylist,
    renamePlaylist,
    deleteFile,
    createImportPlaylist,
)
from src.config import (
    JSON_DOWNLOADED_PATH, 
    JSON_MCONFIG_PATH, 
    ERROR_PATH, CMD, 
    DOWN_FOLDER, 
    SONG_PER_LIST,
    SHORT_URL,
    BASE_URL,
    PLAYLIST_FOLDER,
    PLAYLIST_PARAM,
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
    printSongQueue,
    printAllPlaylist,
    printSongSimple,
    printUsage,
)
from src.audio import (
    downloadAudio, 
    downloadURL,
    getInfoYTPlaylist,
)
from src.utils import (
    str_similar, 
    is_valid_filename, 
    filename_from_path,
)
from src.scrapeYoutube import fetchQuery
from src import Song
from src.object.User import User

class Main():
    def __init__(self):
        self.user = User()
        self.song = Song()
        self.songs = []
        self.downs = []
        self.result = []
        self.listPlaylist = getFilesInFolder(PLAYLIST_FOLDER)
        self.playlist = {'path': None, 'songs': []}
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
            'songs':            (lambda x: self._songs(x[1:])),
            'downloaded':       (lambda x: self._downloaded(x[1:])),
            'search':           (lambda x: self._search(' '.join(x[1:]))),
            'play':             (lambda x: self._play(x[1:])),
            'volume':           (lambda x: self._volume(x[1:])),
            'help':             (lambda x: printHelp()),
            'next':             (lambda x: self._next()),
            'next_info':        (lambda x: self._next_info()),
            'skip':             (lambda x: self._skip(x[1:])),
            'info':             (lambda x: self._info()),
            'delete_all':       (lambda x: self._delete_all()),
            'previous_info':    (lambda x: self._prev_info()),
            'previous':         (lambda x: self._prev()),
            'play_downloaded':  (lambda x: self._play_down()),
            'queue':            (lambda x: self._queue()),
            'queue_add':        (lambda x: self._queue_add(x[1:])),
            'queue_remove':     (lambda x: self._queue_remove(x[1:])),
            'queue_shuffle':    (lambda x: self._queue_shuffle()),
            'copy':             (lambda x: self._copy()),
            'delete':           (lambda x: self._delete(x[1:])),
            'repeat':           (lambda x: self._repeat(x[1:])),
            'set_next':         (lambda x: self._set_next(x[1:])),
            'playlist':         (lambda x: self._playlist(x[1:])),
            'play_playlist':    (lambda x: self._play_playlist(x[1:])),
            'new_playlist':     (lambda x: self._new_playlist(x[1:])),
            'rename_playlist':  (lambda x: self._rename_playlist(x[1:])),
            'delete_playlist':  (lambda x: self._del_playlist(x[1:])),
            'playlist_add':     (lambda x: self._playlist_add(x[1:])),
            'playlist_remove':  (lambda x: self._playlist_remove(x[1:])),
            'playlist_info':    (lambda x: self._playlist_info()),
            'login':            (lambda x: self._login()),
            'import':           (lambda x: self._import()),
            'export':           (lambda x: self._export(x[1:])),
            'usage':            (lambda x: self._usage()),
        }   

    def playSong(self, songInput):
        '''

        Play song with songInput

        songInput: dict (much have {'id': x})

        '''
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

    def regexSongURL(self, string):
        '''Get expresion by check youtube video ID'''
        # if match YT link and youtube id video length == 1
        # or length input == 11
        flag = string.startswith((BASE_URL, SHORT_URL))
        lmd = (lambda x: len(x) == 11) # checking YT video ID
        ytID = string.replace(BASE_URL, '').replace(SHORT_URL, '')
        return [(flag and lmd(ytID)) or lmd(string), ytID]

    def isPlaylistURL(self, string):
        '''Check string is playlist url'''
        flag = string.startswith((BASE_URL))
        return flag and PLAYLIST_PARAM in string

    def get_play_cmd(self, sID=None):
        '''

        Play song based on last command used

        sID: int

        '''
        # if in ['songs', 'downs', 'search']
        # play song from that list
        play_cmd = {
            'sg': self.songs,
            'd': self.downs,
            's': self.result,
            'pl': self.playlist
        }
        if sID != None:
            return play_cmd[self.last_cmd][sID]
        # return all song in curren page
        return play_cmd[self.last_cmd]

    def select_playlist(self):
        '''Select playlist and show playlist infomation'''
        printAllPlaylist(
            [filename_from_path(x) for x in self.listPlaylist]
        )
        _input = input('Select playlist number: ').strip(' ').split(' ')
        if(len(_input) > 1):
            self._del_playlist([-1] + _input)
            return False
        try:
            _input = _input[0]
            self.playlist['path'] = self.listPlaylist[int(_input)]
            self.playlist['songs'] = readJson(self.listPlaylist[int(_input)])['songs']
            return True
        except:
            print('Invalid index')
            return False

    def input_range(self, input_):
        '''Check from input is a range number and return range(min, max)'''
        lst = input_.split('-')
        if len(lst) != 2:
            return None
        else:
            try:
                min_ = int(lst[0])
                max_ = int(lst[1])
                if min_ >= max_:
                    return None
                return range(min_, max_ + 1)
            except:
                return None

    def convert_int(self, input_, default=0):
        '''Convert string to int, if fasle use default number'''
        try:
            page = int(input_[0]) - 1
            if page < 0:
                return default
            return page
        except:
            return default

    def match_name_playlist(self, input_):
        '''

        Check input_ is a name of playlist
        If is a name, add playlist to self.playlist
        Else print playlist name similar

        '''
        # get all playlist name
        listPl = [filename_from_path(x) for x in self.listPlaylist]
         # when input name of playlist
        if input_ in listPl:
            index = listPl.index(input_)
            self.playlist['path'] = self.listPlaylist[index]
            self.playlist['songs'] = readJson(self.listPlaylist[index])['songs']
            return True
        else:
            listPl = [[x, str_similar(x, input_)] for x in listPl]
            listPl = [x for x in listPl if x[1] >= 0.5]
            print('Playlist not found')
            if len(listPl) > 0:
                print('Similar playlist: ')
                for f, r in listPl:
                    if r >= 0.5:
                        print('- ' + f)
        return False

    def _running(self):
        '''Main running function'''
        self.running = True
        while self.running:
            print()
            printMusicStatus(self.song)
            input_ = input('$ ').strip(' ').split(' ')
            try:
                # if input in array of CMD
                # use that key of CMD to active function in dict_cmd
                for key in CMD:
                    if input_[0] in CMD[key]:
                        self.dict_cmd[key](input_)
                        break
                else:
                    if input_[0] != '':
                        print('Command \'%s\' not found'%(input_[0]))
            except Exception as ex:
                writeErrorLog(ex, ' '.join(input_))

    def _delete_all(self):
        '''Delete all mp3, json'''
        print('Delete all file in json, cookie and audio/')
        # confirm delete
        confirm = input('Confirm (y/N): ')
        if confirm.lower().strip(' \t') not in ['y', 'yes']:
            return
        if self.song.mixer != None:
            self.song.mixer.unload()
            self.song.reset_all()
            self.musicThread = None
        pl = input('Do you want delete playlist (y/N): ')
        removePlaylist = pl.lower().strip(' \t') in ['yes', 'y']
        deleteAll(playlist=removePlaylist)

    def _clear(self):
        '''Clear screen'''
        clearScreen()
        self.last_cmd = None

    def _songs(self, input_):
        '''Show song recommended by YT'''
        page = self.convert_int(input_)
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
        # printSongs(self.songs, page, totalPage, '\n'.join(notes))
        printSongSimple(
            self.songs, 
            title='Songs Recommend', 
            note='\n'.join(notes),
            curPage=page + 1,
            maxPage=max(totalPage, 1)
        )
        # save last cmd 'songs'
        self.last_cmd = 'sg'

    def _downloaded(self, input_):
        '''Show downoaded song'''
        page = self.convert_int(input_)
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
        # printSongs(self.downs, page, int(m/SONG_PER_LIST) + 1, "Use 'play|p <sID>' to play")
        printSongSimple(
            self.downs, 
            title='Downloaded', 
            note="Use 'play|p <sID>' to play",
            curPage=page + 1,
            maxPage=max(int(m/SONG_PER_LIST) + 1, 1)
        )
        self.last_cmd = 'd'

    def _search(self, string):
        '''Search song from scrape youtube'''
        self.result = fetchQuery(string)[:SONG_PER_LIST]
        # printSongs(self.result, 0, 1, "Use 'play|p <sID>' to play")
        printSongSimple(
            self.result, 
            title='Search result', 
            note="Use 'play|p <sID>' to play",
            showView=True
        )
        self.last_cmd = 's'

    def _play(self, input_):
        '''

        Play song in songs/search/downloaded current page
        With 2 case
        + play: unpause
        + play <sID>: play song

        '''
        try:
            if len(input_) > 0:
                # try check is play sID or play URL
                sID = int(input_[0])
                if self.last_cmd != None:
                    # play sone from other will stop queue
                    if self.song.queue != []:
                        self.song.remove_queue()
                    self.playSong(self.get_play_cmd(sID))
            # if pause => unpause
            elif len(input_) == 0 and self.song.isPause:
                    self.song.unpause_song()
            else:
                print('Nothing to play')
        # play <url>: play with URL input
        except:
            flag, ytID = self.regexSongURL(input_[0])
            if flag:
                song = downloadURL(ytID)
                if song != {}:
                    self.playSong(song)
            else:
                print('URL invalid')

    def _volume(self, input_):
        '''Show current volume or change volume with input number'''
        # print volume level    
        if (len(input_) == 0):
            print("Volume:", 
                str(round(float(readJson(JSON_MCONFIG_PATH)['volume']) * 100, 2)) + '%')
        # change volume level
        else:
            try:
                updateConfig({'volume': float(input_[0]) / 100})
                if self.song.mixer != None:
                    self.song.mixer.set_volume(float(input_[0]) / 100)
                print('Volume changed')
            except:
                print('Invalid volume value')

    def _next(self):
        '''Play next song'''
        self.song.select_nextSong()
        self.song.next_song()
        self.song.set_mixer(skip=True)

    def _next_info(self):
        '''Show next song info'''
        self.song.select_nextSong()
        printSongs([self.song.nextSong], 0, 1, "Use 'next|n' to play")
        self.last_cmd = None

    def _skip(self, input_):
        '''Skip num seconds of the song'''
        if len(input_) == 0:
            second = input('Add total second want to skip: ')
        else:
            try:
                second = int(input_[0])
            except:
                print('Invalid number')
                return
        if (self.song.isPlaying or self.song.isPause):
            if self.song.is_skipable(second):
                self.song.skip_time(second)
            else:
                print('Skip failed')

    def _info(self):
        '''Show current song info'''
        printSongs([self.song.curSong], 0, 1)
        self.last_cmd = None

    def _prev_info(self):
        '''Show previous info'''
        if self.song.prevSong != {}:
            printSongs([self.song.prevSong], 0, 1, "Use 'prev' to play")
            self.last_cmd = None
        else:
            print('Previous song: None')

    def _prev(self):
        '''Play previous song'''
        if self.song.prevSong != {}:
            self.song.prev_song()
            self.song.set_mixer(skip=True)
        else:
            print('Previous song: None')

    def _exit(self):
        '''Exit'''
        self.running = False

    def _play_down(self):
        '''Play all song in downloaded'''
        self.songs = readJson(JSON_DOWNLOADED_PATH)
        self.song.queue = self.songs[1:]
        self.playSong(self.songs[0])
        self.song.curPlaylist = 'downloaded'

    def _queue(self):
        '''Show queue'''
        if self.song.queue != []:
            printSongQueue(self.song)
        else:
            print('Nothing in queue')

    def _queue_shuffle(self):
        '''Turn on shuffle queue song'''
        self.song.isShuffle = not self.song.isShuffle
        _a = (lambda x: 'ON' if x else 'OFF')
        print('Queue shuffle:', _a(self.song.isShuffle))

    def _copy(self):
        '''Copy current song url to clipboard'''
        if self.song.curSong != {}:
            copy(SHORT_URL + self.song.curSong['id'])
            print('Copied to clipboard')
        else:
            print('Nothing to copy')

    def _delete(self, input_):
        '''
        
        Delete song from downloaded
        
        input_: string (multiable)
            + Can be sID
            + Can be range (i.e. 1-3)

        '''
        if len(input_) == 0:
            print('Please add sID to delete')
            return
        if self.downs == []:
            self.downs = readJson(JSON_DOWNLOADED_PATH)
        
        self.song.isEdit = True
        # check input
        listSong = []
        # turn on edit
        # so thread will not check nextSong when remove curSong 
        # (error when repeat on)
        self.song.isEdit = True
        for value in input_:
            # when delete with sID
            try:
                song = self.downs[int(value)]
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
                print('Deleting: ', song['title'])
            except:
                #check input range
                if isinstance(value, str) and '-' in value:
                    range_ = self.input_range(value)
                    if range_ != None:
                        input_ += list(range_)
                        continue
                print('- Invalid value:', value)
        # remove
        deleteSongs(listSong)
        self.song.isEdit = False

    def _repeat(self, input_):
        '''

        Repeat current song x time

        input_: int (nullable)
            + If null: repeat forever
            + If null and not set repeat => remove repeat
            + If have x time: set repeat x time

        '''
        # repeat song
        if self.song.repeatTime == 0:
            # repeat unlimit
            if len(input_) == 0:
                self.song.repeatTime = -1
            else:
                try:
                    self.song.repeatTime = int(input_[0])
                    self.song.nextSong = {}
                except:
                    print('Invalid number')
        # un-repeat song
        else:
            self.song.repeatTime = 0
            self.song.nextSong = {}
        self.song.select_nextSong()

    def _set_next(self, input_):
        '''

        Set next song

        input_: string
            + If sID: set next song from list
            + If url or video ID: fetch song and set next song

        '''
        if self.last_cmd != None and len(input_) > 0:
            try:
                self.song.nextSong = self.get_play_cmd(int(input_[0]))
                self.song.nextSong['unchange'] = True
                print('Set next song success')
                # if set next when have a queue, remove queue
                if self.song.queue != []:
                    self.song.remove_queue()
            except:
                print('Invalid  sID')
        else:
            print('Nothing to set next')
    
    def _queue_add(self, input_):
        '''

        Add song to queue

        input_: string (multiable)
            + If sID: add song from list with sID to queue
            + If range: add song from list with range (i.e 1-4) to queue
            + If url|song Id: fetch song from url and add to queue

        '''
        # add all song in current page
        if len(input_) == 0:
            if self.last_cmd != None:
                self.song.queue = self.song.queue + self.get_play_cmd()
                print('Added all song in current page to queue')
            else:
                print('Nothing to add')
        else:
            # add multi song
            for value in input_:
                try:
                    if self.last_cmd != None:
                        song = self.get_play_cmd(int(value))
                        if song not in self.song.queue:
                            self.song.queue.append(song)
                            print('sID %s added to queue'%(value))
                    else:
                        raise Exception()
                # play <url>: play with URL input
                except:
                    # check is url?
                    flag, ytID = self.regexSongURL(value)
                    if flag:
                        song = downloadURL(ytID)
                        if song != {}:
                            self.song.queue.append(song)
                            print('Song %s added to queue'%(ytID))
                            continue
                    # input is youtube playlist url
                    if self.isPlaylistURL(value):
                        print('Found Youtube playlist link:', value)
                        print('Get songs in playlist')
                        start = input('Set start song (default 1): ')
                        end = input('Set total song (default 20): ')
                        # get songs in playlist
                        songs = getInfoYTPlaylist(
                            value, 
                            self.convert_int(start, 1), 
                            self.convert_int(end, 20)
                        )
                        print('Total song in YT playlist:', len(songs))
                        # add song to queue
                        self.song.queue += songs
                        continue
                    # check input range
                    if isinstance(value, str) and '-' in value and len(value) <= 5:
                        range_ = self.input_range(value)
                        if range_ != None:
                            input_ += list(range_)
                            continue
                    print('Invalid value:', value)
        # song not play, play it
        if self.musicThread == None and self.song.queue != []:
            self.playSong(self.song.queue.pop(0))
    
    def _queue_remove(self, input_):
        '''

        Remove song in queue

        input_: null => remove all song in queue
        input_: string (multiable)
            + If sID: remove song in queue with sID
            + If range: remove songs in range (i.e. 1-5)

        '''
        # remove 1 song
        if len(input_) > 0:
            listsID = []
            for sID in input_:
                try:
                    listsID.append(int(sID))
                except:
                    # check input range
                    if '-' in sID:
                        range_ = self.input_range(sID)
                        if range_ != None:
                            input_ += list(range_)
                            continue
                    print('Invalid value:', sID)
            # remove duplicate, and remove
            for pos in list(dict.fromkeys(listsID)).sort(reverse=True):
                if len(self.song.queue) >= pos and pos >= 1:
                    self.song.queue.pop(pos)
                    print('Song %s removed'%(pos))
        # remove queue
        else:
            self.song.remove_queue()
            print('Queue removed')
    
    def _playlist(self, input_):
        '''

        Show all playlist, select playlist

        input_: string
            + If playlist index: show songs in playlist at index
            + If playlist name: 
                + Correct: show songs in playlist with name
                + Incorrect: show name suggestion and re-input

        '''
        # show all playlist
        self.listPlaylist = getFilesInFolder(PLAYLIST_FOLDER)
        if len(input_) == 0:
            printAllPlaylist(
                [filename_from_path(x) for x in self.listPlaylist]
            )
        # select playlist
        else:
            try:
                self.playlist['path'] = self.listPlaylist[int(input_[0])]
                self.playlist['songs'] = readJson(self.listPlaylist[int(input_[0])])['songs']
            except:
                # check input name of playlist 'self.match_name_playlist(str)'
                # if not get suggest name
                if not self.match_name_playlist(input_[0]):
                    return
            self.last_cmd = 'pl'
            self._playlist_info()

    def _play_playlist(self, input_):
        '''

        Play playlist

        input_: string
            + If playlist index: play playlist at index
            + If playlist name:
                + Correct: play playlist
                + Incorrect: show name suggestion

        '''
        # play current selected playlist
        if len(input_) == 0 and self.playlist['path'] == '':
            print('Please select playlist')
            return
        # play playlist with input
        elif len(input_) > 0:
            try:
                self.playlist['songs'] = readJson(self.listPlaylist[int(input_[0])])['songs']
                self.playlist['path'] = self.listPlaylist[int(input_[0])]
            except:
                if not self.match_name_playlist(input_[0]):
                    return
        #
        if self.playlist['songs'] == []:
            print('Nothing to play')
            return
        self.song.curPlaylist = self.playlist['path']
        self.song.queue = self.playlist['songs']
        print('Playing playlist', filename_from_path(self.playlist['path']))

        # song not play, play it
        if self.musicThread == None and self.song.queue != []:
            self.playSong(self.song.queue.pop(0))
        else:
            self._next()

    def _new_playlist(self, input_):
        '''

        Create new empty playlist

        input_: null => Get playlist name
        input_: string (name playlist)

        '''
        if len(input_) == 0:
            name = input("Input name new playlist ('.c' to cancel): ")
            if name == '.c':
                return
        else:
            name = input_[0]

        if not is_valid_filename(name):
            print('Invalid name')
            return
        
        if createPlaylist(name):
            print('Created playlist '+ name)
        else:
            print('Failed create playlist')

    def _rename_playlist(self, input_):
        '''

        Rename playlist
        If non-playlist selected => Error
        
        input_: null => Get new name
        input_: string

        Check name valid => Rename

        '''
        if self.playlist['path'] == None:
            print('Please select playlist')
            return

        if len(input_) == 0:
            print('Rename playlist ', filename_from_path(self.playlist['path']))
            new_name = input("Input new name ('.c' to cancle): ")
        else:
            new_name = input_[0]

        if not is_valid_filename(new_name) or new_name == '.c':
            print('Invalid name')
            return

        r = renamePlaylist(self.playlist['path'], new_name)
        if isinstance(r, str):
            self.playlist['path'] = r
            printSongSimple(
                self.playlist['songs'],
                'Playlist: '+ filename_from_path(self.playlist['path'])
            )
            print('Rename successful')
        else:
            print('Rename failed')

    def _del_playlist(self, input_):
        '''

        Delete playlist

        input_: string (multiable)
            + Playlist index
            + Playlist name

        '''
        # delete multi-playlist
        if len(input_) > 0:
            for index in input_:
                try:
                    _name = filename_from_path(self.listPlaylist[int(index)])
                    deleteFile(self.listPlaylist[int(index)])
                    print('Deleted '+ _name)
                except:
                    listPl = [filename_from_path(x) for x in self.listPlaylist]
                    # when input name of playlist
                    if input_ in listPl:
                        index = listPl.index(input_)
                        deleteFile(self.listPlaylist[index])
                    else:
                        print('Invalid value: ' + index)
            return
        # not selected playlist and input only delpl|dpl
        # delete current playlist
        if self.playlist['path'] == None:
            if not self.select_playlist():
                return
            
        deleteFile(self.playlist['path'])
        self.playlist = {'path': None, 'songs': []}
        print('Deleted')
            
    def _playlist_add(self, input_):
        '''

        Add song to playlist

        input_: string
            + sID
            + url|song ID
            + range (i.e. 1-3)

        '''
        if self.playlist['path'] == None:
            if not self.select_playlist():
                return
        
        isChanged = False
        songAdd = []
        # add current song
        if len(input_) == 0:
            songAdd.append(self.song.curSong)
        # input multi-song
        else:
            for value in input_:
                # when input is 1-3
                # get song index 1, 2, 3
                if '-' in value and len(value) <= 5:
                    range_ = self.input_range(value)
                    if range_ == None:
                        print('Invalid range: ' + value )
                        continue
                    # get song will be add
                    else:
                        songAdd += [self.get_play_cmd(x) for x in range_]
                # when input index
                # get song from index current cmd
                try:
                    songAdd.append(self.get_play_cmd(int(value)))
                # get song from Youtube URL/ID
                except:
                    # flag is valid url/video id
                    flag, ytID = self.regexSongURL(value)
                    song = {}
                    if flag:
                        song = downloadURL(ytID)
                    # check playlist url
                    else:
                        if self.isPlaylistURL(value):
                            print('Found Youtube playlist link:', value)
                            print('Get songs in playlist')
                            start = input('Set start song (default 1): ')
                            end = input('Set total song (default 20): ')
                            # get songs in playlist
                            song = getInfoYTPlaylist(
                                value, 
                                self.convert_int(start, 1), 
                                self.convert_int(end, 20)
                            )
                            flag = True
                            print('Total song in YT playlist:', len(song))

                    if song == {} or not flag:
                        print('Invalid value: '+ value)
                        continue
                    # song is dict = 1 song
                    if isinstance(song, dict):
                        songAdd.append(song)
                    # song is list = many song from youtube palylist
                    elif isinstance(song, list):
                        for s in song:
                            songAdd.append(s)

        print('Add song to playlist:', filename_from_path(self.playlist['path']))
        for song in songAdd:
            # check song not in playlist
            if (len([x for x in self.playlist['songs'] 
                    if x['id'] == song['id']])
                == 0): 
                    self.playlist['songs'].append(song)
                    self.song.add_song_playlist_queue(
                        self.playlist['path'],
                        song
                    )
                    isChanged = True
                    print('+ Added '+ song['title'])
            # song already in playlist
            else:
                print('- Song %s already in playlist %s'
                    %(song['title'], 
                        filename_from_path(self.playlist['path'])))

        if isChanged:
            data = readJson(self.playlist['path'])
            data['songs'] = self.playlist['songs']
            writeJson(data, self.playlist['path'])

    def _playlist_remove(self, input_):
        '''

        Remove song in playlist

        input_: string
            + sID
            + range (i.e. 1-3)
            + 'all': remove all song in playlist

        '''
        if self.playlist['path'] == None:
            if not self.select_playlist():
                return 

        if len(input_) == 0:
            print('Please add index song to remove')
            return

        isChanged = False
        if input_[0] == 'all':
            self.playlist['songs'] = []
            isChanged = True
        else:
            songRemove = []
            for value in input_:
                try:
                    # when input is 1-3
                    # get song index 1, 2, 3
                    if isinstance(value, str) and '-' in value:
                        range_ = self.input_range(value)
                        if range_ == None:
                            print('Invalid range: ' + value )
                            continue
                        else:
                            # get song will be remove
                            songRemove += [self.playlist['songs'][x] for x in range_]
                    # when input index
                    else:
                        songRemove += [self.playlist['songs'][int(value)]]
                except:
                    print('Invalid index: ' + value)
            # remove song
            for song in songRemove:
                if song in self.playlist['songs']:
                    self.playlist['songs'].remove(song)
                    print('Removed: '+ song['title'])
                    isChanged = True
        if isChanged:
            data = readJson(self.playlist['path'])
            data['songs'] = self.playlist['songs']
            writeJson(data, self.playlist['path'])

    def _playlist_info(self):
        '''Show all song in playlist'''
        self.playlist['songs'] = readJson(self.playlist['path'])['songs']
        notes = []
        notes.append("Use 'ppl' to play playlist")
        notes.append("Use 'plr <sID>' to remove song")
        printSongSimple(
            self.playlist['songs'], 
            title='Playlist: ' + filename_from_path(self.playlist['path']),
            note="\n".join(notes)
        )
        
    def _login(self):
        '''Change username and password'''
        self.user.login_()

    def _import(self):
        '''Import playlist from username'''
        result = self.user.import_()
        if isinstance(result, dict):
            createImportPlaylist(result['playlists'])
        else:
            print(result)
            # reset when invalid username/password
            if 'Invalid' in result:
                self.user.reset_all()
    
    def _export(self, input_):
        '''Export playlist to usename'''
        exportPL = []
        # export current playlist
        if len(input_) == 0:
            if self.playlist['path'] == None and not self.select_playlist():
                return
            exportPL.append(readJson(self.playlist['path']))
        else:
            self.listPlaylist = getFilesInFolder(PLAYLIST_FOLDER)
            # export all
            if 'all' in input_:
                for pl in self.listPlaylist:
                    exportPL.append(readJson(pl))
            else:
                indexPL = []
                filename = [filename_from_path(x) for x in self.listPlaylist]
                for value in input_:
                    try:
                        indexPL.append(int(value))
                    except:
                        # when input playlist name
                        if value in filename:
                            indexPL += [filename.index(value)]
                            continue
                        # when input range
                        if '-' in value and len(value) <= 5:
                            range_ = self.input_range(value)
                            if range_ == None:
                                print('Invalid range: ' + value )
                                continue
                            # get song will be add
                            else:
                                indexPL += range_
                                continue
                        print('Invalid value:', value)

                for i in list(dict.fromkeys(indexPL)):
                    exportPL.append(readJson(self.listPlaylist[i]))

        result = self.user.export_(exportPL)
        print(result)
        # reset when invalid username/password
        if 'Invalid' in result:
            self.user.reset_all()

    def _usage(self):
        '''Print some useage'''
        printUsage()