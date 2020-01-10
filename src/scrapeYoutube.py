from bs4 import BeautifulSoup as BS
from http import cookiejar
from requests import get
# ------------------------------------------------------------------------------
from src.config import (
    QUERY_URL, 
    COOKIE_PATH, 
    JSON_NAME_PATH,
    MAX_LENGTH_VIDEO,
)
from src.io import writeErrorLog, writeJson
from src.utils import getSongId, remove_emoji
# ------------------------------------------------------------------------------
# headers when send request (get english only)
header={'accept-language':'en;q=0.9'}

# cookie for better recommending
def getCookie():
    try:
        return cookiejar.MozillaCookieJar(COOKIE_PATH).cookie.load()
    except:
        return None

# ------------------------------------------------------------------------------
# list str will be trim from string
# ------------------------------------------------------------------------------
def listStrip(string):
    # trim some space, tab, enter in head of str
    return str(string).strip(' \n\t\r')

def isValidSong(song):
    if 'views' not in song:
        song['views'] = '?'
    # min max 5 key
    if len(song) != 5:
        return None
    # any value is '' => None
    for _, v in song.items():
        if v in ['', None]:
            return None
    
    try:
        # reverser list to easy calculate time
        # from [minute, second] => [second, minute]
        # from [hours, minute, second] => [second, minute, hours]
        splited = song['time'].split(': ')[1].replace('.', '').split(':')[::-1]

        # time from splited to multi [second, minute, hours] to second
        time = [1, 60, 3600]
        total_second = 0
        for spl, t in zip(splited, time):
            total_second += int(spl) * t
        
        if total_second >= MAX_LENGTH_VIDEO:
            return None

        song['time'] = ':'.join(splited[::-1])
    # error when don't have video length, or not correct format
    except:
        return None

    return song

def singleSong(url, write_file=False):
    from datetime import datetime
    try:
        r = get(url, headers=header, cookies=getCookie()) 
        soups = BS(r.content, 'html.parser').find(id='watch7-sidebar-modules').find_all('a')
        
        #
        order = ['title', 'time', 'channel', 'views']
        listContent = []
        for a in soups:
            content = {'id': getSongId(a['href'])}
            # zip to add to dict
            contentA = [listStrip(x.string) for x in a]
            contentA = [x for x in contentA if x not in ['']] #'Recommended for you'
            for k, v in zip(order, contentA):
                content[k] = listStrip(v).replace('Recommended for you', 'Recomend')
            # check valid
            content = isValidSong(content)
            if content != None:
                content['title'] = remove_emoji(content['title'])
                listContent.append(content)
        if not write_file:
            return listContent
        else:
            # use this so thread will not need to wait reuslt of this function
            writeJson(listContent, JSON_NAME_PATH)
    except Exception as ex:
        writeErrorLog(ex)
        return []

def fetchQuery(query):
    try:
        url = QUERY_URL + query.replace(' ', '+')
        r = get(url, headers=header, cookies=getCookie())

        soups = BS(r.text, 'html.parser').body.find(class_='item-section').find_all(class_='yt-lockup-content')
        
        listContent = []
        for a in soups:
            # prevent error from channel information
            try:
                song = {
                    'title': remove_emoji(listStrip(a.find('a').string)),
                    'time': listStrip(a.find('span').string),
                    'id': getSongId(listStrip(a.find('a')['href'])),
                    'channel': listStrip(a.find_all('a')[1].string),
                    'views': listStrip(a.find_all('li')[1].string)
                }
                song = isValidSong(song)
                if song != None:
                    listContent.append(song)
            except:
                pass
        return listContent

    except Exception as ex:
        writeErrorLog(ex)
        return []
