import requests, sys
from bs4 import BeautifulSoup as BS
# ------------------------------------------------------------------------------
from src.config import ID_REC
# ------------------------------------------------------------------------------
# list str will be trim from string
listStrRemove = ['', '  ', '\n', '\r','  \n', '  \r', 'None']
# ------------------------------------------------------------------------------

def singleSong(url):
    page = requests.get(url)
    soups = BS(page.content, 'html.parser').find(id=ID_REC).find_all('a')

    listContent = []

    for a in soups:
        content = [a['href']]
        for child in a.contents:
            s = str(child.string)
            # trim some space, tab, enter in head of str
            for c in listStrRemove:
                s = s.strip(c)
            # if s not empty => add to list
            # s will be remove Enter before add
            if s not in listStrRemove: 
                content.append(s.replace('\n', '').replace('\r', ''))
        if len(content) == 5:
            listContent.append(content)
    return listContent

def playlist(url):
    page = requests.get(url)
    # soups = BS(page.content, 'html.parser').find(class_='watch-queue-items-container')
    # , class_='yt-uix-scroller-scroll-unit'
    # class_='playlist-video'
    # .find(class_='playlist-items')

    soups = BS(str(page.content).replace('\\n', '\n'), 'html.parser')

    print(soups.prettify().replace('\\n', '\n').encode('utf-8'))