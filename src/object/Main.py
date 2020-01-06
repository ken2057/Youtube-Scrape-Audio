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
)
from src.audio import (
    downloadAudio, 
    downloadURL,
)
from src.utils import (
    str_similar, 
    is_valid_filename, 
    filename_from_path,
)
from src.scrapeYoutube import fetchQuery
from src import Song

class Main():
    def __init__(self):
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
            'playlist_info':    (lambda x: self._playlist_info())
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

    def regexURL(self, string):
        # if match YT link and youtube id video length == 1
        # or length input == 11
        flag1 = string.startswith((BASE_URL, SHORT_URL))
        lmd = (lambda x: len(x) == 11) # checking YT video ID
        ytID = string.replace(BASE_URL, '').replace(SHORT_URL, '')
        return [(flag1 and lmd(ytID)) or lmd(string), ytID]

    def get_play_cmd(self, sID=None):
        # check last command used
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
            self.playlist['songs'] = readJson(self.listPlaylist[int(_input)])
            return True
        except:
            print('Invalid index')
            return False

    def input_range(self, input_):
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

    def get_page(self, input_):
        try:
            page = int(input_[0]) - 1
        except:
            page = 0
        return page

    # this function will check input_ is a name of playlist
    # if is a name, add playlist to self.playlist
    # else print playlist name similar
    def match_name_playlist(self, input_):
        # get all playlist name
        listPl = [filename_from_path(x) for x in self.listPlaylist]
         # when input name of playlist
        if input_ in listPl:
            index = listPl.index(input_)
            self.playlist['path'] = self.listPlaylist[index]
            self.playlist['songs'] = readJson(self.listPlaylist[index])
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

    # Call this function to run
    def _running(self):
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

    # delete all mp3, json
    def _delete_all(self):
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
        clearScreen()
        self.last_cmd = None

    # show song recommended by YT
    def _songs(self, input_):
        page = self.get_page(input_)
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

    # show downoaded song
    def _downloaded(self, input_):
        page = self.get_page(input_)
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
            maxPage=max(int(m/SONG_PER_LIST), 1)
        )
        self.last_cmd = 'd'

    # search song from scrape youtube
    def _search(self, string):
        self.result = fetchQuery(string)[:SONG_PER_LIST]
        # printSongs(self.result, 0, 1, "Use 'play|p <sID>' to play")
        printSongSimple(
            self.result, 
            title='Search result', 
            note="Use 'play|p <sID>' to play",
            showView=True
        )
        self.last_cmd = 's'

    # play song in songs/search/downloaded current page
    def _play(self, input_):
        # first case 
        # play: unpause
        # play <sID>: play song
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
            flag, ytID = self.regexURL(input_[0])
            if flag:
                song = downloadURL(ytID)
                if song != {}:
                    self.playSong(song)
            else:
                print('URL invalid')

    # show current volume
    # change volume with num
    def _volume(self, input_):
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
    def _skip(self, input_):
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
        self.song.curPlaylist = 'downloaded'

    # show queue
    def _queue(self):
        if self.song.queue != []:
            printSongQueue(self.song)
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
    def _delete(self, input_):
        if len(input_) == 0:
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
        for sID in input_:
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
    def _repeat(self, input_):
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

    # set next song
    def _set_next(self, input_):
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
    
    # add song to queue
    def _queue_add(self, input_):
        # add all song in current page
        if len(input_) == 0:
            if self.last_cmd != None:
                self.song.queue = self.song.queue + self.get_play_cmd()
                print('Added all song in current page to queue')
            else:
                print('Nothing to add')
        else:
            # add multi song
            for sID in input_[1:]:
                try:
                    if self.last_cmd != None:
                        self.song.queue.append(self.get_play_cmd(int(sID)))
                        print('sID %s added to queue'%(sID))
                # play <url>: play with URL input
                except:
                    flag, ytID = self.regexURL(sID)
                    if flag:
                        song = downloadURL(ytID)
                        if song != {}:
                            self.song.queue.append(song)
                            print('Song %s added to queue'%(ytID))
                    else:
                        print('URL invalid: '+sID)
        # song not play, play it
        if self.musicThread == None and self.song.queue != []:
            self.playSong(self.song.queue[0])
            self.song.queue = self.song.queue[1:]
    
    # remove song in queue
    def _queue_remove(self, input_):
        # remove 1 song
        if len(input_) > 0:
            for sID in input_:
                try:
                    sID = int(sID)
                    if len(self.song.queue) >= sID and sID >= 1:
                        self.song.queue.pop(sID)
                        print('Song %s removed'%(sID))
                except:
                    print('Invalid '+sID)
        # remove queue
        else:
            self.song.remove_queue()
            print('Queue removed')
    
    # show all playlist, select playlist
    def _playlist(self, input_):
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
                self.playlist['songs'] = readJson(self.listPlaylist[int(input_[0])])
            except:
                # check input name of playlist 'self.match_name_playlist(str)'
                # if not get suggest name
                if not self.match_name_playlist(input_[0]):
                    return
            self.last_cmd = 'pl'
            self._playlist_info()

    # play playlist
    def _play_playlist(self, input_):
        # play current selected playlist
        if len(input_) == 0 and self.playlist['path'] == '':
            print('Please select playlist')
            return
        # play playlist 
        else:
            try:
                self.playlist['songs'] = readJson(self.listPlaylist[int(input_[0])])
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
            self.playSong(self.song.queue[0])
            self.song.queue = self.song.queue[1:]

    # create new empty playlist
    def _new_playlist(self, input_):
        if len(input_) == 0:
            name = input('Input name new playlist: ')
        else:
            name = input_[0]

        if not is_valid_filename(name):
            print('Invalid name')
            return
        
        if createPlaylist(name):
            print('Created playlist '+ name)
        else:
            print('Failed create playlist')

    # rename playlist
    def _rename_playlist(self, input_):
        if self.playlist['path'] == None:
            print('Please select playlist')
            return

        if len(input_) == 0:
            print('Rename playlist ', filename_from_path(self.playlist['path']))
            new_name = input("Input new name (type '.c' to cancle): ")
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

    # delete song in playlist
    def _del_playlist(self, input_):
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
            
    # add song to playlist
    def _playlist_add(self, input_):
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
                if '-' in value:
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
                    flag, ytID = self.regexURL(value)
                    song = {}
                    if flag:
                        song = downloadURL(ytID)
                    if song == {} or not flag:
                        print('Invalid value: '+ value)
                        continue
                    songAdd.append(song)

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
                    print('Added '+ song['title'])
            # song already in playlist
            else:
                print('Song %s already in playlist %s'
                    %(song['title'], 
                        filename_from_path(self.playlist['path'])))

        if isChanged:
            writeJson(self.playlist['songs'], self.playlist['path'])

    # remove song in playlist
    def _playlist_remove(self, input_):
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
                    if '-' in value:
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
            writeJson(self.playlist['songs'], self.playlist['path'])

    def _playlist_info(self):
        self.playlist['songs'] = readJson(self.playlist['path'])
        notes = []
        notes.append("Use 'ppl' to play playlist")
        notes.append("Use 'plr <sID>' to remove song")
        printSongSimple(
            self.playlist['songs'], 
            title='Playlist: ' + filename_from_path(self.playlist['path']),
            note="\n".join(notes)
        )
        