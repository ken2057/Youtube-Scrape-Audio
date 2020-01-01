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

# Dependences
```json
python3
ffmpeg 
youtube_dl (python)
requests (python)
beautifulsoup4 (python)
pygame==2.0.0.dev6 (python) //I need 2.0.0 to use pygame.mixer.music.unload()
```
<hr>

# Installation
## 1. Clone repo
## 2. Install Python3
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
$ (env) D:\project\scrape-youtube-music> _
```
## 3. Install python package
### Windows
```js
$ pip install -r requirements.txt
``` 
## 4. Get ffmpeg - [download link](https://ffmpeg.zeranoe.com/builds/)
### Windows:
```js
Download the verson depence on your computer and exact it
Then add path bin/ to Windows path variable
This app only need ffmpeg.exe in bin/ so you can delete other file for spaces

If you are using win10 64bit
You can go into bin/ and exact the file ffmpeg.7z
And add path to Windows path varible
```
## 5. Run
### Windows
```js
$ python main.py
```

<hr>

# Usage
## All command
```
$ downs|d <page>                    : Show downloaded song
$ playd|pd <sID>                    : Play downloaded with sound ID in current page

$ search|s <query>                  : Search song with query
$ plays|ps <sID>                    : Play song from search list result with sID

$ songs <page>                      : Show recommend song based on YT
$ play|p <sID>                      : Play song from 'songs' current page

$ next|n                            : Play next song
$ nexti|ni                          : Play next song info

$ volume|v                          : Show current volume level
$ volume|v <float>                  : Set volume level
$ pause|unpause|play                : Did what they say
$ skip <second>                     : Skip song time from current time
$ info                              : Show information of current song

$ cls|clear                         : Clear screen
$ help|h                            : Show this

$ delete-all                        : Delete all the song in audio/

$ exit                              : Surely is Exit
```
## Example
```js
$ search can we kiss forever //it will get top 6 result from youtube
$ plays 0                    // play first song from search result
```

```js
$ downs       // check which song have been downloaded in audio/
$ playd 0     // play song ID 0 in list downloaded
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