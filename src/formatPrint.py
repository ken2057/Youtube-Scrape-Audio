from os import system
import platform
# ------------------------------------------------------------------------------
from src.config import SHORT_URL
# ------------------------------------------------------------------------------
def changeTitle(title):
    system("title "+'\"'+str(title)+'\"')

def clearScreen():
    if platform.system() == 'Windows':
        system('cls')
    else:
        system('clear')

def printMusicStatus(song):
    if 'title' in song.curSong:
        print(song.__str__())
    else:
        print('Watting song')
        changeTitle('Waitting song')

def printSongs(listSong, page, totalPage, note=None):
    clearScreen()
    print('-'*20)
    for i, s in enumerate(listSong, 0):
        print('- sID:', i, '\t-\t', s['title'])
        print(
            '- Time:', s['time'], 
            '\t-\tChannel:', s['channel'],
            '\t-\tViews:', s['views']
        )
        # print('- Time:', s['time'])
        # print('- Channel:', s['channel'])
        # print('- Views:', s['views'])
        print('- Link:', SHORT_URL + s['id'])
        print('-'*20)
    print("Current page: %s/%s"%(page + 1, totalPage))
    if note != None:
        print(note)

def printHelp():
    print()
    print('Help!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print()
    print('$ downs|d <page>\t\t\t: Show downloaded song')
    print('$ search|s <query>\t\t\t: Search song with query')
    print('$ songs <page>\t\t\t\t: Show recommend song based on YT')
    print()
    print("$ play|p <sID>\t\t\t\t: Play song from songs/search/downs current page")
    print("$ play|p <URL>|<YT_ID>\t\t\t: Play song youtube url or youtube video id")
    print()
    print('$ playdowns|pd\t\t\t\t: Play all sone in downloaded')
    print('$ queue|q\t\t\t\t: Show current queue')
    print('$ qshuffle|qsf\t\t\t\t: Turn ON/OFF queue shuffle')
    print()
    print('$ next|n\t\t\t\t: Play next song')
    print('$ nexti|ni\t\t\t\t: Show next song info')
    print('$ setnext|setn <sID>\t\t\t: Set next song from songs/search/downs curren page')
    print()
    print('$ prev\t\t\t\t\t: Play previous song')
    print('$ previ\t\t\t\t\t: Show previous song info')
    print()
    print("$ volume|v\t\t\t\t: Show current volume level")
    print("$ volume|v <float>\t\t\t: Set volume level")
    print()
    print("$ pause|unpause|play|P\t\t\t: Did what they say")
    print("$ skip <second>\t\t\t\t: Skip song time from current time")
    print("$ info\t\t\t\t\t: Show information of current song")
    print("$ copy|cp\t\t\t\t: Copy current song url to clipboard")
    print('$ repeat|re [time]\t\t\t: Repeat\\Un-repeat current song x time, (not input time, it will run forever)')
    print()
    print('$ cls|clear\t\t\t\t: Clear screen')
    print('$ help|h\t\t\t\t: Show this')
    print()
    print("$ delete|del <sID> [sID]*\t\t: Delete song from downloaded, can delete many")
    print('$ delete-all\t\t\t\t: Delete all the song in audio/, and json file')
    print()
    print('$ exit\t\t\t\t\t: Surely is Exit')
    print()
    print("Commands can be change in config.CMD")
