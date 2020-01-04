from threading import Thread
# ------------------------------------------------------------------------------
from src.scrapeYoutube import singleSong
from src.audio import downloadAudio, playSound
from src.io import writeJson, writeNext
from src.config import BASE_URL, JSON_NAME_PATH
# ------------------------------------------------------------------------------
# set daemon = True so when Ctrl+C it will kill all thread
def newThread():
    return Thread()

def thrWriteJson(data, path):
    d = Thread(target=writeJson, args=(data, path,))
    d.daemon = True
    d.start()

def thrWriteNext(string, path):
    d = Thread(target=writeNext, args=(string, path,))
    d.daemon = True
    d.start()

def thrDownload(url):
    d = Thread(target=downloadAudio, args=(url,))
    d.daemon = True
    d.start()

def thrFetchSong(url):
    # f = Thread(target=writeJson, args=(singleSong(BASE_URL + url,), JSON_NAME_PATH,))
    # change function so thread don't need to wait result of singSong to execute writeJson
    f = Thread(target=singleSong, args=(BASE_URL + url, True,),) 
    f.daemon = True
    f.start()

def thrSong(song):
    return Thread(target=playSound, args=(song,))