import audiere_gst as audiere
from mutagen.easyid3 import EasyID3

class Media(object):
	
	STATE_STOP = 1
	STATE_PLAY = 2
	STATE_PAUSE = 3
	
	def __init__(self):
		self.dev = audiere.open_device()
		self.media_path = None
		self.media_stream = None
		self.id3 = None
		self.time_last = 0
		self.volume = 50
		self.state = Media.STATE_STOP
		
	def __setattr__(self, name, value):
		if name == 'volume' and self.media_stream: 
			self.media_stream.volume = value*0.01
		self.__dict__[name] = value
		
	def set_media(self, path):
		self.media_path = path
		self.media_stream = self.dev.open_file(self.media_path, 1)
		self.media_stream.volume = self.volume*0.01
		try:
			self.id3 = EasyID3(self.media_path)
		except:
			self.id3= {}
		
	def play(self, path=None):
		if path: self.set_media(path)	
		if self.media_stream:
			self.media_stream.play()
			self.state = Media.STATE_PLAY
		
	def pause(self):
		if self.media_stream: 
			self.media_stream.pause()
			self.state = Media.STATE_PAUSE

	def stop(self):
		if self.media_stream: 
			self.media_stream.stop()
			self.state = Media.STATE_STOP
			
	def play_stop(self, path=None):
		if self.state == Media.STATE_PLAY: self.stop()
		else: self.play(path)
		
	def play_pause(self, path=None):
		if self.state == Media.STATE_PLAY: self.pause()
		else: 
			if self.media_stream: self.play()
			else: self.play(path)
			
	def current_time(self):
		if self.media_stream:
			times = self.media_stream.timing()
			if times[0] != audiere.NoneTime and times[1] != audiere.NoneTime:
				self.time_last = times[0]
				return times
			elif times[0] == audiere.NoneTime and times[1] != audiere.NoneTime:
				if self.time_last < 0: self.time_last = 0
				elif self.time_last > times[1]: self.time_last = times[1]
				return (self.time_last, times[1])
		return (0, 0)
			
	def move_cursor(self, offset):
		if self.media_stream and not self.media_stream.streamed:
			times = self.media_stream.timing()
			self.time_last += offset
			if times[0] + offset < 0:
				new_time = 0.001
			elif times[0] + offset > times[1]:
				new_time = times[1]-0.001
			else:
				new_time = times[0] + offset
			
			self.media_stream.seek_to_location(new_time)

