from os import path
from copy import copy
from random import randint
# ------------------------------------------------------------------------------
from src.io import readJson
from src.audio import downloadAudio
from src.utils import calcTime, formatSeconds
from src.createThread import thrDownload, thrFetchSong
from src.config import JSON_MCONFIG_PATH, JSON_DOWNLOADED_PATH
# ------------------------------------------------------------------------------
class Song():
	mixer = None
	isPlaying = False
	isFinish = False
	isPause = False
	isEdit = False
	skipped = 0

	curSong = {}
	nextSong = {}
	prevSong = {}
	# list of song
	queue = []
	isShuffle = False

	# millisecond to second + skipped time
	def mixer_get_pos(self):
		return int((self.mixer.get_pos()/1000 + self.skipped))

	def is_skipable(self, second):
		return self.mixer_get_pos() + second < calcTime(self.curSong['time'])
	
	def skip_time(self, second):
		self.isEdit = True
		self.mixer.pause()
		self.skipped += second
		self.mixer.play(0, self.mixer_get_pos())
		self.isEdit = False

	def prev_song(self):
		self.nextSong = copy(self.curSong)
		self.curSong = copy(self.prevSong)
		self.prevSong = {}
		self.reset_play_value()

	def next_song(self):
		self.prevSong = copy(self.curSong)
		self.curSong = copy(self.nextSong)
		self.nextSong = {}
		self.reset_play_value()
		# select song different with prevSong
		self.select_nextSong()
		thrFetchSong(self.curSong['url'])
	
	def finish_song(self):
		self.skipped += 1 #missing 1s KEKW	
		self.isFinish = True
		self.isPlaying = False
	
	def set_mixer(self, skip=False):
		# when use cmd 'skip', download next song
		if skip:
			downloadAudio(self.curSong)

		# unlocad() can only use in pygame==2.0.0
		# but not released => temp use pygame==2.0.0.dev6
		self.mixer.unload()
		# return before load if not exists
		if not path.exists(self.curSong['path']):
			return
		self.mixer.load(self.curSong['path'])
		self.mixer.set_volume(readJson(JSON_MCONFIG_PATH)['volume'])
		self.mixer.play()
		# pre-print, (lazy way)
		if not skip:
			print('\n\n'+self.__str__()+'\n$ ', end='')

	def down_next_song(self):
		# played 70% of the song, download next song
		if 'path' not in self.nextSong or self.nextSong == {}:
			# move down calcTime and if to reduce usage
			total = calcTime(self.curSong['time'])
			if self.mixer_get_pos() >= total * 0.7 and 'downloading' not in self.nextSong:
				self.select_nextSong()
				# add status to block create thread download
				self.nextSong['downloading'] = True
				thrDownload(self.nextSong)
			
	def __str__(self):
		status = 'Loading'
		if self.isPlaying:
			status = 'Playing'
		elif self.isPause:
			status = 'Pause'
		elif self.isFinish:
			status = 'Finished'
		# format will be <current play time>/<total>
		# format time will be mm:ss
		time = formatSeconds(self.mixer_get_pos())+'/'+self.curSong['time']
		# title - channel name
		curSong = self.curSong['title']+' - '+self.curSong['channel']
		return status+' '+time+': '+ curSong
	
	def pause_song(self):
		self.isPause = True
		self.isPlaying = False
		self.mixer.pause()
	
	def unpause_song(self):
		self.isPause = False
		self.isPlaying = True
		self.mixer.unpause()  

	def select_nextSong(self):
		# current not playing any song or already have nextSong queue
		if self.curSong == {} or self.nextSong != {}:
			return
		# when have queue song, play until fisnish queue
		if len(self.queue) != 0:
			self.set_next_from_queue()
			return

		# read from json
		listSong = readJson()
		# if recommend song empty, make downloaded become a queue
		if listSong == []:
			self.queue = readJson(JSON_DOWNLOADED_PATH)
			self.set_next_from_queue()
			return

		# select song different with prevSong
		for song in listSong:
			if self.prevSong == {} or song['url'] != self.prevSong['url']:
				# check currentSong and nextSong not same
				if song['url'] != self.curSong['url']:
					self.nextSong = song
					break
	
	def reset_play_value(self):
		self.isFinish = False
		self.isPlaying = True
		self.skipped = 0

	def reset_all(self):
		self.isPlaying = False
		self.isFinish = False
		self.isPause = False
		self.isEdit = False
		self.mixer = None
		self.skipped = 0
		self.prevSong = {}
		self.nextSong = {}
		self.curSong = {}

	def set_next_from_queue(self):
		pos = 0
		if self.isShuffle:
			pos = randint(0, len(self.queue))
			
		self.nextSong = copy(self.queue[pos])
		self.queue.pop(pos)
