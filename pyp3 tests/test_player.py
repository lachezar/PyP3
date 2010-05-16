import unittest
import playlist, player

class TestPlayer(unittest.TestCase):
	
	def setUp(self):
		self.pl = playlist.PlayList()
		self.p = player.Player(self.pl)
		self.pl.add_item("./royksopp - Eple.mp3", "1")
		self.pl.add_item("./royksopp - Eple.mp3", "2")
		self.pl.add_item("./royksopp - Eple.mp3", "3")
		
	def test_get_artist_title(self):
		wi = self.pl.walker[1]
		self.assertEqual(self.p._Player__find_item_position(wi, 1), 1)
		
	def test_next_track(self):
		self.p.playing_track = self.pl.listbox.get_focus()
		self.p.next_track()
		self.assertEqual(self.p.playing_track[1], 0)
		
	def test_prev_track(self):
		self.p.playing_track = self.pl.listbox.get_focus()
		self.p.prev_track()
		self.assertEqual(self.p.playing_track[1], len(self.pl.walker)-2)
		
	def test_find_item_position(self):
		w = self.pl.walker[2]
		self.pl.action(["meta up"], (10, 10))
		self.assertEqual(self.p._Player__find_item_position(w, 112), 1)
		self.pl.remove_item(1)
		self.assertEqual(self.p._Player__find_item_position(w, 112), 112)
		
	def test_action(self):
		old_v = self.p.media.volume
		self.p.action(["+"], (10, 10))
		self.assertEqual(self.p.media.volume, old_v+5)
		self.p.action(["-"], (10, 10))
		self.assertEqual(self.p.media.volume, old_v)
		for x in range(20): self.p.action(["-"], (10, 10))
		self.assertEqual(self.p.media.volume, 0)
		self.p.action(["x"], (10, 10))
		self.assertTrue(self.p.media.media_stream.playing)
		self.p.action(["c"], (10, 10))
		self.assertFalse(self.p.media.media_stream.playing)
		self.p.action(["c"], (10, 10))
		self.assertTrue(self.p.media.media_stream.playing)
		self.p.action(["v"], (10, 10))
		self.assertFalse(self.p.media.media_stream.playing)
		
	def tearDown(self):
		pass
