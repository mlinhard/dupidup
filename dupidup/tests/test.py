from dupidup.filewalk import FileWalk, get_size
import unittest
import tempfile
import os
from os.path import dirname
import asyncio
from dupidup.analysis import get_hash


class TestFileWalk(unittest.TestCase):

    def test_filewalk_tail(self):
        f = self._create_test_firewalk()
        self.assertEquals([
            "/home/u/b.txt",
            "/home/u/Documents/c.txt" ,
            "/home/u/Documents/d.txt"],
            [a for a in f.tail(1)])
        self.assertEquals([
            "/home/u/Documents/c.txt" ,
            "/home/u/Documents/d.txt"],
            [a for a in f.tail(2)])
        self.assertEquals(["/home/u/Documents/d.txt"], [a for a in f.tail(3)])

    def test_metadata_extractor(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            hello_file = os.path.join(tmpdirname, "hello.txt")
            self._create_file(hello_file, "Hello")
            hash_value = get_hash(hello_file)
            self.assertEqual("8b1a9953c4611296a827abf8c47804d7", hash_value)
            file_size = get_size(hello_file)
            self.assertEqual(5, file_size)

    def _create_test_firewalk(self):
        f = FileWalk()
        f.add_directory("/home/u", [ "a.txt", "b.txt"])
        f.add_directory("/home/u/Documents", [ "c.txt", "d.txt"])
        return f

    def _create_file(self, path, content):
        os.makedirs(dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)

    def _create_test_directory(self, tmpdir):
        self._create_file(os.path.join(tmpdir, "a.txt"), "A")
        self._create_file(os.path.join(tmpdir, "b.txt"), "B")
        self._create_file(os.path.join(tmpdir, "c.txt"), "C")
        self._create_file(os.path.join(tmpdir, "d", "d.txt"), "D")
        self._create_file(os.path.join(tmpdir, "d", "e.txt"), "B")
        self._create_file(os.path.join(tmpdir, "d", "f.txt"), "C")
        self._create_file(os.path.join(tmpdir, "f", "g.txt"), "G")
        self._create_file(os.path.join(tmpdir, "f", "sub", "h.txt"), "H")
        self._create_file(os.path.join(tmpdir, "f", "i.txt"), "D")

    def test_filewalk_add_constraints(self):
        f = FileWalk()
        with self.assertRaises(Exception) as _:
            f.add_directory("a", ["a.txt"])
        with self.assertRaises(Exception) as _:
            f.add_directory("/a", ["/a.txt"])

    def test_filewalk_string(self):
        f = self._create_test_firewalk()
        self.assertEqual(str(f), """/home/u
  a.txt
  b.txt
/home/u/Documents
  c.txt
  d.txt""")
        
    def test_filewalk_item_retrieval(self):
        f = self._create_test_firewalk()
        self.assertEquals(len(f), 4)
        self.assertEquals(f[0], "/home/u/a.txt")
        self.assertEquals(f[1], "/home/u/b.txt")
        self.assertEquals(f[2], "/home/u/Documents/c.txt")
        self.assertEquals(f[3], "/home/u/Documents/d.txt")
        with self.assertRaises(IndexError) as _:
            f[4]

        self.assertEquals(f[-1], "/home/u/Documents/d.txt")
        self.assertEquals(f[-2], "/home/u/Documents/c.txt")
        self.assertEquals(f[-3], "/home/u/b.txt")
        self.assertEquals(f[-4], "/home/u/a.txt")
        with self.assertRaises(IndexError) as _:
            f[-5]

    def test_filewalk_iteration(self):
        f = [file for file in self._create_test_firewalk()]
        self.assertEquals(len(f), 4)
        self.assertEquals(f[0], "/home/u/a.txt")
        self.assertEquals(f[1], "/home/u/b.txt")
        self.assertEquals(f[2], "/home/u/Documents/c.txt")
        self.assertEquals(f[3], "/home/u/Documents/d.txt")
        with self.assertRaises(IndexError) as _:
            f[4]
        
    def test_filewalk_real_dir(self):
        with tempfile.TemporaryDirectory() as tmpdirname:

            async def async_test():
                self._create_test_directory(tmpdirname)
                f = await FileWalk.from_walk(tmpdirname)
                self.assertEquals(len(f), 9)
                self.assertTrue(os.path.join(tmpdirname, "f", "sub", "h.txt") in f)
                self.assertTrue(os.path.join(tmpdirname, "a.txt") in f)
                await f.save_to(os.path.join(tmpdirname, "file_walk.txt"))
                f2 = await FileWalk.from_file(os.path.join(tmpdirname, "file_walk.txt"))
                self.assertEquals(f, f2)

            asyncio.run(async_test())


if __name__ == '__main__':
    unittest.main()
