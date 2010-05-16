import unittest
import os
import repo_manager

class TestPlaylist(unittest.TestCase):
	
	def setUp(self):
		repo_manager.PALETTE_FILE = os.path.abspath("./palette.dat")
		self.def_pal =  [
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
		
	def test_build_palette(self):
		res = repo_manager.build_palette(self.def_pal)
		self.assertEquals(res[0], ('tag', 'yellow', 'dark blue', 'standout'))
		self.assertEquals(res[1], ('tag_data', 'white', 'black', 'standout'))
		self.assertEquals(res[2], ('custom_tag_title', 'light blue', 'black', 'standout'))
		self.assertEquals(len(res), len(self.def_pal))

	def test_build_palette(self):
		repo_manager.PALETTE_FILE = "./test.dat"
		res = repo_manager.build_palette(self.def_pal)
		self.assertEquals(self.def_pal, res)

	def tearDown(self):
		pass
