from glob import glob
from json import load, dump
from os import remove
from datetime import datetime
from traceback import TracebackException
import logging
# -----------------------------------------------------------------------------
from src.config import (
    JSON_DOWNLOADED_PATH, 
    JSON_MCONFIG_PATH,
    JSON_NAME_PATH, 
    DOWN_FOLDER, 
    COOKIE_PATH,
    ERROR_PATH, 
    ERROR_HIDE, 
)
# -----------------------------------------------------------------------------
# READ
# -----------------------------------------------------------------------------
# default get list next song
def readJson(path=JSON_NAME_PATH):
    with open(path, 'r', encoding='utf8') as j:
        return load(j)
# -----------------------------------------------------------------------------
# WRITE
# -----------------------------------------------------------------------------
def writeJson(data, path):
    with open(path, 'w', encoding='utf8') as j:
        dump(data, j, ensure_ascii=True)

def writeDownloaded(song):
    listSong = readJson(JSON_DOWNLOADED_PATH)
    listSong.append(song)
    writeJson(listSong, JSON_DOWNLOADED_PATH)


def writeNext(string, path):
    with open(path, 'a', encoding='utf8') as f:
        f.writelines(string + '\n')

def writeErrorLog(error, data=None):
    note = []
    note.append('Time: ' + datetime.now().__str__())
    if data != None:
        note.append('Input: '+ data)
    trace = TracebackException.from_exception(error)
    note.append(''.join(trace.format()))

    writeNext('\n'.join(note) + '\n', ERROR_PATH)

    # some error will not need to print out
    if len([x for x in ERROR_HIDE if x in str(error)]) == 0:
        logging.error('\n'+str(error))

# -----------------------------------------------------------------------------
# OTHER
# -----------------------------------------------------------------------------
def updateConfig(newData):
    data = readJson(JSON_MCONFIG_PATH)
    data.update(newData)
    writeJson(data, JSON_MCONFIG_PATH)

# delete songs in downloaded
def deleteSongs(songs):
    try:
        data = readJson(JSON_DOWNLOADED_PATH)
        
        for song in songs:
            # remove mp3 file
            remove(song['path'])
            # remove item in json
            data.remove(song)
            
        writeJson(data, JSON_DOWNLOADED_PATH)
    except Exception as ex:
        writeErrorLog(ex)

def deleteAllSong():
    files = glob(DOWN_FOLDER+'/*')
    if (len(files) == 0):
        print('Nothing to delete')
        return
    print('Deleting '+str(len(files))+' in audio/')
    for f in files:
        remove(f)
    writeJson([], JSON_DOWNLOADED_PATH)
    writeJson([], JSON_NAME_PATH)
    # delete log
    try:
        remove(ERROR_PATH)
    except:
        pass
    # delete cookie
    try:
        remove(COOKIE_PATH)
    except:
        pass
    print('Done')

def getInDownloaded(song):
    for s in readJson(JSON_DOWNLOADED_PATH):
        if song['id'] == s['id']:
            return s
    return song
