import threading
# ------------------------------------------------------------------------------
from src.ScrapeYoutube import singleSong
from src.audio import downloadAudio, playSound
from src.IO import writeFetchJson
from src.config import BASE_URL
# ------------------------------------------------------------------------------
def newThread():
    return threading.Thread()

def download(song):
    d = threading.Thread(target=downloadAudio, args=({'url': song},))
    d.start()

def fetchSong(url):
    f = threading.Thread(target=writeFetchJson, args=(singleSong(BASE_URL+url),))
    f.start()

def thrSong(songInput, song):
    return threading.Thread(target=playSound, args=(songInput['url'], song))