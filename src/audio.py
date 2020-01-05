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
    getInDownloaded,
)
from src.utils import (
    getSongId,
)
# ------------------------------------------------------------------------------
def sendClickedSong(song):
    with YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(BASE_URL + song['id'], False)

def downloadAudio(song):
    try:
        # check exists mp3
        song = getInDownloaded(song)
        if 'path' in song and path.exists(song['path']):
            # try send cookie when listen to this song
            # does YT recommend effect ?
            from threading import Thread
            thr = Thread(target=sendClickedSong, args=(song,))
            thr.daemon = True
            thr.start()
            return song

        mp4 = DOWN_FOLDER + song['title'] +'-'+ song['id'] + '.mp4'
        # check exists mp4 => delete
        if path.exists(mp4):
            remove(mp4)

        # download mp4
        print('\nDownloading: ' + song['title'], end='')
        with YoutubeDL(ydl_opts) as ydl:
            t = ydl.extract_info(BASE_URL + song['id'], True)

            # info = {
            #     'id': t['id'],
            #     'channel': t['uploader'],
            #     'title': t['title'],
            #     'categories': t['categories'],
            #     'id': t['webpage_url'],
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
    except Exception as ex:
        writeErrorLog(ex)
    return song

def playSound(song):
    # create
    mixer.init()
    song.mixer = mixer.music
    # set default music
    song.set_mixer()
    # start loop play event
    song.isPlaying = True
    try:
        while song.isPlaying or song.isPause:
            # mixer != None: now throw error when play new song
            # get_busy: check is runing
            # isPause: get_busy alway return 1 so can't use for song.time+=1
            if (not song.isPause
                and song.mixer != None
                and song.mixer.get_busy()):
                    song.time += 1
                    song.down_next_song()
            # when play finished change status, and play next song
            # add check surSong != {} to prevent when 'delete-all'
            elif (not song.isEdit
                and song.curSong != {} 
                and not song.isPause):
                    song.finish_song()
                    song.next_song()
                    song.set_mixer()
            sleep(1) # reduce cpu usage and add time
    except Exception as ex:
        writeErrorLog(ex)
        
