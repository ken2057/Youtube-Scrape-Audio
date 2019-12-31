import requests, sys
import urllib.parse
from bs4 import BeautifulSoup as BS
# ------------------------------------------------------------------------------
from src.config import ID_REC
from src.config import QUERY_URL
# ------------------------------------------------------------------------------
# headers when send request (get english only)
header={'accept-language':'en;q=0.9'}

# ------------------------------------------------------------------------------
# list str will be trim from string
# ------------------------------------------------------------------------------
def listStrip(string):
    # trim some space, tab, enter in head of str
    return str(string).strip(' \n\t\r')

def isValidSong(song):
    # min max 5 key
    if len(song) != 5:
        return None
    # any value is '' => None
    for _, v in song.items():
        if v in ['', None]:
            return None
    
    try:
        splited = song['time'].split(': ')[1].replace('.', '').split(':')
        # less than 1hour
        flag1 = len(splited) > 2
        # duration > 15min?
        flag2 = int(splited[0]) >= 15
        if flag1 or flag2:
            return None
        song['time'] = ':'.join(splited)
    except:
        return None

    return song

def singleSong(url):
    try:
        page = requests.get(url, headers=header)
        soups = BS(page.content, 'html.parser').find(id=ID_REC).find_all('a')
        #
        order = ['title', 'time', 'channel', 'views']
        listContent = []
        for a in soups:
            content = {'url': a['href']}
            # zip to add to dict
            contentA = [listStrip(x.string) for x in a]
            contentA = [x for x in contentA if x != '']
            for k, v in zip(order, contentA):
                content[k] = listStrip(v)
            # check valid
            content = isValidSong(content)
            if content != None:
                listContent.append(content)
        return listContent
    except Exception as ex:
        print('error get suggest song:',ex)
        return []

def playlist(url):
    page = requests.get(url)
    # soups = BS(page.content, 'html.parser').find(class_='watch-queue-items-container')
    # , class_='yt-uix-scroller-scroll-unit'
    # class_='playlist-video'
    # .find(class_='playlist-items')

    soups = BS(str(page.content).replace('\\n', '\n'), 'html.parser')

    print(soups.prettify().replace('\\n', '\n').encode('utf-8'))

def fetchQuery(query):
    try:
        query = QUERY_URL + urllib.parse.quote(query)
        page = requests.get(query, headers=header)
        soups = BS(page.text, 'lxml').body.find(class_='item-section').find_all(class_='yt-lockup-content')
        
        listContent = []
        for a in soups:
            # prevent error from channel information
            try:
                song = {
                    'title': listStrip(a.find('a').string),
                    'time': listStrip(a.find('span').string),
                    'url': listStrip(a.find('a')['href']),
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
        print('error query:',ex)
        return []