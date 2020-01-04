import threading
# ------------------------------------------------------------------------------
from src.scrapeYoutube import singleSong
from src.audio import downloadAudio, playSound
from src.io import writeJson, writeNext
from src.config import BASE_URL, JSON_NAME_PATH
# ------------------------------------------------------------------------------
# set daemon = True so when Ctrl+C it will kill all thread
def newThread():
    return threading.Thread()

def thrWriteJson(data, path):
    d = threading.Thread(target=writeJson, args=(data, path,))
    d.daemon = True
    d.start()

def thrWriteNext(string, path):
    d = threading.Thread(target=writeNext, args=(string, path,))
    d.daemon = True
    d.start()

def thrDownload(url):
    d = threading.Thread(target=downloadAudio, args=(url,))
    d.daemon = True
    d.start()

def thrFetchSong(url):
    # f = threading.Thread(target=writeJson, args=(singleSong(BASE_URL + url,), JSON_NAME_PATH,))
    # change function so thread don't need to wait result of singSong to execute writeJson
    f = threading.Thread(target=singleSong, args=(BASE_URL + url, True,),) 
    f.daemon = True
    f.start()

def thrSong(song):
    return threading.Thread(target=playSound, args=(song,))