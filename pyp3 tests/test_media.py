import unittest
import media
import time, os

class TestPlaylist(unittest.TestCase):
	
	def setUp(self):
		self.mp3_path = os.path.abspath("./royksopp - Eple.mp3")
		self.m = media.Media()
		
	def test_set_media(self):
		self.m.set_media(self.mp3_path)
		self.assertTrue(self.m.id3)
		self.m.id3 = {}
		self.assertRaises(OSError, self.m.set_media, "./none.mp3")
		self.assertEquals(self.m.id3, {})
		
	def test_current_time(self):
		self.assertEquals(self.m.current_time(), (0, 0))
		self.m.set_media(self.mp3_path)
		self.assertEquals(self.m.current_time()[0], 0)
		self.m.play()
		time.sleep(1.5)
		self.assertEquals(self.m.current_time()[0], 1)
		self.assertNotEquals(self.m.current_time()[1], 0)
		
	def test_play_pause(self):
		self.m.set_media(self.mp3_path)
		
		self.m.play()
		self.assertTrue(self.m.media_stream.playing)
		self.assertEquals(self.m.state, media.Media.STATE_PLAY)
		
		self.m.play_pause()
		self.assertFalse(self.m.media_stream.playing)
		self.assertEquals(self.m.state, media.Media.STATE_PAUSE)
		
		self.m.play_pause()
		self.assertTrue(self.m.media_stream.playing)
		self.assertEquals(self.m.state, media.Media.STATE_PLAY)
		
	def test_play_stop(self):
		self.m.set_media(self.mp3_path)
		
		self.m.play()
		self.assertTrue(self.m.media_stream.playing)
		self.assertEquals(self.m.state, media.Media.STATE_PLAY)
		
		self.m.play_stop()
		self.assertFalse(self.m.media_stream.playing)
		self.assertEquals(self.m.state, media.Media.STATE_STOP)
		
		self.m.play_stop()
		self.assertTrue(self.m.media_stream.playing)
		self.assertEquals(self.m.state, media.Media.STATE_PLAY)
		
	def test_play_stop_pause(self):
		self.m.set_media(self.mp3_path)
		
		self.m.play()
		self.assertTrue(self.m.media_stream.playing)
		self.assertEquals(self.m.state, media.Media.STATE_PLAY)
		
		self.m.pause()
		self.assertFalse(self.m.media_stream.playing)
		self.assertEquals(self.m.state, media.Media.STATE_PAUSE)
		
		self.m.stop()
		self.assertFalse(self.m.media_stream.playing)
		self.assertEquals(self.m.state, media.Media.STATE_STOP)
		
		self.m.play()
		self.assertTrue(self.m.media_stream.playing)
		self.assertEquals(self.m.state, media.Media.STATE_PLAY)
		
	def tearDown(self):
		pass
