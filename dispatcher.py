import urwid, urwid.curses_display, gobject
import traceback, os
import playlist, browse, player, repo_manager

class Dispatcher(object):
	
	PL = 1
	OP = 2
	
	PALETTE = [
				('border', 'yellow', 'black', 'standout')
				]

	UNSUPPORTED_KEYS_MAP = {
	"8": "shift up", "2": "shift down", 
	"7": "meta up", "1": "meta down", 
	"4": "shift left", "6": "shift right" } 
	
	def __init__(self):
		self.error = []
		self.playlist = playlist.PlayList()
		self.player = player.Player(self.playlist)
		last_visited_dir = None
		try:
			self.playlist.walker, self.playlist.items, self.playlist.old_items, self.player.media.volume, last_visited_dir = repo_manager.load(self.playlist.walker, self.playlist.items, self.playlist.old_items)
			ids = [item.id for item in self.playlist.items]
			if ids: self.playlist.current_item_id = max(ids)
			self.player.volume.set_completion(self.player.media.volume)
		except Exception, e:
					self.error.append(str(traceback.format_exc()))
		self.browser = browse.DirectoryBrowser(last_visited_dir)
		self.focused_track = None
		self.playing_track = None
		self.event_processor = gobject.MainLoop()
		gobject.threads_init()
		self.event_context = self.event_processor.get_context()

	def main(self):
			self.ui = urwid.curses_display.Screen()
			self.ui.register_palette(repo_manager.build_palette(playlist.PlayList.PALETTE + browse.DirectoryBrowser.palette + Dispatcher.PALETTE + player.Player.PALETTE))
			self.ui.run_wrapper(self.run)
			os.system("clear")
			if self.error: print "\n".join(self.error)
			
	def run(self):
		state = Dispatcher.PL
		size = self.ui.get_cols_rows()
		left_width = size[0]/2 + size[0]%2 - 1
		right_width = size[0]/2
		border_canvas = urwid.TextCanvas('|'*size[1], [[('border', 1)]]*size[1])
		while True:
			
			while self.event_context.pending(): # process some playbin events
				self.event_context.iteration(False)
				
			keys = self.ui.get_input()
			
			if 'window resize' in keys: 
				size = self.ui.get_cols_rows()
				left_width = size[0]/2 + size[0]%2 - 1
				right_width = size[0]/2
				border_canvas = urwid.TextCanvas('|'*size[1], [[('border', 1)]]*size[1])
			elif 'f8' in keys:
				if len(self.playlist.items) != len(self.playlist.old_items):
					self.playlist.exit_filter()
				try:
					repo_manager.save(self.playlist.walker, self.playlist.items, self.playlist.old_items, self.player.media.volume, browse.last_visited_dir)
				except Exception, e:
					self.error.append(str(traceback.format_exc()))
				break
			elif 'ctrl o' in keys: 
				state = Dispatcher.OP
			elif 'esc' in keys and state == Dispatcher.OP: 
				state = Dispatcher.PL
				keys.remove('esc')
				
			canvases = []
			
			if state == Dispatcher.OP:
				br_canvas = self.browser.action(keys, (left_width,  size[1]))	
				canvases.append((br_canvas, (0, 0), False, left_width))
			elif state == Dispatcher.PL:
				p_keys = [] if self.playlist.pile_in_focus == 1 else keys
				p_canvas = self.player.action(p_keys, (left_width,  size[1]))	
				canvases.append((p_canvas, (0, 0), False, left_width))
				
			canvases.append((border_canvas, (0, left_width), False, 1))
			
			for data in browse.add_files_list: self.playlist.add_item(*data)
			browse.add_files_list = []
			
			pl_keys = [] if state == Dispatcher.OP else keys
			if self.playlist.pile_in_focus == 0:
				pl_keys = [Dispatcher.UNSUPPORTED_KEYS_MAP.get(key, key) for key in pl_keys]
			pl_canvas = self.playlist.action(pl_keys, (right_width, size[1]))
			
			canvases.append((pl_canvas, (0, left_width+1), False, right_width))
			
			canvas = urwid.CanvasJoin(canvases)
			
			self.ui.draw_screen(size,  canvas)
			
if __name__ == "__main__":
	Dispatcher().main()
