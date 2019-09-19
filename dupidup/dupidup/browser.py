from itertools import chain, repeat


class DuplicateBox:

    def __init__(self, parent, duplicate_item, columns_above, parent_offset, box_offset, box_width):
        self._parent = parent
        self._duplicate_item = duplicate_item
        self._top_border = columns_above == 0
        cols = len(duplicate_item.dirs)
        parent.put_text(0, parent_offset, self._border(box_width, cols, columns_above))
        for i, dir1 in enumerate(duplicate_item.dirs):
            parent.put_text(2 + i * (box_width + 1), parent_offset, self._limit_path(box_width - 2, dir1))
        box_line_idx = 0
        line_offset = 1
        for row in duplicate_item.rows:
            for i in row.idx_range():
                if box_line_idx >= box_offset and parent_offset + line_offset < parent.height:
                    line = row.get_line(i)
                    parent.put_text(0, parent_offset + line_offset, self._line(box_width, cols))
                    for j, file1 in enumerate(line):
                        parent.put_text(2 + j * (box_width + 1), parent_offset + line_offset, self._limit_line_file(box_width - 2, file1))

                    line_offset += 1
                box_line_idx += 1

    def get_height(self):
        return self._duplicate_item.get_box_height() + 1

    def _limit_path(self, max_size, path):
        if len(path) <= max_size:
            return path
        else:
            return "..." + path[:-max_size + 3]

    def _limit_line_file(self, max_size, path):
        if path is None:
            return ""
        elif len(path) <= max_size:
            return path
        else:
            return "..." + path[:-max_size + 3]

    def _line(self, box_width, cols):
        return  "│" + (" "*box_width + "│") * cols

    def _border(self, box_width, cols, cols_above):
        line = "─"*box_width
        if cols_above == 0:
            return "┌" + "┬".join(repeat(line, cols)) + "┐"
        elif cols == cols_above:
            return "├" + "┼".join(repeat(line, cols)) + "┤"
        elif cols > cols_above:
            return "├" + "┼".join(repeat(line, cols_above)) + "┼" + "┬".join(repeat(line, cols - cols_above)) + "┐"
        else:
            return "├" + "┼".join(repeat(line, cols_above)) + "┼" + "┴".join(repeat(line, cols_above - cols)) + "┘"


class DuplicateBrowser(object):
    '''
    Duplicate browser
    '''

    def __init__(self, parent, analysis):
        self._parent = parent
        self._window = parent.sub_window(parent.width, parent.height - 1, 0, 0)
        self._window.reset_to(" ", "white blue")
        self._analysis = analysis
        self._window.put_text(0, 0, "duplicate browser")
        self._boxes = []

        parent_offset = 0
        box_offset = 0
        column_width = (parent.width - 4) // 2
        columns_above = 0
        for item in analysis.items:
            box = DuplicateBox(self._window, item, columns_above, parent_offset, box_offset, column_width)
            columns_above = len(item.dirs)
            self._boxes.append(box)
            parent_offset += box.get_height()
        self._window.put_text(0, parent_offset, "└" + "┴".join(repeat("─"*column_width, columns_above)) + "┘")

    def refresh(self):
        self._window.refresh()

