from concurrent import futures
import os

from dupidup.analysis import  DuplicateAnalysis, FileHashProcessor
from dupidup.filewalk import FileWalkProcessor, FileSizeProcessor
from magicur.app import MagicApplication, callback
from dupidup.view import RootView


class DupidupApplication(MagicApplication):

    def __init__(self, temp_datadir, root_folders, ignored_folders):
        self._temp_datadir = temp_datadir
        self._root_folders = [os.path.abspath(f) for f in root_folders]
        self._ignored_folders = ignored_folders
        if not os.path.exists(self._temp_datadir):
            os.makedirs(self._temp_datadir, exist_ok=False)
        self._walk_file = os.path.join(self._temp_datadir, "file_walk.txt")
        self._size_file = os.path.join(self._temp_datadir, "sizes.txt")
        self._hash_file = os.path.join(self._temp_datadir, "hashes.txt")
        self._executor = futures.ThreadPoolExecutor(max_workers=4)

    def init_palette(self, palette):
        palette.add_default_colors()
        palette.add_pair("lightgray black", "lightgray", "black")
        palette.add_pair("yellow blue", "yellow", "blue")
        palette.add_pair("black lightgray", "black", "lightgray")
        palette.add_pair("lightgray black", "lightgray", "black")
        palette.add_pair("white blue", "white", "blue")
        palette.add_pair("white red", "white", "red")

    def init_view(self, screen):
        self._view = RootView(screen)
        self._view.clear()

    def on_resize(self, new_width, new_height):
        self._view.resize(new_width, new_height)

    def on_start(self):
        self._view.show_scanning()
        self.schedule_async(FileWalkProcessor(self._root_folders, self._walk_file, self, self._log).process())

    @callback
    def on_filewalk_progress(self, folder_count, file_count):
        self._view.update_scanning(folder_count, file_count)

    @callback
    def on_filewalk_loading(self, walk_file):
        self._view.show_loading(walk_file)

    @callback
    def on_filewalk_saving(self, walk_file):
        self._view.show_saving(walk_file)

    @callback
    def on_filewalk_finished(self, file_walk):
        self._file_walk = file_walk
        self._total_files = len(file_walk)
        self._view.show_size_counting(file_walk.folder_count(), self._total_files)
        self.schedule_async(FileSizeProcessor(file_walk, self._size_file, self, self._log).process())

    @callback
    def on_filesize_progress(self, file_count, byte_count):
        self._view.update_size_counting(file_count, self._total_files, byte_count)

    @callback
    def on_filesize_finished(self, sizes, byte_count):
        self._sizes = sizes
        self._total_bytes = byte_count
        self._view.show_hashing(self._total_files, byte_count)
        self.schedule_async(FileHashProcessor(self._file_walk, self._sizes, self._hash_file, self, self._log).process())

    @callback
    def on_hashing_progress(self, file_count, byte_count):
        self._view.update_hashing(file_count, self._total_files, byte_count, self._total_bytes)

    @callback
    def on_hashing_finished(self, hashes):
        self._hashes = hashes
        self._view.show_analysing()
        self.schedule_async(DuplicateAnalysis.create(hashes, self._file_walk, self._sizes, self._ignored_folders, self))

    @callback
    def on_analysis_progress(self, file_count):
        self._view.update_analysing(file_count, self._total_files)

    @callback
    def on_analysis_finished(self, analysis):
        self._view.show_browser(analysis)

    def on_error(self, error, task=None):
        if task is None:
            self._log.error(f"Error while handling event {str(error)}")
        else:
            self._log.error(f"Error while executing task {task}: {str(error)}")
        self._view.show_error(error)

    def on_key(self, key):
        self._log.debug(f"on_key: {key}")
        if key == 27:
            self.terminate()
        elif key == 410:
            self.resize()
        else:
            pass

    def on_termination(self):
        self._executor.shutdown()
