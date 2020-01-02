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