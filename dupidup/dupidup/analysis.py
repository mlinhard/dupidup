from os.path import dirname
import os
import hashlib
import asyncio


class DupItemRow:

    def __init__(self, files, size, hash_value):
        self.files = files
        self.size = size
        self.hash_value = hash_value

    def get_num_files(self):
        return sum([len(a) for a in self.files])

    def get_boxrow_height(self):
        return max(len(file_list) for file_list in self.files)

    def idx_range(self):
        return range(self.get_boxrow_height())

    def get_line(self, idx):
        line = []
        for file_list in self.files:
            if idx < len(file_list):
                line.append(file_list[idx])
            else:
                line.append(None)
        return tuple(line)


def _get_dirs(path_list):
    dir_list = list({ dirname(path) for path in path_list })
    dir_list.sort()
    return tuple(dir_list)


def _get_row(dirs, path_list, hash_value, size):
    files = {dir1: [] for dir1 in dirs}
    for path in path_list:
        pdir, pfile = os.path.split(path)
        files[pdir].append(pfile)
    return DupItemRow([ files[pdir] for pdir in dirs], size, hash_value)


class DupItem:

    def __init__(self, dirs, rows):
        self.dirs = dirs
        self.rows = rows

    def get_box_height(self):
        return sum(row.get_boxrow_height() for row in self.rows)

    def append(self, path_list, hash_value, size):
        if self.dirs == _get_dirs(path_list):
            self.rows.append(_get_row(self.dirs, path_list, hash_value, size))
            return True
        else:
            return False

    @staticmethod
    def create(path_list, hash_value, size):
        dirs = _get_dirs(path_list)
        return DupItem(dirs, [_get_row(dirs, path_list, hash_value, size)])


def shifts(lst):
    return [ lst[i:] + lst[:i] for i in range(len(lst)) ]


def is_ignored(path, ignored_prefixes):
    for ignored_prefix in ignored_prefixes:
        if path.startswith(ignored_prefix):
            return True
    return False


def remove_ignored(path_list, ignored_prefixes):
    return [ path for path in path_list if not is_ignored(path, ignored_prefixes)]


def _hash_bytestr_iter(bytesiter, hasher):
    for block in bytesiter:
        hasher.update(block)
    return hasher.hexdigest()


def _file_as_blockiter(afile, blocksize=1024 * 1024):
    with afile:
        block = afile.read(blocksize)
        while len(block) > 0:
            yield block
            block = afile.read(blocksize)


def get_hash(path):
    return _hash_bytestr_iter(_file_as_blockiter(open(path, 'rb')), hashlib.md5())


class FileHashProcessor:

    def __init__(self, file_walk, sizes, hash_file, callback, log):
        self._file_walk = file_walk
        self._sizes = sizes
        self._hash_file = hash_file
        self._callback = callback
        self._log = log

    async def _read_file(self):
        hashes = []
        with open(self._hash_file, "r") as f:
            line = f.readline()
            while line:
                hashes.append(line.strip())
                line = f.readline()
                await asyncio.sleep(0)
        return hashes

    def _check_last(self, hashes, n):
        finished = len(hashes)
        for i in range(finished - n, finished):
            file_i = self._file_walk[i]
            hash_i = get_hash(file_i)
            if hash_i != hashes[i]:
                raise Exception(f"File {file_i} hash is {hash_i}, not {hashes[i]}")

    async def process(self):
        try:
            hashes = []
            if os.path.exists(self._hash_file):
                hashes = await self._read_file()
                self._check_last(hashes, 3)

            total_files = len(self._file_walk)
            file_count = len(hashes)
            byte_count = sum(self._sizes[:file_count])

            if file_count < total_files:
                with open(self._hash_file, "a+") as f:
                    for file_path in self._file_walk.tail(file_count):
                        hashval = get_hash(file_path)
                        hashes.append(hashval)
                        f.write(hashval)
                        f.write("\n")
                        f.flush()
                        byte_count += self._sizes[file_count]
                        file_count += 1
                        await self._callback.on_hashing_progress(file_count, byte_count)
                        await asyncio.sleep(0)

            await self._callback.on_hashing_finished(hashes)
        except Exception as e:
            await self._callback.on_task_error("hashing", e)


class DuplicateAnalysis:

    def __init__(self, items):
        self.items = items

    def get_duplicated_bytes(self):
        duplicated_bytes = 0
        for item in self.items:
            for row in item.rows:
                duplicated_bytes += row.size * (row.get_num_files() - 1)
        return duplicated_bytes

    def max_columns(self):
        return max(len(item.dirs) for item in self.items)

    @staticmethod
    async def create(hashes, file_walk, sizes, ignored_folders, callback):
        if len(hashes) != len(file_walk) or len(hashes) != len(sizes):
            raise Exception("Integrity error: number of hashes must be equal to number of files and number of file sizes")
        paths_by_hash = {}
        dups_size_by_hash = {}

        for i, path, hashval, size in zip(range(len(sizes)), file_walk, hashes, sizes):
            if hashval in paths_by_hash:
                prevsize = dups_size_by_hash.get(hashval)
                if prevsize == None:
                    dups_size_by_hash[hashval] = size
                else:
                    if size != prevsize:
                        raise Exception(f"Hash collision: file {path} size {size} has same hash {hashval} as files {repr(paths_by_hash[hashval])} size {prevsize}")
                paths_by_hash[hashval].append(path)
            else:
                paths_by_hash[hashval] = [path]
            if i % 1000 == 0:
                await callback.on_analysis_progress(i)
                await asyncio.sleep(0)

        # filter ignored folders
        duplists = []
        i = 0
        for duphash, size in dups_size_by_hash.items():
            dup_paths = paths_by_hash[duphash]
            non_ignored_paths = remove_ignored(dup_paths, ignored_folders)
            if len(non_ignored_paths) > 1:
                for dupshift in shifts(non_ignored_paths):
                    duplists.append((dupshift, duphash, size))
            i += 1
            if i % 1000 == 0:
                await asyncio.sleep(0)

        await asyncio.sleep(0)
        duplists.sort(key=lambda l: l[0][0])
        await asyncio.sleep(0)

        used_hashes = set()
        finlist = []
        prev_item = None

        for path_list, hash_value, size in duplists:
            if not hash_value in used_hashes:
                if prev_item == None or not prev_item.append(path_list, hash_value, size):
                    prev_item = DupItem.create(path_list, hash_value, size)
                    finlist.append(prev_item)
                used_hashes.add(hash_value)
        await asyncio.sleep(0)

        await callback.on_analysis_finished(DuplicateAnalysis(finlist))
