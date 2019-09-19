from dupidup.progress import ProgressWindow, sizeof_fmt
from dupidup.browser import DuplicateBrowser
import traceback


class RootView:

    def __init__(self, screen):
        self._screen = screen

    def clear(self):
        bg = self._screen.sub_window(self._screen.width, self._screen.height, 0, 0)
        bg.reset_to(" ", "lightgray black")
        bg.refresh()

    def size(self):
        return self._screen.size()

    @property
    def width(self):
        return self.size()[0]

    @property
    def height(self):
        return self.size()[1]

    def sub_window(self, width, height, x, y):
        return self._screen.sub_window(width, height, x, y)

    def resize(self, new_width, new_height):
        self.clear()
        if self._progress is not None:
            self._progress.resize(new_width, new_height)

    def show_error(self, exception):
        self.clear()
        self._progress = None
        self._browser = None
        bg = self._screen.sub_window(self._screen.width, self._screen.height, 0, 0)
        bg.reset_to(" ", "white red")
        bg.put_text(0, 0, str(exception))
        bg.put_text(0, 2, traceback.format_exc())
        bg.refresh()

    def show_scanning(self):
        self._progress = ProgressWindow(self)
        self._progress.set_action_msg("Scanning files ...")
        self._progress.refresh()

    def update_scanning(self, folder_count, file_count):
        self._progress.set_num_folders(folder_count)
        self._progress.set_num_files(file_count)
        self._progress.refresh()

    def show_loading(self, walk_file):
        self._progress.set_action_msg(f"Loading walk file {walk_file} ...")
        self._progress.refresh()

    def show_saving(self, walk_file):
        self._progress.set_action_msg(f"Saving walk file {walk_file} ...")
        self._progress.refresh()

    def show_size_counting(self, folder_count, file_count):
        self._progress.set_num_folders(folder_count)
        self._progress.set_num_files(file_count)
        self._progress.set_action_msg("Counting file sizes ...")
        self._progress.refresh()

    def update_size_counting(self, file_count, total_files, byte_count):
        self._progress.set_num_files(file_count, total=total_files)
        self._progress.set_size(byte_count)
        self._progress.refresh()

    def show_hashing(self, total_files, total_bytes):
        self._progress.set_num_files(total_files)
        self._progress.set_size(total_bytes)
        self._progress.set_action_msg("Computing file hashes ...")
        self._progress.refresh()

    def update_hashing(self, file_count, total_files, byte_count, total_bytes):
        self._progress.set_num_files(file_count, total=total_files)
        self._progress.set_size(byte_count, total=total_bytes)
        self._progress.refresh()

    def show_analysing(self):
        self._progress.set_action_msg("Analysing duplicates ...")
        self._progress.refresh()

    def update_analysing(self, file_count, total_files):
        self._progress.set_num_files(file_count, total=total_files)
        self._progress.refresh()

    def show_browser(self, analysis):
        self._progress = None
        self.clear()
        self._browser = DuplicateBrowser(self, analysis)
        self._browser.refresh()
        self._status = Status(self)
        self._status.message(f"Duplicated bytes: {sizeof_fmt(analysis.get_duplicated_bytes())}")
        self._status.refresh()


class Status():

    def __init__(self, parent):
        self._parent = parent
        self._window = parent.sub_window(parent.width, 1, 0, parent.height - 1)

    def message(self, msg):
        self._window.put_text(1, 0, msg)
        self._window.refresh()

    def refresh(self):
        self._window.refresh()
