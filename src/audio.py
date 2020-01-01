import youtube_dl, os, time, threading
from datetime import datetime
from pygame import mixer # audio player
# ------------------------------------------------------------------------------
from src.config import JSON_DOWNLOADED_PATH, ERROR_PATH
from src.config import DOWN_FOLDER, BASE_URL, ydl_opts
from src.utils import getSongId
from src.IO import writeDownloaded, readJson, writeNext
# ------------------------------------------------------------------------------

def downloadAudio(song):
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
        print('$ ', end='')

    return 'done'

def playSound(song):
    # create
    mixer.init()
    song.mixer = mixer.music
    # set default music
    song.set_mixer()
    # start loop play event
    song.playing = True
    try:
        while song.playing:
            # add time played
            while song.mixer.get_busy():
                    time.sleep(1)
                    song.down_next_song()
            # when play finished change status, and play next song
            if not song.pause and not song.edit:
                song.finish_song()
                song.next_song()
                song.set_mixer()
    except Exception as ex:
        # write error to file
        lines = []
        lines.append('Time: ' + datetime.now().__str__())
        lines.append('Func: playSound')
        lines.append('Error: ' + str(ex) + '\n')
        writeNext('\n'.join(lines), ERROR_PATH)
