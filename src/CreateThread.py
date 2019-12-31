import threading
# ------------------------------------------------------------------------------
from src.ScrapeYoutube import singleSong
from src.audio import downloadAudio, playSound
from src.IO import writeJson
from src.config import BASE_URL, JSON_NAME_PATH
# ------------------------------------------------------------------------------
def newThread():
    return threading.Thread()

def thrWriteJson(data, path):
    d = threading.Thread(target=writeJson, args=(data, path,))
    d.start()

def download(song):
    d = threading.Thread(target=downloadAudio, args=({'url': song},))
    d.start()

def fetchSong(url):
    f = threading.Thread(target=writeJson, args=(singleSong(BASE_URL+url,), JSON_NAME_PATH,))
    f.start()

def thrSong(songInput, song):
    return threading.Thread(target=playSound, args=(songInput['url'], song))