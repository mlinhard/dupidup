'''
Efficient representation of a saved os.walk traversal on a filesystem that is possibly slow and inefficient to pass multiple times.
'''
import os
import stat
import asyncio


class DirListing:

    def __init__(self, folder, files):
        self.folder = folder
        self.files = files

    def __str__(self):
        return self.folder + "".join(['\n  ' + f for f in self.files])

    def __eq__(self, other):
        return self.folder == other.folder and self.files == other.files


class NoopProgressCallback:

    async def on_filewalk_progress(self, folder_count, file_count):
        pass

    async def on_filewalk_loading(self, walk_file):
        pass

    async def on_filewalk_saving(self, walk_file):
        pass

    async def on_filewalk_finished(self, file_walk):
        pass

    async def on_task_error(self, task, error):
        pass


noop_progress_callback = NoopProgressCallback()


class FileWalkIterator(object):

    def __init__(self, walk, idx_dir_listing, idx_file, idx_walk):
        self._walk = walk
        self._idx_dir_listing = idx_dir_listing
        self._idx_file = idx_file
        self._idx_walk = idx_walk

    def __next__(self):
        if self._idx_dir_listing < len(self._walk._dir_listings):
            listing = self._walk._dir_listings[self._idx_dir_listing]
            if self._idx_file < len(listing.files):
                file = os.path.join(listing.folder, listing.files[self._idx_file])
                self._idx_file += 1
                return file
            else:
                self._idx_dir_listing += 1
                self._idx_file = 0
                return self.__next__()
        else:
            raise StopIteration()

    def __iter__(self):
        return self


class FileWalk(object):

    def __init__(self):
        self._size = 0
        self._dir_listings = []

    def folder_count(self):
        return len(self._dir_listings)

    def __len__(self):
        return self._size

    def tail(self, skip_count):
        i, j = self._compute_idxs(skip_count)
        return FileWalkIterator(self, i, j, skip_count)

    def __iter__(self):
        return FileWalkIterator(self, 0, 0, 0)

    def __getitem__(self, key):
        i, j = self._compute_idxs(key)
        l = self._dir_listings[i]
        return os.path.join(l.folder, l.files[j])

    def _compute_idxs(self, global_idx):
        if global_idx >= 0:
            listing_idx = 0
            while listing_idx < len(self._dir_listings) and global_idx >= len(self._dir_listings[listing_idx].files):
                global_idx -= len(self._dir_listings[listing_idx].files)
                listing_idx += 1
            if listing_idx < len(self._dir_listings):
                return listing_idx, global_idx
            else:
                raise IndexError("Index out of range")
        else:
            listing_idx = len(self._dir_listings) - 1
            while listing_idx >= 0 and -global_idx > len(self._dir_listings[listing_idx].files):
                global_idx += len(self._dir_listings[listing_idx].files)
                listing_idx -= 1
            if listing_idx >= 0:
                return listing_idx, global_idx
            else:
                raise IndexError("Index out of range")

    def __str__(self):
        return "\n".join([str(dir_listing) for dir_listing in self._dir_listings])

    def __repr__(self):
        return f"FileWalk({self._size} files, {len(self._dir_listings)} folders)"

    def add_directory(self, folder, files):
        if folder[0] != "/":
            raise Exception(f'Wrong folder name: {folder}')
        for file in files:
            if file[0] == "/":
                raise Exception(f'Wrong file name: {file}')
        self._dir_listings.append(DirListing(folder=folder, files=files))
        self._size += len(files)

    def __eq__(self, other):
        return self._dir_listings == other._dir_listings

    async def save_to(self, path):
        with open(path, "w") as w:
            for dir_listing in self._dir_listings:
                w.write(dir_listing.folder)
                w.write("\n")
                for file in dir_listing.files:
                    w.write(file)
                    w.write("\n")
                await asyncio.sleep(0)
            w.flush()

    async def load_from(self, path):
        with open(path, "r") as r:
            current_dir = None
            current_files = []
            for line in r.readlines():
                path = line[:-1]
                if path[0] == "/":
                    if current_dir != None:
                        self.add_directory(current_dir, current_files)
                    current_dir = path
                    current_files = []
                else:
                    current_files.append(path)
                await asyncio.sleep(0)
            if current_dir != None:
                self.add_directory(current_dir, current_files)

    @staticmethod
    async def from_file(path):
        file_walk = FileWalk()
        await file_walk.load_from(path)
        return file_walk

    @staticmethod
    async def from_walk(*roots, callback=noop_progress_callback):
        file_walk = FileWalk()
        for root in roots:
            for folder, _, files in os.walk(root, True, None, False):
                file_walk.add_directory(folder, files)
                await callback.on_filewalk_progress(len(file_walk._dir_listings), len(file_walk))
                await asyncio.sleep(0)

        return file_walk


class FileWalkProcessor:

    def __init__(self, folders, walk_file, callback, log):
        self._folders = folders
        self._walk_file = walk_file
        self._callback = callback
        self._log = log

    async def process(self):
        try:
            self._log.debug("File scanning started")
            file_walk = None
            if os.path.exists(self._walk_file):
                await self._callback.on_filewalk_loading(self._walk_file)
                file_walk = await FileWalk.from_file(self._walk_file)
            else:
                if len(self._folders) == 0:
                    raise Exception(f"At least one root folder must be given if walk file {self._walk_file} is not present")
                file_walk = await FileWalk.from_walk(*self._folders, callback=self._callback)
                await self._callback.on_filewalk_saving(self._walk_file)
                await file_walk.save_to(self._walk_file)

            await self._callback.on_filewalk_finished(file_walk)
            self._log.debug("File scanning finished")
        except Exception as e:
            await self._callback.on_task_error("file walk", e)


def get_size(path):
    stat_record = os.stat(path)
    return stat_record[stat.ST_SIZE]


class FileSizeProcessor:

    def __init__(self, file_walk, size_file, callback, log):
        self._file_walk = file_walk
        self._size_file = size_file
        self._callback = callback
        self._log = log

    async def _read_file(self):
        sizes = []
        with open(self._size_file, "r") as f:
            line = f.readline()
            while line:
                sizes.append(int(line.strip()))
                line = f.readline()
                await asyncio.sleep(0)
        return sizes

    def _check_last(self, sizes, n):
        finished = len(sizes)
        for i in range(finished - n, finished):
            file_i = self._file_walk[i]
            size_i = get_size(file_i)
            if size_i != sizes[i]:
                raise Exception(f"File {i} {file_i} size is {size_i}, not {sizes[i]}")

    async def process(self):
        try:
            sizes = []
            if os.path.exists(self._size_file):
                sizes = await self._read_file()
                self._check_last(sizes, 3)

            total_files = len(self._file_walk)
            file_count = len(sizes)
            byte_count = sum(sizes)

            if file_count < total_files:
                with open(self._size_file, "a+") as f:
                    for file_path in self._file_walk.tail(file_count):
                        size = get_size(file_path)
                        sizes.append(size)
                        f.write(str(size))
                        f.write("\n")
                        f.flush()
                        file_count += 1
                        byte_count += size
                        await self._callback.on_filesize_progress(file_count, byte_count)
                        if self._callback.terminating():
                            self._log.debug("Terminating file size processor due to application termination")
                            break
                        await asyncio.sleep(0)

            await self._callback.on_filesize_finished(sizes, byte_count)
        except Exception as e:
            await self._callback.on_task_error("size computation", e)

