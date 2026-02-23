"""Reusable file picker for HP Prime (320x240).

Column-based file browser resembling a desktop file explorer.
Displays sortable columns for favorites (star), filename, and size.
Tap column headers to sort. Tap a star to toggle favorite.

The caller can customize the title, subtitle, file extension filter,
menu labels, menu-tap handler, and color palette.
"""

from micropython import const
from constants import (GR_AFF, FONT_10, FONT_12, FONT_14)
from hpprime import fillrect
from graphics import draw_text, draw_rectangle, text_width
from keycodes import KEY_UP, KEY_DOWN, KEY_ENTER, KEY_ESC
from file_ops import list_files, get_file_size
from input_helpers import get_key, get_touch, get_menu_tap
from ui import draw_menu
import file_prefs

# Column layout (pixel positions)
_COL_FAV_X = const(7)
_COL_DIV1 = const(27)
_COL_NAME_X = const(30)
_COL_DIV2 = const(255)
_COL_SIZE_X = const(258)
_COL_RIGHT = const(313)

# Rows
_HDR_Y = const(38)
_HDR_H = const(14)
_SEP_Y = const(52)
_ITEM_Y0 = const(54)
_ITEM_H = const(20)
_MAX_VISIBLE = const(8)


def _get_colors(colors):
    if colors is not None:
        return colors
    import theme
    return theme.colors


def get_files(ext=None):
    """List files from storage, optionally filtered by extension.

    Args:
        ext: file extension including dot (e.g. '.md'). None = all files.
    """
    all_files = list_files()
    result = []
    if all_files:
        for f in all_files:
            s = str(f)
            if ext is None or s.endswith(ext):
                result.append(s)
    return result


def _format_size(size):
    """Format file size for display (always in KB, 2 decimals)."""
    kb100 = (size * 100 + 512) // 1024
    whole = kb100 // 100
    frac = kb100 % 100
    if frac < 10:
        return str(whole) + '.0' + str(frac) + ' KB'
    return str(whole) + '.' + str(frac) + ' KB'


def _draw_progress_bar(x, y, w, h, pct, fg_color, bg_color, border_color):
    """Draw a tiny horizontal progress bar showing pct% progress.

    Lightweight alternative to pie chart — no trig, no pixel loops.
    Just three fillrect calls at most.
    """
    # Border
    fillrect(GR_AFF, x, y, w, h, border_color, bg_color)
    # Fill
    if pct > 0:
        fw = max(1, (w - 2) * min(pct, 100) // 100)
        fillrect(GR_AFF, x + 1, y + 1, fw, h - 2, fg_color, fg_color)


def _file_label(fname):
    """Build display label for a filename.

    Files named ``prefix_rest.md`` display as ``prefix/rest.md``
    to provide a visual folder-like grouping convention.
    """
    idx = fname.find('_')
    if idx > 0 and idx < len(fname) - 1:
        return fname[:idx] + '/' + fname[idx + 1:]
    return fname


def _build_file_list(ext, sizes):
    """Build sorted file list based on current sort settings.

    Args:
        ext: file extension filter.
        sizes: dict {filename: size_in_bytes}.

    Returns list of (filename, size, is_fav) tuples.
    """
    raw_files = get_files(ext)
    favs = file_prefs.get_favorites()
    col, asc = file_prefs.get_sort()

    items = []
    for f in raw_files:
        sz = sizes.get(f, 0)
        is_fav = f in favs
        items.append((f, sz, is_fav))

    if col == 'fav':
        if asc:
            items.sort(key=lambda x: (not x[2], x[0].lower()))
        else:
            items.sort(key=lambda x: (x[2], x[0].lower()))
    elif col == 'size':
        items.sort(key=lambda x: x[1], reverse=not asc)
    else:
        items.sort(key=lambda x: x[0].lower(), reverse=not asc)

    return items


def file_picker(title="Files", subtitle="Select a file", ext=None,
                menu_labels=None, on_menu_tap=None, highlight=None,
                menu_y=220, colors=None):
    """Show a column-based file picker and return the selected filename.

    Args:
        title:       heading text centred at top.
        subtitle:    smaller text below the heading.
        ext:         file extension filter (e.g. '.md'). None = all files.
        menu_labels: list of up to 6 menu-bar labels.
        on_menu_tap: callback(slot, selected_file) for menu actions.
        highlight:   filename to mark with a triangle in the list.
        menu_y:      Y coordinate of the menu bar.
        colors:      color dict. Falls back to theme.colors.

    Returns:
        Selected filename (str), or None if cancelled (ESC / ON).
    """
    # Compute file sizes once
    raw = get_files(ext)
    sizes = {}
    for f in raw:
        sizes[f] = get_file_size(f)

    items = _build_file_list(ext, sizes)
    selected = 0

    if highlight:
        for i in range(len(items)):
            if items[i][0] == highlight:
                selected = i
                break

    if menu_labels is None:
        menu_labels = ["", "", "", "", "", ""]

    touch_down = False
    tap_x = -1
    tap_y = -1
    touch_start_time = 0
    long_press_fired = False

    from input_helpers import get_ticks

    def _fav_color():
        c = _get_colors(colors)
        return c.get('fav_star', 0xCCA000)

    def draw_screen():
        c = _get_colors(colors)
        # Cache color lookups to avoid repeated dict access and
        # guard against KeyError if theme dict is incomplete.
        bg = c.get('browser_bg', 0xF8F8F8)
        subtitle_c = c.get('browser_subtitle', 0x000080)
        hint_c = c.get('browser_hint', subtitle_c)
        hdr_bg = c.get('table_header_bg', 0xE8E8E8)
        tbl_bdr = c.get('table_border', 0xAAAAAA)
        br_bdr = c.get('browser_border', 0x000080)
        sel_bg = c.get('browser_sel', 0x000080)
        sel_text = c.get('browser_sel_text', 0xF8F8F8)
        normal_text = c.get('browser_text', 0x000000)
        alt_bg = c.get('table_alt_bg', bg)
        err_c = c.get('browser_error', 0xF80000)
        prog_fg = c.get('progress_bar', c.get('header', 0x000080))

        fillrect(0, 0, 0, 320, menu_y, bg, bg)

        # Title
        tw = text_width(title, FONT_14)
        draw_text(GR_AFF, (320 - tw) // 2, 5, title, FONT_14,
                  subtitle_c)
        # Subtitle
        draw_text(GR_AFF, 10, 23, subtitle, FONT_10, hint_c)

        # Column header background
        draw_rectangle(GR_AFF, 5, _HDR_Y, 315, _HDR_Y + _HDR_H,
                       hdr_bg, 255, hdr_bg, 255)

        col, asc = file_prefs.get_sort()
        arrow = ' \u25B2' if asc else ' \u25BC'

        # Fav column header
        fav_hdr = '\u2605'
        if col == 'fav':
            fav_hdr += arrow
        draw_text(GR_AFF, _COL_FAV_X + 2, _HDR_Y + 2, fav_hdr, FONT_10,
                  _fav_color())

        # Name column header
        name_hdr = 'Name'
        if col == 'name':
            name_hdr += arrow
        draw_text(GR_AFF, _COL_NAME_X + 2, _HDR_Y + 2, name_hdr, FONT_10,
                  subtitle_c)

        # Size column header
        size_hdr = 'Size'
        if col == 'size':
            size_hdr += arrow
        draw_text(GR_AFF, _COL_SIZE_X + 2, _HDR_Y + 2, size_hdr, FONT_10,
                  subtitle_c)

        # Column dividers in header
        draw_rectangle(GR_AFF, _COL_DIV1, _HDR_Y,
                       _COL_DIV1 + 1, _HDR_Y + _HDR_H,
                       tbl_bdr, 255, tbl_bdr, 255)
        draw_rectangle(GR_AFF, _COL_DIV2, _HDR_Y,
                       _COL_DIV2 + 1, _HDR_Y + _HDR_H,
                       tbl_bdr, 255, tbl_bdr, 255)

        # Separator below header
        draw_rectangle(GR_AFF, 5, _SEP_Y, 315, _SEP_Y + 1,
                       tbl_bdr, 255, tbl_bdr, 255)

        # Left / right borders
        bdr_bottom = menu_y - 3
        draw_rectangle(GR_AFF, 5, _HDR_Y, 6, bdr_bottom,
                       br_bdr, 255, br_bdr, 255)
        draw_rectangle(GR_AFF, 314, _HDR_Y, 315, bdr_bottom,
                       br_bdr, 255, br_bdr, 255)

        # File rows
        start = 0
        if selected >= _MAX_VISIBLE:
            start = selected - _MAX_VISIBLE + 1

        for i in range(start, min(start + _MAX_VISIBLE, len(items))):
            y = _ITEM_Y0 + (i - start) * _ITEM_H
            fname, sz, is_fav = items[i]
            label = _file_label(fname)
            size_str = _format_size(sz)

            if i == selected:
                draw_rectangle(GR_AFF, 6, y, 314, y + _ITEM_H - 2,
                               sel_bg, 255, sel_bg, 255)
                text_c = sel_text
            else:
                text_c = normal_text
                if (i - start) % 2 == 1:
                    draw_rectangle(GR_AFF, 6, y, 314, y + _ITEM_H - 2,
                                   alt_bg, 255, alt_bg, 255)

            # Favorite star
            if is_fav:
                draw_text(GR_AFF, _COL_FAV_X + 4, y + 3, '\u2605',
                          FONT_10, _fav_color())
            elif highlight and fname == highlight and i != selected:
                draw_text(GR_AFF, _COL_FAV_X + 4, y + 3, '\u25B6',
                          FONT_10, hint_c)

            # File name + tag dot
            tag_id = file_prefs.get_tag(fname)
            name_x = _COL_NAME_X + 2
            if tag_id > 0 and tag_id < len(file_prefs.TAG_COLORS):
                tc = file_prefs.TAG_COLORS[tag_id]
                fillrect(GR_AFF, name_x, y + 6, 6, 6, tc, tc)
                name_x += 9
            max_name_w = _COL_DIV2 - name_x - 2
            draw_text(GR_AFF, name_x, y + 3, label,
                      FONT_10, text_c, max_name_w)

            # Size
            draw_text(GR_AFF, _COL_SIZE_X + 2, y + 3, size_str,
                      FONT_10, text_c)

            # Reading progress bar
            pct = file_prefs.get_progress(fname)
            if pct > 0:
                bar_x = _COL_RIGHT - 16
                bar_y = y + _ITEM_H // 2 - 2
                bar_bg = sel_bg if i == selected else (
                    alt_bg if (i - start) % 2 == 1 else bg)
                _draw_progress_bar(bar_x, bar_y, 14, 4, pct,
                                   prog_fg, bar_bg, hint_c)

            # Column dividers for this row
            div_c = sel_bg if i == selected else tbl_bdr
            draw_rectangle(GR_AFF, _COL_DIV1, y,
                           _COL_DIV1 + 1, y + _ITEM_H - 2,
                           div_c, 255, div_c, 255)
            draw_rectangle(GR_AFF, _COL_DIV2, y,
                           _COL_DIV2 + 1, y + _ITEM_H - 2,
                           div_c, 255, div_c, 255)

        if len(items) == 0:
            draw_text(GR_AFF, 15, _ITEM_Y0 + 6, "No files found", FONT_10,
                      err_c)

        # Bottom border
        draw_rectangle(GR_AFF, 5, bdr_bottom, 315, bdr_bottom + 1,
                       br_bdr, 255, br_bdr, 255)
        draw_menu(menu_labels, menu_y=menu_y, colors=c)

    def _header_tap(tx):
        """Handle a tap on a column header."""
        nonlocal items, selected
        sel_fname = items[selected][0] if items else None
        if tx < _COL_DIV1:
            file_prefs.cycle_sort('fav')
        elif tx < _COL_DIV2:
            file_prefs.cycle_sort('name')
        else:
            file_prefs.cycle_sort('size')
        items = _build_file_list(ext, sizes)
        selected = 0
        if sel_fname:
            for i in range(len(items)):
                if items[i][0] == sel_fname:
                    selected = i
                    break
        return True

    def _star_tap(row_idx):
        """Toggle favorite for the tapped row."""
        nonlocal items, selected
        if row_idx < 0 or row_idx >= len(items):
            return False
        fname = items[row_idx][0]
        file_prefs.toggle_favorite(fname)
        sel_fname = items[selected][0] if items else None
        items = _build_file_list(ext, sizes)
        selected = 0
        if sel_fname:
            for i in range(len(items)):
                if items[i][0] == sel_fname:
                    selected = i
                    break
        return True

    def _do_menu(slot):
        """Process a menu action. Returns a filename or None."""
        nonlocal items, selected
        if not on_menu_tap:
            return None
        sel_file = items[selected][0] if items else None
        result = on_menu_tap(slot, sel_file)
        if result == 'reload':
            items = _build_file_list(ext, sizes)
            if selected >= len(items):
                selected = max(0, len(items) - 1)
            if sel_file:
                for i in range(len(items)):
                    if items[i][0] == sel_file:
                        selected = i
                        break
            draw_screen()
        elif isinstance(result, str) and result.startswith('open:'):
            return result[5:]
        elif result:
            draw_screen()
        return None

    draw_screen()

    try:
        while True:
            key = get_key()
            if key > 0:
                if key == KEY_UP:
                    if selected > 0:
                        selected -= 1
                        draw_screen()
                elif key == KEY_DOWN:
                    if items and selected < len(items) - 1:
                        selected += 1
                        draw_screen()
                elif key == KEY_ENTER:
                    if items:
                        return items[selected][0]
                elif key == KEY_ESC:
                    return None

            tx, ty = get_touch()
            if tx >= 0 and ty >= 0:
                if not touch_down:
                    touch_down = True
                    tap_x = tx
                    tap_y = ty
                    touch_start_time = get_ticks()
                    long_press_fired = False
                else:
                    # Long press detection for tag assignment
                    if (not long_press_fired and items
                            and tap_y >= _ITEM_Y0 and tap_y < menu_y
                            and abs(tx - tap_x) + abs(ty - tap_y) < 10):
                        elapsed = get_ticks() - touch_start_time
                        if elapsed >= 600:  # LONG_PRESS_MS
                            long_press_fired = True
                            start_row = 0
                            if selected >= _MAX_VISIBLE:
                                start_row = selected - _MAX_VISIBLE + 1
                            row = (tap_y - _ITEM_Y0) // _ITEM_H
                            tapped = start_row + row
                            if tapped < len(items):
                                fname = items[tapped][0]
                                from ui import show_context_menu
                                cur_tag = file_prefs.get_tag(fname)
                                tag_labels = []
                                for ti in range(len(file_prefs.TAG_NAMES)):
                                    lbl = file_prefs.TAG_NAMES[ti]
                                    if ti == cur_tag:
                                        lbl = '\u2713 ' + lbl
                                    tag_labels.append(lbl)
                                choice = show_context_menu(
                                    tap_x, tap_y, tag_labels,
                                    content_bottom=menu_y)
                                if choice >= 0:
                                    file_prefs.set_tag(fname, choice)
                                draw_screen()
            elif touch_down:
                touch_down = False
                if long_press_fired:
                    continue
                # Column header tap
                if _HDR_Y <= tap_y < _SEP_Y and 5 < tap_x < 315:
                    if _header_tap(tap_x):
                        draw_screen()
                # Menu tap
                elif tap_y >= menu_y:
                    slot = get_menu_tap(tap_x, tap_y, menu_y)
                    if slot >= 0:
                        result = _do_menu(slot)
                        if result is not None:
                            return result
                # File row tap
                elif items and tap_y >= _ITEM_Y0 and tap_y < menu_y:
                    start = 0
                    if selected >= _MAX_VISIBLE:
                        start = selected - _MAX_VISIBLE + 1
                    row = (tap_y - _ITEM_Y0) // _ITEM_H
                    tapped = start + row
                    if tapped < len(items):
                        if tap_x < _COL_DIV1:
                            if _star_tap(tapped):
                                draw_screen()
                        elif tapped == selected:
                            return items[selected][0]
                        else:
                            selected = tapped
                            draw_screen()

    except KeyboardInterrupt:
        return None
