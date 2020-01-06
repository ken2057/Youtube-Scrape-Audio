from tabulate import tabulate
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

def printSongQueue(song):
    print('[x]', song.curSong['title'])
    songs = [song.nextSong] + song.queue
    for i, s in enumerate([x for x in songs if x != {}], 1):
        print('[%s] %s'%(i, s['title']))
    print()

def printAllPlaylist(allPl):
    clearScreen()
    # get file name only

    allPl = [{x.split('\\')[-1].replace('.json', '')} for x in allPl]
    print('All playlist')
    print(tabulate(allPl, showindex=True, headers=['Name']))
    print('-'*20)
    print("Use 'playlist|pl <index>' to select playlist")

def printSongSimple(
        listSong, 
        showView=False, 
        title=None, note=None, 
        curPage=1, maxPage=1):
    if curPage > maxPage:
        return
    clearScreen()
    if title != None:
        print(title)
    songs = []
    # create format to use tabulate
    for i, song in enumerate(listSong, 0):
        s = {
            'sID': i,
            'Title': song['title'].strip(' \t'),
            'Length': song['time'].strip(' \t'),
            'Channel': song['channel'].strip(' \t')
        }
        # if title to long, get 47 char and add '...'
        if len(s['Title']) > 50:
            s['Title'] = s['Title'][:47]+'...'
        if showView:
            s['Views'] = song['views'].replace(' views', '').strip(' \t')
        songs.append(s)

    print(tabulate(songs, headers="keys") )
    print('-'*20)
    print('Current page: %s/%s'%(curPage, maxPage))
    if note != None:
        print(note)
    

def printHelp():
    print()
    print('Help!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print()
    print('Note:')
    print("   '*': multiable")
    print('   range: syntax <min_num>-<max_num> (ex: 1-3)')
    print('   [...]: optional')
    print("   '|': or")
    print("   sID: song ID")
    print("   pl: playlist")
    print()
    print('$ downs|d <page>\t\t\t: Show downloaded song')
    print('$ search|s <query>\t\t\t: Search song with query')
    print('$ songs <page>\t\t\t\t: Show recommend song based on YT')
    print()
    print("$ play|p <sID>\t\t\t\t: Play song from songs/search/downs current page")
    print("$ play|p <URL>|<YT_ID>\t\t\t: Play song youtube url or youtube video id")
    print()
    print('$ playdowns|pd\t\t\t\t: Play all sone in downloaded')
    print()
    print('$ queue|q\t\t\t\t: Show current queue')
    print('$ qshuffle|qsf\t\t\t\t: Turn ON/OFF queue shuffle')
    print('$ qadd|qa [sID|URL|range]*\t\t\t: Add song to queue, if no params, add all song in current page')
    print('$ qremove|qr [sID|range]*\t\t\t: Remove song in queue w/ sID, if no params, remove all queue')
    print()
    print('$ playlist|pl [index|name]\t\t: Show all pl, show song in pl w/ pl index or pl name (selected that pl)')
    print('$ plinfo|pli \t\t\t\t: Show all song of selected pl')
    print('$ playpl|ppl [index|name]\t\t: Play current pl or play pl w/ pl index or pl name')
    print('$ pladd|pla [range|sID]*\t\t: If no params add current song to pl else add song from range sID or w/ sID')
    print('$ plre|plr [range|sID]*\t\t\t: If no params remove all song in pl else remove song from range sID or w/ sID')
    print()
    print('$ newpl|npl [name]\t\t\t: Create new pl with name')
    print('$ renamepl|repl [name]\t\t\t: Rename current pl seletected')
    print('$ delpl|dpl [index|name]*\t\t: Delete pl with index/name')
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
    print("$ delete|del [sID|range]1*\t\t: Delete song from downloaded, can delete many")
    print('$ delete-all\t\t\t\t: Delete all the song in audio/, and json file')
    print()
    print('$ exit\t\t\t\t\t: Surely is Exit')
    print()
    print("Commands can be change in config.CMD")
