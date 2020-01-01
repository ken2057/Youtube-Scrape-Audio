import json, os, glob
from datetime import datetime
# -----------------------------------------------------------------------------
from src.config import JSON_NAME_PATH, JSON_FORMAT, JSON_PLAYLIST_PATH, ERROR_PATH
from src.config import JSON_MCONFIG_PATH, JSON_DOWNLOADED_PATH, DOWN_FOLDER
# -----------------------------------------------------------------------------
# default get list next song
def readJson(path=JSON_NAME_PATH):
    with open(path, 'r', encoding='utf8') as j:
        return json.load(j)

def writeJson(data, path):
    with open(path, 'w', encoding='utf8') as j:
        json.dump(data, j, ensure_ascii=True)

def writeDownloaded(song):
    listSong = readJson(JSON_DOWNLOADED_PATH)
    listSong.append(song)
    writeJson(listSong, JSON_DOWNLOADED_PATH)

def updateConfig(newData):
    data = readJson(JSON_MCONFIG_PATH)
    data.update(newData)
    writeJson(data, JSON_MCONFIG_PATH)

def writeNext(string, path):
    with open(path, 'a', encoding='utf8') as f:
        f.writelines(string + '\n')

def deleteAllSong():
    files = glob.glob(DOWN_FOLDER+'/*')
    if (len(files) == 0):
        print('Nothing to delete')
        return
    print('Deleting '+str(len(files))+' in audio/')
    for f in files:
        os.remove(f)
    writeJson([], JSON_DOWNLOADED_PATH)
    writeJson([], JSON_NAME_PATH)
    # delete log
    try:
        os.remove('error.txt')
    except:
        pass
    print('Done')

def writeErrorLog(error, function, data=None):
    note = []
    note.append('Time: ' + datetime.now().__str__())
    note.append('Func: ' + function)
    if data != None:
        note.append('Input: '+ data)
    note.append('Error: '+ str(error))

    writeNext('\n'.join(note) + '\n', ERROR_PATH)
    print('\nError:', str(error)+'\n$ ')