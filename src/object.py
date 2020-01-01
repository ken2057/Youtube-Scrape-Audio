import copy
from os import path
# ------------------------------------------------------------------------------
from src.audio import downloadAudio
from src.CreateThread import thrDownload, thrFetchSong
from src.IO import readJson
from src.utils import calcTime, formatSeconds, getPathMp3
from src.config import JSON_MCONFIG_PATH
# ------------------------------------------------------------------------------
class Song():
	playing = False
	finish = False
	pause = False
	edit = False
	mixer = None
	skipped = 0
	curSong = {}
	nextSong = {}
	prevSong = {}

	def __intit__(self):
		pass

	# millisecond to second + skipped time
	def mixer_get_pos(self):
		return int((self.mixer.get_pos()/1000 + self.skipped))

	def is_skipable(self, second):
		return self.mixer_get_pos() + second < calcTime(self.curSong['time'])
	
	def skip_time(self, second):
		self.edit = True
		self.mixer.pause()
		self.skipped += second
		self.mixer.play(0, self.mixer_get_pos())
		self.edit = False

	def next_song(self):
		self.prevSong = copy.copy(self.curSong)
		self.curSong = copy.copy(self.nextSong)
		self.finish = False
		self.playing = True
		self.skipped = 0
		# select song different with prevSong
		self.select_nextSong()
		thrFetchSong(self.curSong['url'])
	
	def finish_song(self):
		self.skipped += 1 #missing 1s KEKW	
		self.finish = True
		self.playing = False
	
	def set_mixer(self, skip=False):
		# when use cmd 'skip', download next song
		if skip:
			downloadAudio(self.curSong)

		mp3 = getPathMp3(self.curSong['url'])
		# unlocad() can only use in pygame==2.0.0
		# but not released => temp use pygame==2.0.0.dev6
		self.mixer.unload()
		# return before load if not exists
		if not path.exists(mp3):
			return

		print(mp3)
		self.mixer.load(mp3)
		self.mixer.set_volume(readJson(JSON_MCONFIG_PATH)['volume'])
		self.mixer.play()
		# pre-print, (lazy way)
		if not skip:
			print('\n\n'+self.__str__()+'\n$ ', end='')

	def down_next_song(self):
		total = calcTime(self.curSong['time'])
		# played 70% of the song, download next song
		if 'downloaded' not in self.nextSong and self.mixer_get_pos() >= total * 0.7:
			self.nextSong['downloaded'] = True
			thrDownload(self.nextSong)
			
	def __str__(self):
		status = 'Loading'
		if self.playing:
			status = 'Playing'
		elif self.pause:
			status = 'Pause'
		elif self.finish:
			status = 'Finished'
		# format will be <current play time>/<total>
		# format time will be mm:ss
		time = formatSeconds(self.mixer_get_pos())+'/'+self.curSong['time']
		# title - channel name
		curSong = self.curSong['title']+' - '+self.curSong['channel']
		return status+' '+time+': '+ curSong
	
	def pause_song(self):
		self.pause = True
		self.playing = False
		self.mixer.pause()
	
	def unpause_song(self):
		self.pause = False
		self.playing = True
		self.mixer.unpause()  

	def select_nextSong(self):
		if self.curSong == {}:
			return
		# select song different with prevSong
		for song in readJson():
			if self.prevSong == {} or song['url'] != self.prevSong['url']:
				self.nextSong = song
				break
	
	def reset_all(self):
		self.playing = False
		self.finish = False
		self.pause = False
		self.edit = False
		self.mixer = None
		self.skipped = 0
		self.curSong = {}
		self.nextSong = {}
		self.prevSong = {}