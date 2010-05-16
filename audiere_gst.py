import gst
import os, time

# A GStreamer implementation of Audiere

NoneTime = gst.CLOCK_TIME_NONE

def open_device():
		return AudiereGst()

class AudiereGst(object):

	def __init__(self):
		self.player = gst.element_factory_make("playbin", "player")
		bus = self.player.get_bus()
		bus.add_signal_watch()
		bus.connect('message', self.on_message)
		self.local = True
		self.playing = False
		self.volume = 0.5
		self.position = 0
		self.streamed= False
		self._last_position = 0
		self._last_position_mark = 0
		
	def open_file(self, uri, streamed):
		self.player.set_state(gst.STATE_NULL)
		if uri.startswith("http://"):
			self.streamed = True
		else:
			if not os.path.isfile(uri): raise os.error
			self.streamed = False
			uri = "file://" + uri
		self.player.set_property('uri', uri)
		return self
	
	def pause(self):
		self.player.set_state(gst.STATE_PAUSED)
		self.playing = False

	def play(self):
		self.player.set_state(gst.STATE_PLAYING)
		self.playing = True

	def stop(self):
		self.player.set_state(gst.STATE_NULL)
		self.playing = False	
	
	def __setattr__(self, name, value):
		if name == "volume":
			self.player.set_property("volume", value)
		self.__dict__[name] = value

	def timing(self):
		try:
			position, format = self.player.query_position(gst.FORMAT_TIME)
			position /= gst.SECOND
		except:
			position = NoneTime

		try:
			duration, format = self.player.query_duration(gst.FORMAT_TIME)
			duration /= gst.SECOND
		except:
			duration = NoneTime
			
		if position == duration and duration != NoneTime and duration != 0: self.playing = False
			
		if self.streamed and self.playing:
			now = time.time()
			if self._last_position_mark+2 < now:	 # Check whether the stream got broken, if for 2 seconds the position is remaining unchanged
				if self._last_position == position:
					self.player.set_state(gst.STATE_NULL)
					self.player.set_state(gst.STATE_PLAYING)
				self._last_position_mark = now
				self._last_position = position

		return (position, duration)

	def seek_to_location(self, location):
		if not self.streamed:
			location *= gst.SECOND
			event = self.player.seek(1.0, gst.FORMAT_TIME,
			gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
			gst.SEEK_TYPE_SET, location,
			gst.SEEK_TYPE_NONE, 0)
			
	def on_message(self, bus, message):
		if message.type == gst.MESSAGE_ERROR or message.type == gst.MESSAGE_EOS:
			self.playing = False
		
