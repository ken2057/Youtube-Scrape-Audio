
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
