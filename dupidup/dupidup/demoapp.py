from magicur.app import MagicApplication
from dupidup.progress import ProgressWindow

# 176    B0    U+2591    ░    light shade
# 177    B1    U+2592    ▒    medium shade
# 178    B2    U+2593    ▓    dark shade
# 179    B3    U+2502    │    box drawings light vertical
# 180    B4    U+2524    ┤    box drawings light vertical and left
# 181    B5    U+2561    ╡    box drawings vertical single and left double
# 182    B6    U+2562    ╢    box drawings vertical double and left single
# 183    B7    U+2556    ╖    box drawings down double and left single
# 184    B8    U+2555    ╕    box drawings down single and left double
# 185    B9    U+2563    ╣    box drawings double vertical and left
# 186    BA    U+2551    ║    box drawings double vertical
# 187    BB    U+2557    ╗    box drawings double down and left
# 188    BC    U+255D    ╝    box drawings double up and left
# 189    BD    U+255C    ╜    box drawings up double and left single
# 190    BE    U+255B    ╛    box drawings up single and left double
# 191    BF    U+2510    ┐    box drawings light down and left
# 192    C0    U+2514    └    box drawings light up and right
# 193    C1    U+2534    ┴    box drawings light up and horizontal
# 194    C2    U+252C    ┬    box drawings light down and horizontal
# 195    C3    U+251C    ├    box drawings light vertical and right
# 196    C4    U+2500    ─    box drawings light horizontal
# 197    C5    U+253C    ┼    box drawings light vertical and horizontal
# 198    C6    U+255E    ╞    box drawings vertical single and right double
# 199    C7    U+255F    ╟    box drawings vertical double and right single
# 200    C8    U+255A    ╚    box drawings double up and right
# 201    C9    U+2554    ╔    box drawings double down and right
# 202    CA    U+2569    ╩    box drawings double up and horizontal
# 203    CB    U+2566    ╦    box drawings double down and horizontal
# 204    CC    U+2560    ╠    box drawings double vertical and right
# 205    CD    U+2550    ═    box drawings double horizontal
# 206    CE    U+256C    ╬    box drawings double vertical and horizontal
# 207    CF    U+2567    ╧    box drawings up single and horizontal double
# 208    D0    U+2568    ╨    box drawings up double and horizontal single
# 209    D1    U+2564    ╤    box drawings down single and horizontal double
# 210    D2    U+2565    ╥    box drawings down double and horizontal single
# 211    D3    U+2559    ╙    box drawings up double and right single
# 212    D4    U+2558    ╘    box drawings up single and right double
# 213    D5    U+2552    ╒    box drawings down single and right double
# 214    D6    U+2553    ╓    box drawings down double and right single
# 215    D7    U+256B    ╫    box drawings vertical double and horizontal single
# 216    D8    U+256A    ╪    box drawings vertical single and horizontal double
# 217    D9    U+2518    ┘    box drawings light up and left
# 218    DA    U+250C    ┌    box drawings light down and right
# 219    DB    U+2588    █    full block
# 220    DC    U+2584    ▄    lower half block
# 221    DD    U+258C    ▌    left half block
# 222    DE    U+2590    ▐    right half block
# 223    DF    U+2580    ▀    upper half block


class DemoApplication(MagicApplication):

    def init_palette(self, palette):
        palette.add_default_colors()
        palette.add_pair("lightgray black", "lightgray", "black")
        palette.add_pair("yellow blue", "yellow", "blue")
        palette.add_pair("black lightgray", "black", "lightgray")

    def init_view2(self, screen):
        # Folders Processed Total
        # Files   Processed Total
        # Size

        win = screen.sub_window(screen.width, screen.height, 0, 0)
        win.reset_to(" ", "lightgray black")
        self._stat = ProgressWindow(win)
        self._stat.set_num_files(100023)
        self._stat.set_num_folders(223)
        self._stat.set_size(132489674323)
        self._stat.set_action_msg("Creating a demo thing ...")

    def on_key(self, key):
        if key == 32 and self._stat is not None:
            self._stat.set_num_files(100024)
            self._stat.set_num_folders(224)
            self._stat.set_size(152489674323)
            self._stat.set_action_msg("Another message ...")
            self._stat.refresh()
            self._screen._stdscr.move(0, 0)

    def init_view(self, screen):
        win = screen.sub_window(screen.width, screen.height, 0, 0)
        win.reset_to(" ", "lightgray black")
        win.put_text(0, 0, "┌─────────────────────────────┬─────────────────────────────┐")
        win.put_text(0, 1, "│                             │                             │")
        win.put_text(0, 2, "╞═════════════════════════════╪═════════════════════════════╡")
        win.put_text(0, 3, "│                             │                             │")
        win.put_text(0, 4, "╞═════════════════════════════╪═════════════════════════════╡")
        win.put_text(0, 5, "│                             │                             │")
        win.put_text(0, 6, "│                             │                             │")
        win.put_text(0, 7, "└─────────────────────────────┴─────────────────────────────┘")

        lab1 = win.sub_window(18, 1, 2, 4)
        lab1.reset_to(" ", "black lightgray")
        lab1.put_text(0, 0, "/path/to/something")

        lab2 = win.sub_window(23, 1, 2, 2)
        lab2.reset_to(" ", "black lightgray")
        lab2.put_text(0, 0, "/path/to/something/else")
        lab2.set_paint(0, 0, 10, "yellow blue")
        win.refresh()

