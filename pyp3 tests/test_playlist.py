import unittest
import playlist

class TestPlaylist(unittest.TestCase):
	
	def setUp(self):
		self.p = playlist.PlayList()
		self.p.add_item("./royksopp - Eple.mp3", "1")
		self.p.add_item("./royksopp - Eple.mp3", "2")
		self.p.add_item("./royksopp - Remind Me.mp3", "3")
	
	def test_focus(self):
		self.assertEqual(self.p._PlayList__get_listbox_focus(), len(self.p.items)-1)
		self.p.action(["down"], (10, 10))
		self.assertEqual(self.p._PlayList__get_listbox_focus(), len(self.p.items)-1)
		self.p.action(["up"], (10, 10))
		self.assertEqual(self.p._PlayList__get_listbox_focus(), len(self.p.items)-2)
		self.p.action(["home"], (10, 10))
		self.assertEqual(self.p._PlayList__get_listbox_focus(), 0)
		self.p.action(["end"], (10, 10))
		self.assertEqual(self.p._PlayList__get_listbox_focus(), len(self.p.items)-1)
		
	def test_filter_edit(self):
		self.assertEqual(self.p.pile_in_focus, None)
		self.p.action(["tab"], (10, 10))
		self.assertEqual(self.p.pile_in_focus, 1)
		self.p.action(["a"], (10, 10))
		self.p.action(["b"], (10, 10))
		self.p.action(["c"], (10, 10))
		self.p.action(["tab"], (10, 10))
		self.assertEqual(self.p.filter_edit.get_edit_text(), "abc")
		
	def test_filter_edit(self):
		self.assertEqual(len(self.p.items), 3)
		self.assertEqual(self.p.pile_in_focus, None)
		self.p.action(["tab"], (10, 10))
		self.assertEqual(self.p.pile_in_focus, 1)
		self.p.action(["m"], (10, 10))
		self.p.action(["e"], (10, 10))
		self.p.action(["enter"], (10, 10))
		self.assertEqual(len(self.p.items), 1)
		self.p.action(["end"], (10, 10))
		self.p.action(["enter"], (10, 10))
		self.assertEqual(len(self.p.items), 3)
		self.p.action(["m"], (10, 10))
		self.p.action(["p"], (10, 10))
		self.p.action(["3"], (10, 10))
		self.p.action(["enter"], (10, 10))
		self.assertEqual(len(self.p.items), 0)
		
	def test_add_item(self):
		self.p.add_item("./royksopp - Remind Me.mp3", "4")
		self.assertEqual(len(self.p.items), 4)
		self.p.remove_item(2)
		self.assertEqual(len(self.p.items), 3)
		self.assertRaises(IndexError, self.p.remove_item, 22)
		
	def tearDown(self):
		pass
