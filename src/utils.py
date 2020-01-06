from difflib import SequenceMatcher
from re import search
# ------------------------------------------------------------------------------

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

def str_similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

    # check file name valid (regex)
def is_valid_filename(name):
    return search('[a-zA-Z0-9]', name)

def filename_from_path(path):
    # get filename only (for playlist)
    # remove '.json' 1 time from tail
    return path.split('/')[-1].replace('.json', '', 1)
