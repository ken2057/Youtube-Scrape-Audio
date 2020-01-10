# **Youtube Scrape Audio**

<hr>

# About
### I usually listen to music on Youtube, so I have an idea that to create a script scrape the YT HTML to get sound information and listen on it.
### All the song will be download at mp4 and convert to mp3 via ffmpeg, and stored in audio/ for listen later
### All the result will come from Youtube
### Current only work with Windows. Other OS have error with open mp3 via pygame.mixer
### Song length greater than or euqal 15 minutes will not showed
### After playing 70% of current song, it will download next song
<hr>

# Features:
- [x] Search/Play song
- [x] Store song
- [x] Play song with youtube link|video id
- [x] Delete songs in downloaded
- [x] Repeat/Unrepeat
- [x] Set next song
- [x] Add to queue, Remove in queue
- [x] Custom playlist
- [x] Copy current song link to clipboard
- [x] Play YT playlist
- [x] Export/Import playlist (from my simple api, mongodb cluster)

# Dependences
```json
python3
ffmpeg // Video convert
youtube_dl (python)
requests (python)
beautifulsoup4 (python)
pygame==2.0.0.dev6 (python) //I need 2.0.0 to use pygame.mixer.music.unload()
pyperclip (python)
tabulate (python)
emoji (python)
```
<hr>

# Installation

## 1. Clone repo
## 2. Install Python3

## 3. Install package, ffmpeg
<details>
    <summary>Option 1: Using script</summary>
<p>

## - Double-click `install.bat`
```js
This script will do:
    - Extract ffmpeg in bin/ base on your OS 32bit or 64bit
    - Create virtualenv (optional)
    - Install python package
```

</p>
</details>

<details>
    <summary>Option 2: Install by yourself</summary>
<p>

```js
// This is optional
use 'virtualenv' for easy delete later
$ pip install virtualenv
// Go to repo folder
// Create a virtual enviroment for python with name 'env'
$ virtualenv env
// active virtualenv
$ env\Script\activate
// If you command promt show (env) on the first, it worker
// Example: 
$ (env) D:\project\youtube-scrape-audio> _
```
## - Install python package
```js
$ pip install -r requirements.txt
``` 
## - Extract ffmpeg in bin/
```js
Choose which version base on your OS 32/64bit
Then extract it
```

</p>
</details>

## 4. Add bin/ path to your Path Environment

## 5. Run
```js
$ python main.py // cmd need to cd into repo path
or
$ ytsa // active script from any path
```

<hr>

# Usage
## All command
```
Note:
   '*': multiable
   range: syntax <min_num>-<max_num> (ex: 1-3)
   [...]: optional
   '|': or
   sID: song ID
   pl: playlist

$ downs|d <page>                        : Show downloaded song
$ search|s <query>                      : Search song with query
$ songs <page>                          : Show recommend song based on YT

$ play|p <sID>                          : Play song from songs/search/downs current page
$ play|p <URL>|<YT_ID>                  : Play song youtube url or youtube video id

$ playdowns|pd                          : Play all sone in downloaded

$ queue|q                               : Show current queue
$ qshuffle|qsf                          : Turn ON/OFF queue shuffle
$ qadd|qa [sID|URL]*                    : Add song to queue, if no params, add all song in current page
$ qremove|qr [sID]*                     : Remove song in queue w/ sID, if no params, remove all queue

$ playlist|pl [index|name]              : Show all pl, show song in pl w/ pl index or pl name (selected that pl)
$ plinfo|pli                            : Show all song of selected pl
$ playpl|ppl [index|name]               : Play current pl or play pl w/ pl index or pl name
$ pladd|pla [range|sID|URL|YT_ID]*      : If no params add current song to pl else add song from range sID or w/ sID
$ plre|plr [range|sID]*                 : If no params remove all song in pl else remove song from range sID or w/ sID

$ newpl|npl [name]                      : Create new pl with name
$ renamepl|repl [name]                  : Rename current pl seletected
$ delpl|dpl [index|name]*               : Delete pl with index/name

$ next|n                                : Play next song
$ nexti|ni                              : Show next song info
$ setnext|setn <sID>                    : Set next song from songs/search/downs curren page

$ prev                                  : Play previous song
$ previ                                 : Show previous song info

$ volume|v                              : Show current volume level
$ volume|v <float>                      : Set volume level

$ pause|unpause|play|P                  : Did what they say
$ skip <second>                         : Skip song time from current time
$ info                                  : Show information of current song
$ copy|cp                               : Copy current song url to clipboard
$ repeat|re [time]                      : Repeat\\Un-repeat current song x time, (not input time, it will run forever)

$ login                                 : Change username, password
$ import                                : Import all playlist from db (this is my api, mongodb cluster)
$ export [all|index|playlist_name]      : Export playlist from db (this is my api, mongodb cluster)

$ cls|clear                             : Clear screen
$ usage                                 : Get usage
$ help|h                                : Show this

$ delete|del <sID> [sID]*               : Delete song from downloaded, can delete many
$ delete-all                            : Delete all the song in audio/, and json file

$ exit                                  : Surely is Exit
```
## Example
```js
$ search can we kiss forever //it will get top 6 result from youtube
$ play 0                    // play first song from search result
```

```js
$ downs       // check which song have been downloaded in audio/
$ play 1     // play song ID 1 in list downloaded
```
```js
$ nexti       // display next song info
$ info        // display current song info
$ next        // play next song
$ skip 100    // skip 100s on current song
```
```js
$ delete-all  // delete all file in audio/ for spaces
```