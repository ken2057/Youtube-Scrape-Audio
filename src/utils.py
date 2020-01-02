
# ------------------------------------------------------------------------------
from src.config import DOWN_FOLDER
# ------------------------------------------------------------------------------
# get 4:12 turn to time useable
def calcTime(time):
    t = time.split(':')
    return int(t[0]) * 60 + int(t[1])

# turn seconds to mm:ss
def formatSeconds(total):
    m  = int(total/60)
    s = total - m*60
    return str(m).zfill(2)+':'+str(s).zfill(2)

def getSongId(url):
    return url.replace('/watch?v=', '')

def getPathMp3(url):
    return DOWN_FOLDER+ '/' + getSongId(url) +  '.mp3'