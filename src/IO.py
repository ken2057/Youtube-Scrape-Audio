import json
# -----------------------------------------------------------------------------
from src.config import JSON_NAME_PATH, JSON_FORMAT, JSON_PLAYLIST_PATH
from src.config import JSON_MCONFIG_PATH, JSON_DOWNLOADED_PATH
# -----------------------------------------------------------------------------

def readJson(path=JSON_NAME_PATH):
    with open(path, 'r', encoding='utf8') as j:
        return json.load(j)

def writeJson(data, path):
    with open(path, 'w', encoding='utf8') as j:
        json.dump(data, j, ensure_ascii=True)

# only work for scrape web
def writeFetchJson(listContent):
    data = []
    for content in listContent:
        song = {}
        for i, value in enumerate(JSON_FORMAT, 0):
            # if value == 'time':
            #     song[value] = content[i][2:]
            # else:
            song[value] = content[i].strip(' ')
        data.append(song)
    # write
    writeJson(data, JSON_NAME_PATH)

def writeDownloaded(song):
    listSong = readJson(JSON_DOWNLOADED_PATH)
    listSong.append(song)
    writeJson(listSong, JSON_DOWNLOADED_PATH)

def updateConfig(newData):
    data = readJson(JSON_MCONFIG_PATH)
    data.update(newData)
    writeJson(data, JSON_MCONFIG_PATH)
