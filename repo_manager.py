from __future__ import with_statement
import urwid, urwid.curses_display
import pickle

DATA_FILE = "pyp3.dat"
PALETTE_FILE = "palette.dat"

def save(walker, items, old_items, volume, last_visited_dir):
	with open(DATA_FILE, "w") as f:
		memo = []
		for item in items:
			memo.append((item.path, item.get_text()[0], item.title, item.id))
		memo.append(volume)
		memo.append(last_visited_dir)
		pickle.dump(memo, f)
	
def load(walker, items, old_items):
	with open(DATA_FILE, "r") as f:
		memo = pickle.load(f)
		if len(memo) > 2:
			for m in memo[:-2]:
				item = urwid.AttrWrap(urwid.Text(m[1]), None, 'reveal focus')
				item.title = m[2]
				item.path = m[0]
				items.append(item) 
				item.id = m[3]
				old_items[item.id] = item
				walker.append(item)
	return walker, items, old_items, memo[-2], memo[-1]
	
def build_palette(args):
	items = {}
	try:
		with open(PALETTE_FILE, "r") as f:
			for line in f.readlines()[:]:
				elements = line.split(":")
				if len(elements) == 2: 
					items[elements[0].strip()] = elements[1].strip()
	except:
		return args
	result = []
	for arg in args:
		colors = items.get(arg[0])
		if colors:
			colors_couple = colors.split(",")
			if len(colors_couple) == 2:
				foreground, background = colors_couple[0].strip(), colors_couple[1].strip()
				if urwid.curses_display._curses_colours.get(foreground) and urwid.curses_display._curses_colours[foreground][1] == 1 and \
				urwid.curses_display._curses_colours.get(background) and urwid.curses_display._curses_colours[background][1] == 0:
					result.append((arg[0], foreground, background, 'standout'))
					continue
		result.append(arg)
	return result
	
			
			
