

def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


def _get_segment_dims(width):
    width_in = width - 3
    width_labels = max((width_in * 30) // 100, 9)
    width_values = max((width_in * 70) // 100, 23)

    while width_labels + width_values < width_in:
        width_values += 1

    while width_labels + width_values > width_in and width_values > 23:
        width_values -= 1

    while width_labels + width_values > width_in and width_labels > 9:
        width_labels -= 1

    return width_in + 1, width_labels, width_values


class ProgressWindow(object):
    '''
    Window that displays information about file scanning, file size counting and file hashing progress
    '''

    def __init__(self, parent):
        self._parent = parent
        self._window = self.draw()
        self._value_action_msg = None
        self._value_size = None
        self._value_size_total = None
        self._value_files = None
        self._value_files_total = None
        self._value_folders = None

    def draw(self):
        width = min(102, self._parent.width)
        if width < 35:
            raise Exception(f"Terminal too narrow. Needs width 35")
        if self._parent.height < 11:
            raise Exception(f"Terminal too small. Needs height 11")
        win = self._parent.sub_window(width, 11, (self._parent.width - width) // 2, (self._parent.height - 11) // 2)

        width_in, width_labels, width_values = _get_segment_dims(width)

        win.reset_to(" ", "black lightgray")
        win.put_text(0, 0, "┌" + "─"*width_in + "┐")
        win.put_text(0, 1, "│" + " "*width_in + "│")
        win.put_text(0, 2, "│" + " "*width_in + "│")
        win.put_text(0, 3, "│" + " "*width_in + "│")
        win.put_text(0, 4, "╞" + "═"*width_labels + "╤" + "═"*width_values + "╡")
        win.put_text(0, 5, "│" + "Folders ".rjust(width_labels, " ") + "│" + " "*width_values + "│")
        win.put_text(0, 6, "├" + "─"*width_labels + "┼" + "─"*width_values + "┤")
        win.put_text(0, 7, "│" + "Files ".rjust(width_labels, " ") + "│" + " "*width_values + "│")
        win.put_text(0, 8, "├" + "─"*width_labels + "┼" + "─"*width_values + "┤")
        win.put_text(0, 9, "│" + "Size ".rjust(width_labels, " ") + "│" + " "*width_values + "│")
        win.put_text(0, 10, "└" + "─"*width_labels + "┴" + "─"*width_values + "┘")

        return win

    def resize(self, w, h):
        self._window = self.draw()
        if self._value_action_msg is not None:
            self.set_action_msg(self._value_action_msg)
        if self._value_files is not None:
            self.set_num_files(self._value_files, total=self._value_files_total)
        if self._value_folders is not None:
            self.set_num_files(self._value_folders)
        if self._value_size is not None:
            self.set_num_files(self._value_size, total=self._value_size_total)

    def set_action_msg(self, action_msg):
        self._value_action_msg = action_msg
        width_in = self._window.width - 2
        if len(action_msg) > width_in:
            action_msg = action_msg[:width_in]
        self._window.put_text(1, 1, " "*width_in)
        self._window.put_text(1, 2, " "*width_in)
        self._window.put_text(1, 3, " "*width_in)
        halflen = (width_in - len(action_msg)) // 2
        self._window.put_text(1 + halflen, 2, action_msg)

    def _clear_value(self, y):
        _, w_lab, w_val = _get_segment_dims(self._window.width)
        self._window.put_text(2 + w_lab, y, " "*w_val)

    def _set_value(self, y, val):
        _, w_lab, w_val = _get_segment_dims(self._window.width)
        if len(val) > w_val - 1:
            val = "ERROR"
        self._window.put_text(2 + w_lab, y, (val + " ").rjust(w_val))

    def clear_num_folders(self):
        self._value_folders = None
        self._clear_value(5)

    def clear_num_files(self):
        self._value_files = None
        self._clear_value(7)

    def clear_size(self):
        self._value_size = None
        self._clear_value(9)

    def set_num_folders(self, num_folders):
        self._value_folders = num_folders
        self._set_value(5, "{:,}".format(num_folders))

    def set_num_files(self, num_files, total=None):
        self._value_files = num_files
        self._value_files_total = total
        self._set_value(7, "{:,}".format(num_files) if total is None else "{:,} / {:,}".format(num_files, total))

    def set_size(self, size, total=None):
        self._value_size = size
        self._value_size_total = total
        self._set_value(9, sizeof_fmt(size) if total is None else sizeof_fmt(size) + " / " + sizeof_fmt(total))

    def refresh(self):
        self._window.refresh()
