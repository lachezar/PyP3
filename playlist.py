import urwid, urwid.curses_display
from mutagen.easyid3 import EasyID3
import os

class PlayList(object):
	
	PALETTE = [('header', 'light cyan', 'dark blue', 'standout'),  
						('reveal focus', 'black', 'brown', 'standout'),
						('playing', 'white', 'black', 'standout'),
						('selected', 'white', 'dark red', 'standout'),
						('filter_edit', 'yellow', 'black', 'standout')
						]
	
	def __init__(self):
		self.items = [] 
		self.current_item_id = 0
		self.item_focus = 0
		self.old_items = dict() 
		self.walker = urwid.SimpleListWalker(self.items)
		self.listbox = urwid.ListBox(self.walker)
		self.header_text = urwid.Text("...")
		header = urwid.AttrWrap(self.header_text, 'header')
		self.top = urwid.Frame(self.listbox, header)
		self.last_keys = []
		self.filter_edit = urwid.Edit(('filter_edit', "Filter: "),  wrap='clip')
		self.last_size = (0,  0)
		self.pile_in_focus = None
		self.last_played_track_position = 0

	def main(self):
		self.ui = urwid.curses_display.Screen()
		self.ui.register_palette(PlayList.PALETTE)
		self.ui.run_wrapper(self.run)
	
	def action(self, keys, size):
		size = list(size)
		if self.last_size != size: 
			self.__setup_pile(size)
			self.last_size = size
		rows = size[1]-2
		
		pos = self.listbox.get_focus()[1] or 0
		
		if "tab" in keys: 
			self.pile_in_focus = (self.pile_in_focus+1)%2
			self.pile.set_focus(self.pile_in_focus)
			
		if self.pile_in_focus == 0:			
			if "ctrl a" in keys:
				for item in self.items: item.set_attr("selected")
			elif ">" in keys:
				self.__do_select(len(self.items))
				keys.append("end")
			elif "<" in keys:
				self.__do_select(-1)
				keys.append("home")
			elif "." in keys:
				self.__do_select(min(pos+rows, len(self.items)))
				keys.append("page down")
			elif "," in keys:
				self.__do_select(max(pos-rows, -1))
				keys.append("page up")
			elif "shift down" in keys and pos < len(self.items)-1: 
				keys.extend((" ",  "down"))
				if "shift down" not in self.last_keys:  self.__do_select()
			elif "shift up" in keys and pos > 0: 
				keys.extend((" ",  "up"))
				if "shift up" not in self.last_keys:  self.__do_select()
			elif "meta down" in keys and pos < len(self.items)-1: 
				keys.append("down")
				self.items[pos].id,  self.items[pos+1].id = self.items[pos+1].id,  self.items[pos].id
				self.items[pos],  self.items[pos+1] = self.items[pos+1],  self.items[pos]
				self.walker[pos],  self.walker[pos+1] = self.walker[pos+1],  self.walker[pos]
				self.old_items[self.items[pos].id],  self.old_items[self.items[pos+1].id] = self.old_items[self.items[pos+1].id],  self.old_items[self.items[pos].id]
			elif "meta up" in keys and pos > 0: 
				keys.append("up")
				self.items[pos].id,  self.items[pos-1].id = self.items[pos-1].id,  self.items[pos].id
				self.items[pos],  self.items[pos-1] = self.items[pos-1],  self.items[pos]
				self.walker[pos],  self.walker[pos-1] = self.walker[pos-1],  self.walker[pos]
				self.old_items[self.items[pos].id],  self.old_items[self.items[pos-1].id] = self.old_items[self.items[pos-1].id],  self.old_items[self.items[pos].id]
			elif "delete" in keys and self.listbox.get_focus()[1] is not None: 
				if all(map(lambda x: x.get_attr() != 'selected', self.items)):
					self.remove_item(self.listbox.get_focus()[1])
				else:
					i = 0
					while i < len(self.items):
						if self.items[i].get_attr() == 'selected':
							self.remove_item(i)
						else:
							i += 1
							
			if "home" in keys: self.listbox.set_focus(0,  coming_from='below')
			if "end" in keys: self.listbox.set_focus(len(self.items),  coming_from='above')
			if "down" in keys and pos < len(self.items)-1: self.listbox.set_focus(pos+1,  coming_from='above')
			if "up" in keys and pos > 0: self.listbox.set_focus(pos-1,  coming_from='below')
			if "page down" in keys and pos < len(self.items)-1: self.listbox.set_focus(min(pos+rows,  len(self.items)-1),  coming_from='above')
			if "page up" in keys and pos > 0: self.listbox.set_focus(max(pos-rows,  0),  coming_from='below')
			
			if " " in keys: self.__do_select()
			
			if ("j" in keys or "enter" in keys) and len(self.items) != len(self.old_items) and len(self.items) > 0:  
				keys.append("esc")
				self.item_focus = self.items[self.listbox.get_focus()[1]].id
			
			if "esc" in keys:
				if len(self.items) == len(self.old_items): 
					for item in self.items: item.set_attr(None)
				else: 
					self.exit_filter()
					
			if not self.is_filter_mode(): self.item_focus = self.items[self.listbox.get_focus()[1]].id
		
		else:
			if "enter" in keys:
				words = list(set(self.filter_edit.get_edit_text().split(' ')))
				self.items = sorted([v for i, v in self.old_items.items()],  lambda x,  y: x.id-y.id)
				del self.walker[:]
				for w in words:
					if w and w != " ": 
						wl = w.lower()
						self.items = filter(lambda x: wl in x.get_text()[0].lower(),  self.items)
				self.walker.extend(self.items)
				self.listbox.set_focus(0)
			elif "end" in keys:
				self.filter_edit.set_edit_text("")
				
			if "esc" in keys:
				self.exit_filter()
				
			for key in keys: self.filter_edit.keypress((size[0],), key)
				
		self.last_keys = list(keys)
		
		self.header_text.set_text("Song %s/%s" % (self.__get_listbox_focus()+1,  len(self.items)))
		
		canvas = self.pile.render((size[0],),  focus=True)
		return canvas
			
	def __get_listbox_focus(self):
		return -1 if self.listbox.get_focus()[1] is None else self.listbox.get_focus()[1]
			
	def __resize(self):
		size = list(self.ui.get_cols_rows())
		self.__setup_pile(size)
		return size,  size[1]-2
			
	def __setup_pile(self,  size):
		if not hasattr(self,  'pile'): self.pile_in_focus = 0
		self.pile = urwid.Pile([
							urwid.BoxAdapter(self.top,  size[1]-1),  
							self.filter_edit
							])
			
	def __do_select(self,  limit=None):
		widget,  pos = self.listbox.get_focus()
		if limit is None: limit = pos-1
		while limit != pos:
			if self.items[pos].get_attr() == 'selected':
				self.items[pos].set_attr(None)
			else:
				self.items[pos].set_attr('selected')
			pos += (limit-pos)/abs(limit-pos)
			
	def exit_filter(self):
		self.items = sorted([v for i, v in self.old_items.items()],  lambda x,  y: x.id-y.id)
		del self.walker[:]
		self.walker.extend(self.items)
		self.filter_edit.set_edit_text("")
		self.listbox.set_focus(0)
		for id, item in enumerate(self.items):
			if self.item_focus == item.id:
				self.listbox.set_focus(id)
				break
	
	def draw_screen(self, size):
		canvas = self.pile.render((size[0]/2,),  focus=True)
		self.ui.draw_screen(size, canvas)
		
	def add_item(self, path, title):
		item = urwid.AttrWrap(urwid.Text(self.get_artist_title(path)), None, 'reveal focus')
		item.title = title
		item.path = path
		self.items.append(item) 
		self.current_item_id += 1
		item.id = self.current_item_id
		self.old_items[self.current_item_id] = item
		self.walker.append(item)
		self.listbox.set_focus(len(self.items))
		
	def remove_item(self, pos):
		del self.old_items[self.items[pos].id]
		del self.items[pos]
		del self.walker[pos]
		
	def is_filter_mode(self):
		return not (self.items and len(self.items) == len(self.old_items))
		
	def get_artist_title(self, path):
		id3 = None
		try:
			id3 = EasyID3(path)
		except:
			pass
		
		if id3 and id3.get('title') and len(id3.get('title')) > 0:
			title = id3.get('title')[0]
		else:
			title = os.path.basename(path)
		if id3 and id3.get('artist') and len(id3.get('artist')) > 0:
			artist = id3.get('artist')[0]
		else:
			artist = ""
		return (artist + " - " + title) if artist else title
	
