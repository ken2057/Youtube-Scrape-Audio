from threading import Thread
# ------------------------------------------------------------------------------
from src.scrapeYoutube import singleSong
from src.audio import downloadAudio, playSound
from src.io import writeJson, writeNext
from src.config import BASE_URL, JSON_NAME_PATH
# ------------------------------------------------------------------------------
# set daemon = True so when Ctrl+C it will kill all thread
def newThread():
    '''
    
    Create empty thread
    
    return: Thread

    '''
    return Thread()

def thrWriteJson(data, path):
    '''
    
    Create thread write data to json file

    data: string
    path: string

    '''
    d = Thread(target=writeJson, args=(data, path,))
    d.daemon = True
    d.start()

def thrWriteNext(string, path):
    '''

    Create thread write error

    string: string
    path: string

    '''
    d = Thread(target=writeNext, args=(string, path,))
    d.daemon = True
    d.start()

def thrDownload(url):
    '''

    Create thread download song (when fetch next song)

    url: string

    '''
    d = Thread(target=downloadAudio, args=(url,))
    d.daemon = True
    d.start()

def thrFetchSong(url):
    '''

    Fetch song reccommend from youtube

    url: string

    '''
    # f = Thread(target=writeJson, args=(singleSong(BASE_URL + url,), JSON_NAME_PATH,))
    # change function so thread don't need to wait result of singSong to execute writeJson
    f = Thread(target=singleSong, args=(BASE_URL + url, True,),) 
    f.daemon = True
    f.start()

def thrSong(song):
    '''

    Create thread play audio

    song: dict

    return: Thread

    '''
    return Thread(target=playSound, args=(song,))