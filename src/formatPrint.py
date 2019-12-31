import os, platform
# ------------------------------------------------------------------------------
from src.utils import formatSeconds
from src.config import BASE_URL
# ------------------------------------------------------------------------------
def clearScreen():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def printMusicStatus(song):
    if 'title' in song.curSong:
        print(song.__str__())
    else:
        print('Watting song')

def printSongs(listSong, page, totalPage, note=None):
    clearScreen()
    print('-'*20)
    for i, s in enumerate(listSong, 0):
        print('- sID:', i)
        print('- Name:', s['title'])
        print('- Time:', s['time'])
        print('- Channel:', s['channel'])
        print('- Views:', s['views'])
        print('- Link:', BASE_URL + s['url'])
        print('-'*20)
    print("Current page: %s/%s"%(page + 1, totalPage))
    if note != None:
        print(note)

def printHelp():
    print()
    print('Help!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print()
    print('$ downs|d <page>\t\t\t: Show downloaded song')
    print('$ playd|pd <sID>\t\t\t: Play downloaded with sound ID in current page')
    print()
    print('$ search|s <query>\t\t\t: Search song with query')
    print('$ plays|ps <sID>\t\t\t: Play song from search list result with sID')
    print()
    print('$ songs <page>\t\t\t\t: Show recommend song based on YT')
    print("$ play|p <sID>\t\t\t\t: Play song from 'songs' current page")
    print()
    print('$ next|n\t\t\t\t: Play next song')
    print('$ nexti|ni\t\t\t\t: Play next song info')
    print()
    print("$ volume|v\t\t\t\t: Show current volume level")
    print("$ volume|v <float>\t\t\t: Set volume level")
    print("$ pause|unpause|play\t\t\t: Did what they say")
    print("$ skip <second>\t\t\t\t: Skip song time from current time")
    print("$ info\t\t\t\t\t: Show information of current song")
    print()
    print('$ cls|clear\t\t\t\t: Clear screen')
    print('$ help|h\t\t\t\t: Show this')
    print()
    print('$ delete-all\t\t\t\t: Delete all the song in audio/')
    print()
    print('$ exit\t\t\t\t\t: Surely is Exit')