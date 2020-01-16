from difflib import SequenceMatcher
from re import search
from emoji import get_emoji_regexp
from pathlib import Path
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# get 4:12 turn to time useable
def calcTime(time):
    '''

    Calculate total second from string time format mm:ss

    time: string (format mm:ss)

    return: int

    '''
    t = time.split(':')
    return int(t[0]) * 60 + int(t[1])

def formatSeconds(total):
    '''

    Turn seconds to mm:ss

    total: int (total second)

    return: string (format mm:ss)

    '''
    m  = int(total/60)
    s = total - m*60
    return str(m).zfill(2)+':'+str(s).zfill(2)

def getSongId(url):
    return url.replace('/watch?v=', '')

def str_similar(a, b):
    '''
    
    Check 2 string similarity

    a: string
    b: string

    return: float

    '''
    return SequenceMatcher(None, a, b).ratio()

    # check file name valid (regex)

def is_valid_filename(name):
    '''

    Check valid file name before create

    name: string

    return: bool

    '''
    try:
        # name not number only
        _ = int(name)
        print('Name much contain at least 1 character')
        return False
    except:
        return search('[a-zA-Z0-9]', name)

def filename_from_path(path):
    '''

    Get filename only (for playlist)

    path: string

    return: string

    '''
    # Remove '.json' 1 time from tail
    return path.split('/')[-1].replace('.json', '', 1)

def remove_emoji(text):
    '''

    Remove some emoji in string

    text: string

    return: string

    '''
    return get_emoji_regexp().sub(u'', text)

def folder_size(path):
    '''

    Calculate folder size

    path: string

    return: float (MB)

    '''
    folder = Path(path)
    size = sum(f.stat().st_size for f in folder.glob('**/*') if f.is_file())
    # convert bytes to MB
    return round(size / pow(1024, 2), 2)