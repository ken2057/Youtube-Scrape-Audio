from youtube_dl import YoutubeDL
from os import path, remove
from pygame import mixer # audio player
from time import sleep
import traceback
# ------------------------------------------------------------------------------
from src.formatPrint import changeTitle
from src.config import (
    DOWN_FOLDER,
    ydl_opts,
)
from src.io import (
    writeDownloaded, 
    writeErrorLog,
    getInDownloaded,
)
from src.utils import (
    getSongId,
    formatSeconds
)
# ------------------------------------------------------------------------------
def sendClickedSong(song):
    with YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(song['id'], False)

def songInfoFormat(song, fileName):
    path = '.'.join(fileName.split('.')[:-1])
    return {
        'id': song['id'], 
        'channel': song['uploader'], 
        'title': song['title'], 
        'views': song['view_count'], 
        'time': formatSeconds(song['duration']), 
        'path': path + '.mp3'
    }


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
            t = ydl.extract_info(song['id'], True)
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

def downloadURL(ytID):
    try:
        song = getInDownloaded({'id': ytID})
        if 'path' not in song:
            print('\nDownloading '+ytID, end='')
            with YoutubeDL(ydl_opts) as ydl:
                t = ydl.extract_info(ytID, True)
                # write to download
                writeDownloaded(songInfoFormat(t, ydl.prepare_filename(t)))
        return song
    except Exception as ex:
        writeErrorLog(ex)
        return {}

def getInfoYTPlaylist(url, start=1, end=20):
    try:
        ydl_opts['playliststart'] = start
        ydl_opts['playlistend'] = end
        ydl_opts.pop('noplaylist')
        print('Getting songs in playlist')
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, False)
            songs = []
            for song in info['entries']:
                songs.append(songInfoFormat(song, ydl.prepare_filename(song)))
            return songs

    except Exception as ex:
        writeErrorLog(ex)
        return []

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
                    # changeTitle(formatSeconds(song.time))
                    changeTitle(song.__str__())
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

