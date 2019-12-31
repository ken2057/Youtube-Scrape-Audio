import youtube_dl, os
from pygame import mixer # audio player
# ------------------------------------------------------------------------------
from src.config import DOWN_FOLDER, BASE_URL, ydl_opts, DEFAULT_VOLUME
from src.config import JSON_MCONFIG_PATH, JSON_DOWNLOADED_PATH
from src.IO import writeDownloaded, readJson
# ------------------------------------------------------------------------------
# http://builds.libav.org/windows/release-gpl/
# https://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/
# https://ffmpeg.zeranoe.com/builds/

def getSongId(url):
    return url.replace('/watch?v=', '')

def downloadAudio(song):
    songId = getSongId(song['url'])
    # check exists mp3
    mp3 = DOWN_FOLDER + '/' + songId + '.mp3'
    mp4 = DOWN_FOLDER + '/' + songId + '.mp4'
    if os.path.exists(mp3):
        return 'mp3 exist'
    if not os.path.exists(mp4):
        ydl_opts['outtmpl'] = mp4
        # download mp4
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([BASE_URL + song['url']])

    writeDownloaded(song)
    return 'done'

def playSound(songId, song):
    mixer.init()
    song.mixer = mixer.music
    song.mixer.load(DOWN_FOLDER+ '/' + getSongId(songId) +  '.mp3')
    song.mixer.set_volume(readJson(JSON_MCONFIG_PATH)['volume'])
    song.mixer.play()

    song.playing = True
    while song.pause and not song.stop:
        # play sound
        while song.mixer.get_busy():
            continue

class Song():
    pause = False
    stop = False
    playing = False
    mixer = None
    title = 'None'

    def __intit__(self):
        pass
    
    