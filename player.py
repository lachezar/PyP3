import urwid, urwid.curses_display
import media

class Player(object):
	
	PALETTE = [
				('tag', 'yellow', 'black', 'standout'),
				('tag_data', 'white', 'black', 'standout'),
				('custom_tag_title', 'light blue', 'black', 'standout'),
				('custom_tag_data', 'white', 'black', 'standout'),
				('volume_title', 'light cyan', 'black', 'standout'),
				('volume_uncomplete', 'white', 'black', 'standout'),
				('volume_complete', 'white', 'dark magenta', 'standout'),
				('timer_title', 'light green', 'black', 'standout'),
				('timer_data', 'light green', 'black', 'standout')
				]

	VOLUME_TXT = " Volume: "
	
	def __init__(self, playlist):
		self.current_track = urwid.Text("") 
		self.current_track.set_text(self.get_formated_artist_title("", ""))
		self.track_details = urwid.Text("") 
		self.timing = urwid.Text("") 
		self.space = urwid.Text("") 
		self.volume_title = urwid.Text(('volume_title', Player.VOLUME_TXT))
		self.last_size = (0, 0)
		self.playlist = playlist
		self.playing_track = None
		self.last_playing_position = 0
		self.media = media.Media()
		self.volume = urwid.ProgressBar('volume_uncomplete', 'volume_complete', self.media.volume)
		
	def action(self, keys, size):
		size = list(size)
		if self.last_size != size: 
			self.__setup_pile(size)
			self.last_size = size
			
		if not self.playlist.is_filter_mode():
			if 'x' in keys or (self.playlist.pile_in_focus == 0 and 'enter' in keys):
				self.change_track(*self.playlist.listbox.get_focus())
			elif 'z' in keys:
				self.prev_track()
			elif 'b' in keys:
				self.next_track()
			elif 'v' in keys:
				self.media.stop()
			elif 'c' in keys:
				if self.playing_track: self.media.play_pause(self.playing_track[0].path)
			elif 'shift right' in keys and self.media.media_stream and self.media.media_stream.playing:
				self.media.move_cursor(5)
			elif 'shift left' in keys and self.media.media_stream and self.media.media_stream.playing:
				self.media.move_cursor(-5)
		
		if '+' in keys and self.media.volume < 100:
			self.media.volume += 5
			self.volume.set_completion(self.media.volume)
		elif '-' in keys and self.media.volume > 0:
			self.media.volume -= 5
			self.volume.set_completion(self.media.volume)
			
		times = self.media.current_time()
		self.timing.set_text([('timer_title', " "+("", "Stopped ", "Playing ", "Paused  ")[self.media.state]), ('timer_data', self.time_format(times[0]) + " / " + self.time_format(times[1]))])
		
		if self.media.state == media.Media.STATE_PLAY and self.media.media_stream and not self.media.media_stream.playing and not keys and len(self.playlist.walker):
			self.next_track()
			
		canvas = self.pile.render((size[0],),  focus=True)
		return canvas

	def __setup_pile(self,  size):
		if not hasattr(self,  'pile'): self.pile_in_focus = 0
		self.pile = urwid.Pile([
							self.space,
							urwid.Columns([('fixed', len(Player.VOLUME_TXT), self.volume_title), ('weight', 12, self.volume)]),
							self.space,
							self.current_track,
							self.space,
							self.timing,
							self.space,
							self.track_details
							])

	def change_track(self, widget, pos):
		if self.playing_track is None or self.playing_track[0].id != widget.id:
			if self.playing_track:
				w_pos = None
				for p, w in enumerate(self.playlist.walker):
					if w.id == self.playing_track[0].id:
						w_pos = p
						break
				if w_pos is not None:
					self.last_playing_position = w_pos
					self.playlist.walker[w_pos] = urwid.AttrWrap(self.playing_track[0], None)
					self.playing_track[0].set_text(self.playing_track[0].get_text()[0])
			self.playing_track = (widget, pos)
			self.playlist.walker[self.playing_track[1]] = urwid.AttrWrap(self.playing_track[0], 'playing')
		try:
			self.media.play(self.playing_track[0].path)
		except:
			self.next_track()
		self.update_track_data()

	def __find_item_position(self, wanted_item, def_pos):
		for i, item in enumerate(self.playlist.walker):
			if item.id == wanted_item.id:
				return i
		return def_pos

	def next_track(self):
		if self.playing_track: 
			if self.playlist.old_items.get(self.playing_track[0].id): 
				pos = (self.__find_item_position(*self.playing_track) + 1) % len(self.playlist.walker)
			else:
				pos = (self.last_playing_position+1) % len(self.playlist.walker)
			self.change_track(self.playlist.walker[pos], pos)
		
	def prev_track(self):
		if self.playing_track:
			if self.playlist.old_items.get(self.playing_track[0].id): 
				pos = (len(self.playlist.walker) + self.__find_item_position(*self.playing_track) - 1) % len(self.playlist.walker)
			else:
				pos = (self.last_playing_position+1) % len(self.playlist.walker)
			self.change_track(self.playlist.walker[pos], pos)
			
	def get_artist_title(self):
		if self.media.id3.get('title') and len(self.media.id3.get('title')) > 0:
			title = self.media.id3.get('title')[0]
		else:
			title = self.playing_track[0].title
		if self.media.id3.get('artist') and len(self.media.id3.get('artist')) > 0:
			artist = self.media.id3.get('artist')[0]
		else:
			artist = ""
		return (artist, title)
		
	def get_formated_artist_title(self, artist, title):
		return [('tag', " Track:\n"), ('tag_data', str("" if not title else "   "+ title) +"\n"), 
		        ('tag', " Artist:\n"), ('tag_data', str("" if not artist else "   "+ artist) )]

	def get_id3_data(self):
		if self.media.id3:
			text_elements = []
			for k, v in self.media.id3.items():
				if k not in ('title', 'artist'):
					text_elements.append(('custom_tag_title', " "+k[0].upper()+k[1:]+": "))
					text_elements.append(('custom_tag_data', str(v[0])+"\n"))
			return text_elements
		else:
			return []
				
	def update_track_data(self):
		if self.playing_track: 
			self.current_track.set_text(self.get_formated_artist_title(*self.get_artist_title()))
			self.track_details.set_text(self.get_id3_data())
			
	def time_format(self, time):
		return str(time / 60) + ":" + "%02d" % (time % 60)
			
