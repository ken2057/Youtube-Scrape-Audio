import youtube_dl, os
from time import sleep
from pygame import mixer # audio player
# ------------------------------------------------------------------------------
from src.config import DOWN_FOLDER, BASE_URL, ydl_opts
from src.IO import writeDownloaded, writeErrorLog
from src.utils import getSongId
# ------------------------------------------------------------------------------

def downloadAudio(song):
    try:
        songId = getSongId(song['url'])
        mp3 = DOWN_FOLDER + '/' + songId + '.mp3'
        mp4 = DOWN_FOLDER + '/' + songId + '.mp4'
        # check exists mp3
        if os.path.exists(mp3):
            return 'mp3 exist'
        # check exists mp4 => delete
        if os.path.exists(mp4):
            os.remove(mp4)

        ydl_opts['outtmpl'] = mp4
        # download mp4
        print('\nDownloading:', song['title'])
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([BASE_URL + song['url']])

        writeDownloaded(song)
        # pre-print '$ ' after auto downoad (lazy way)
        if 'downloaded' in song:
            print('\n$ ', end='')
    except Exception as ex:
        writeErrorLog(str(ex), 'audio.downloaodAudio')

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
            while song.mixer.get_busy():
                song.down_next_song()
                sleep(2)
            # when play finished change status, and play next song
            if not song.isPause and not song.isEdit:
                song.finish_song()
                song.next_song()
                song.set_mixer()
            sleep(1)
    except Exception as ex:
        writeErrorLog(str(ex), 'audio.playSound')
