'''
Created on 18 Sep 2019

@author: mlinhard
'''
import unittest
from tests.testview import TestMagicWindow
from dupidup.progress import ProgressWindow
from dupidup.browser import DuplicateBrowser
from dupidup.analysis import DuplicateAnalysis, DupItem, DupItemRow


class Test(unittest.TestCase):

    def test_TestMagicWindow(self):

        win = TestMagicWindow(8, 2, 0, 0)
        self.assertEqual("        ", win.line[0])
        self.assertEqual("        ", win.line[1])
        win.put_text(0, 0, "AAAA")
        self.assertEqual("AAAA    ", win.line[0])
        self.assertEqual("        ", win.line[1])
        win.put_text(1, 0, "BBBB")
        self.assertEqual("ABBBB   ", win.line[0])
        self.assertEqual("        ", win.line[1])
        win.put_text(2, 1, "CCCC")
        self.assertEqual("ABBBB   ", win.line[0])
        self.assertEqual("  CCCC  ", win.line[1])
        win.put_text(7, 0, "D")
        self.assertEqual("ABBBB  D", win.line[0])
        self.assertEqual("  CCCC  ", win.line[1])
        win.put_text(6, 0, "EEEE")
        self.assertEqual("ABBBB EE", win.line[0])
        self.assertEqual("EECCCC  ", win.line[1])
        win.put_text(6, 1, "GGGG")
        self.assertEqual("ABBBB EE", win.line[0])
        self.assertEqual("EECCCCGG", win.line[1])

    def test_progress_window_shapes(self):
        self.assertEmptyProgressWindow(35,
"""
┌─────────────────────────────────┐
│                                 │
│                                 │
│                                 │
╞═════════╤═══════════════════════╡
│ Folders │                       │
├─────────┼───────────────────────┤
│   Files │                       │
├─────────┼───────────────────────┤
│    Size │                       │
└─────────┴───────────────────────┘
""")
        self.assertEmptyProgressWindow(70,
"""
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│                                                                    │
│                                                                    │
╞════════════════════╤═══════════════════════════════════════════════╡
│            Folders │                                               │
├────────────────────┼───────────────────────────────────────────────┤
│              Files │                                               │
├────────────────────┼───────────────────────────────────────────────┤
│               Size │                                               │
└────────────────────┴───────────────────────────────────────────────┘
""")

    def assertEmptyProgressWindow(self, width, contents):
        root_win = TestMagicWindow(width, 20, 0, 0)
        ProgressWindow(root_win)
        self.assertEqual(1, len(root_win.children))
        child_win = root_win.children[0]
        # print(child_win.contents())
        self.assertEqual(contents, "\n" + child_win.contents())

    def test_progress_window_values(self):
        root_win = TestMagicWindow(35, 20, 0, 0)
        prog_win = ProgressWindow(root_win)
        self.assertEqual(1, len(root_win.children))
        child_win = root_win.children[0]
        prog_win.set_action_msg("Bla bla")
        prog_win.set_num_files(10000)
        prog_win.set_num_folders(1000)
        prog_win.set_size(50 * 1024 * 1024)
        # print(child_win.contents())
        self.assertEqual(
"""
┌─────────────────────────────────┐
│                                 │
│             Bla bla             │
│                                 │
╞═════════╤═══════════════════════╡
│ Folders │                 1,000 │
├─────────┼───────────────────────┤
│   Files │                10,000 │
├─────────┼───────────────────────┤
│    Size │              50.0 MiB │
└─────────┴───────────────────────┘
""", "\n" + child_win.contents())
        prog_win.set_action_msg("AAAAAAAAAABBBBBBBBBBCCCCCCCCCCDDDDDDDDDD")
        self.assertEqual(
"""
┌─────────────────────────────────┐
│                                 │
│AAAAAAAAAABBBBBBBBBBCCCCCCCCCCDDD│
│                                 │
╞═════════╤═══════════════════════╡
│ Folders │                 1,000 │
├─────────┼───────────────────────┤
│   Files │                10,000 │
├─────────┼───────────────────────┤
│    Size │              50.0 MiB │
└─────────┴───────────────────────┘
""", "\n" + child_win.contents())

    def test_browser_shapes(self):
        root_win = TestMagicWindow(50, 12, 0, 0)
        item_a = DupItem(("/home/u/0",), [
            DupItemRow([["file1.txt", "file1_dup.txt"]], 9, "flabadaba0")
        ])
        item_b = DupItem(("/home/u/a", "/home/u/b"), [
            DupItemRow([["file1.txt"], ["file1.txt"]], 10, "flabadaba1"),
            DupItemRow([["file2.txt"], ["file2.txt", "file2_dup.txt"]], 12, "flabadaba2")
        ])
        item_c = DupItem(("/home/u/c", "/home/u/d"), [
            DupItemRow([["file3.txt"], ["file3.txt"]], 13, "flabadaba3"),
            DupItemRow([["file4.txt"], ["file4.txt"]], 14, "flabadaba4")
        ])
        analysis = DuplicateAnalysis([item_a, item_b, item_c])
        DuplicateBrowser(root_win, analysis)
        self.assertEqual(
"""
┌─/home/u/0─────────────┐                         
│ file1.txt             │                         
│ file1_dup.txt         │                         
├─/home/u/a─────────────┼─/home/u/b─────────────┐ 
│ file1.txt             │ file1.txt             │ 
│ file2.txt             │ file2.txt             │ 
│                       │ file2_dup.txt         │ 
├─/home/u/c─────────────┼─/home/u/d─────────────┤ 
│ file3.txt             │ file3.txt             │ 
│ file4.txt             │ file4.txt             │ 
└───────────────────────┴───────────────────────┘ 
""", "\n" + root_win.children[0].contents())

# 0         1         2         3         4
# 01234567890123456789012345678901234567890123456789
#  01234567890123456789012


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_progress_window']
    unittest.main()
