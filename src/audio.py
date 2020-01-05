from youtube_dl import YoutubeDL
from os import path, remove
from pygame import mixer # audio player
from time import sleep
import traceback
# ------------------------------------------------------------------------------
from src.config import (
    DOWN_FOLDER, 
    BASE_URL,
    ydl_opts,
)
from src.io import (
    writeDownloaded, 
    writeErrorLog,
)
from src.utils import (
    getSongId,
)
# ------------------------------------------------------------------------------
def sendClickedSong(song):
    with YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(BASE_URL + song['url'], False)

def downloadAudio(song):
    try:
        # check exists mp3
        if 'path' in song and path.exists(song['path']):
            # try send cookie when listen to this song
            # does YT recommend effect ?
            from threading import Thread
            thr = Thread(target=sendClickedSong, args=(song,))
            thr.daemon = True
            thr.start()

            return 'mp3 exist'

        songId = getSongId(song['url'])
        mp4 = DOWN_FOLDER + song['title'] +'-'+ songId + '.mp4'
        # check exists mp4 => delete
        if path.exists(mp4):
            remove(mp4)

        # download mp4
        print('\nDownloading: ' + song['title'], end='')
        with YoutubeDL(ydl_opts) as ydl:
            t = ydl.extract_info(BASE_URL + song['url'], True)

            # info = {
            #     'id': t['id'],
            #     'channel': t['uploader'],
            #     'title': t['title'],
            #     'categories': t['categories'],
            #     'url': t['webpage_url'],
            #     'views': t['view_count'],
            #     'time': formatSeconds(t['duration'])
            # }

            # get file name generate by ydl
            name = '.'.join(ydl.prepare_filename(t).split('.')[:-1])
            song['path'] = name + '.mp3'
        # remove status when fisnish download
        if 'downloading' in song:
            song.pop('downloading')
        # write to download
        writeDownloaded(song)
        # pre-print '$ ' after auto downoad (lazy way)
        if 'path' in song:
            print('\n$ ', end='')
    except Exception as ex:
        writeErrorLog(ex)

def playSound(song):
    # create
    mixer.init()
    song.mixer = mixer.music
    # set default music
    song.set_mixer()
    # start loop play event
    song.isPlaying = True
    try:
        while song.isPlaying:
            while song.mixer != None and song.mixer.get_busy():
                song.down_next_song()
                sleep(2)
            # when play finished change status, and play next song
            # add check surSong != {} to prevent when 'delete-all'
            if song.curSong != {} and not song.isPause and not song.isEdit:
                song.finish_song()
                song.next_song()
                song.set_mixer()
            sleep(1)
    except Exception as ex:
        writeErrorLog(ex)
        
