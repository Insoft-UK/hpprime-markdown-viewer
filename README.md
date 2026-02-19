# MarkdownViewer for HP Prime

**The first Markdown renderer built entirely in MicroPython for the HP Prime graphing calculator.**

Read beautifully formatted Markdown documents right on your calculator's 320×240 display — no PC required.

---

## Features

### Markdown Rendering

- **Headers** — H1 through H6 with distinct sizing and color
- **Bold**, *italic*, ~~strikethrough~~, and `inline code` formatting
- **[Links](url)** rendered in a distinct color
- **Blockquotes** with accent bar (supports nesting)
- **Bullet lists** and **numbered lists** with nesting support
- **Task lists** — `- [x]` and `- [ ]` checkboxes
- **Horizontal rules** (`---`, `***`, `___`)
- **Tables** with header styling and alternating row colors (warns if too wide)
- **Embedded images** via base64-encoded raw pixel data or **image files** (PNG, etc.)
- **Math formula rendering** — fenced code blocks tagged `math`, `formula`, or `cas` render CAS expressions in pretty-print via the HP Prime CAS engine
- **Syntax highlighting** in code fences for Python, C/C++, and PPL — keywords, builtins, strings, numbers, and comments are color-coded
- **Word wrapping** that fits the 320px-wide screen

### Navigation & Viewer

- **Smooth scrolling** with Up/Down keys or **touch drag**
- **Fast drag scrolling** — pixel-shifted rendering via `strblit` for responsive touch drag
- **Scroll position indicator** — thin scrollbar on the right edge
- **Table of Contents** — press F3 or tap TOC to see all headers and jump to any section
- **Internal links** — links to other `.md` files are tappable; press ESC to go back (multi-level back-stack)
- **Document info** — press F5 or tap Info to see line count, word count, and estimated reading time
- **Search** — press F1 to find text, F2 for next match, with highlighting and case-sensitivity toggle
- **Reading progress** — percentage indicator at the bottom of the screen

### File Browser

- **Built-in file browser** to pick `.md` files from calculator storage
- **Favorites / pinned files** — tap the yellow \u2605 star on any row to pin it; favorites sort to the top
- **Recently opened files** — quick access to your last 10 opened files
- **Sortable column headers** — tap \u2605, Name, or Size headers to sort; tap again to reverse
- **File size display** — each file’s size is shown in its own column
- **Reading progress pie charts** — small pie chart on each file row showing how much you've read
- **Folder-prefix display** — files named `prefix_name.md` display as `prefix/name.md` for visual organization

### Themes & Persistence

- **Light / Dark theme** — press F6 to toggle, works in browser and viewer
- **Multiple bookmarks per file** — long-press to add, red indicators on scrollbar
- **Bookmark manager** — tap Marks to view, jump to, or delete bookmarks
- **Back navigation** — press ESC to return to file browser without exiting
- **Auto-save** — last opened file, scroll position, and reading progress remembered across sessions

## Demo
https://github.com/user-attachments/assets/5307571c-12e3-4f97-8d1d-4dc5f9e3dab0

## Getting Started

### Prerequisites

- An **HP Prime** graphing calculator (hardware or virtual/emulator)
- Firmware that supports MicroPython / Python apps

### Installation

1. Connect your HP Prime to your computer.
2. Copy the entire `MarkdownViewer.hpappdir` folder into the calculator's app directory.
3. The app will appear as **MarkdownViewer** in your application list.

### Adding Markdown Files

Place any `.md` files in the app's storage folder on the calculator. The built-in file browser will list them automatically.

### Usage

1. Launch **MarkdownViewer** from the app menu.
2. Use **Up / Down** to highlight a `.md` file, then press **Enter** to open it.
3. Scroll through the rendered document with **Up / Down** or by **dragging** on the touchscreen.
4. Press **ON** (or trigger a `KeyboardInterrupt`) to return to the file browser or exit.

## Controls

### File Browser

| Key | Action |
|---|---|
| **Up / Down** | Navigate file list |
| **Enter / Tap** | Open selected file |
| **Tap column header** | Sort by \u2605, Name, or Size |
| **Tap \u2605 star** | Pin / unpin a file |
| **Recent** (F1) | Show recently opened files |
| **Theme** (F6) | Toggle light / dark theme |
| **ON** | Exit app |

### Document Viewer

| Key | Action |
|---|---|
| **Up / Down** | Scroll line by line |
| **+ / -** | Scroll page by page |
| **Backspace** | Jump to start |
| **LOG** | Jump to end |
| **ESC** | Back to file browser |
| **Find** (F1) | Search for text (with case-sensitivity toggle) |
| **Next** (F2) | Jump to next search match |
| **Marks** (F3) | Open bookmark manager |
| **TOC** (F4) | Table of Contents — jump to any header |
| **Info** (F5) | Show document stats (lines, words, reading time) |
| **Theme** (F6) | Toggle light / dark theme |
| **Long press** | Add bookmark at current position |
| **Tap .md link** | Open linked file (ESC to go back) |
| **Touch drag** | Drag to scroll document |
| **ON** | Exit app |

## Supported Markdown Syntax

| Element | Syntax |
|---|---|
| Headings | `# H1` through `###### H6` |
| Bold | `**bold**` |
| Italic | `*italic*` |
| Strikethrough | `~~deleted~~` |
| Inline code | `` `code` `` |
| Links | `[text](url)` |
| Blockquotes | `> quote` (nest with `>>`) |
| Bullet list | `- item` or `* item` (indent for nesting) |
| Ordered list | `1. item` (indent for nesting) |
| Task list | `- [ ] todo` or `- [x] done` |
| Horizontal rule | `---`, `***`, or `___` |
| Tables | `\| col1 \| col2 \|` (up to 5 columns) |
| Code fences | ` ``` ` or ` ```python ` (syntax highlighting) |
| Math formulas | ` ```math ` / ` ```formula ` / ` ```cas ` |
| Images | `![alt](image.png)` or `![alt](data:image/raw;base64,...)` |
| Internal links | `[text](other.md)` to open another file |

> **Note:** Images can be loaded directly from files (PNG, etc.) placed in the app folder using `![alt](filename.png)`. Alternatively, images can use a custom raw format — the first 4 bytes encode width and height (2 bytes each, big-endian), followed by RGB pixel triplets, all base64-encoded. File-based images that exceed the display width are automatically scaled down.

## Project Structure

```
MarkdownViewer.hpappdir/
├── main.py              # Entry point — viewer loop + app-specific logic
├── browser.py           # Column-based file picker with sortable headers
├── ui.py                # Reusable UI: menu bar, input bar, context menu, list manager
├── input_helpers.py     # Reusable keyboard and touch input helpers
├── markdown_viewer.py   # MarkdownViewer, MarkdownRenderer & MarkdownDocument classes
├── graphics.py          # Drawing primitives (text, rectangles, images)
├── constants.py         # Colors, font sizes, layout constants
├── theme.py             # Light/dark theme palettes and toggle
├── bookmarks.py         # Multi-bookmark storage per file
├── file_prefs.py        # Favorites, recent files, sort prefs, reading progress
├── file_ops.py          # File listing via HP Prime AFiles()
├── keycodes.py          # Key code constants for GETKEY
├── utils.py             # Minimal utility stubs
├── time.py              # Simple tick-based timer
├── help.md              # Sample Markdown file bundled with the app
├── MarkdownViewer.hpapp          # HP Prime app descriptor
├── MarkdownViewer.hpappnote      # App notes
└── MarkdownViewer.hpappprgm      # App program metadata
```

## Sample Code

A minimal example showing how the viewer is used in `main.py`:

```python
from constants import GR_AFF
from markdown_viewer import MarkdownViewer

# Create viewer targeting the display buffer
viewer = MarkdownViewer(GR_AFF)

# Load and render a Markdown file
viewer.load_markdown_file("help.md")
viewer.render()

# Scroll through the document
viewer.scroll_down()   # scroll by 20px
viewer.render()

viewer.scroll_by(50)   # scroll by arbitrary pixel amount
viewer.render()
```

## How It Works

1. **`main.py`** boots the app, scans for `.md` files via `file_ops.list_files()`, and presents a column-based file browser with favorites, sorting, and reading progress indicators.
2. When a file is selected, a **`MarkdownViewer`** instance loads and parses the Markdown content line-by-line to conserve memory.
3. **`MarkdownRenderer`** walks each line, identifies block-level elements (headers, lists, rules, code fences, math blocks, images), then renders them with word-wrapping, inline formatting, and syntax highlighting to the HP Prime's graphics buffer using `TEXTOUT_P` and `FILLRECT` PPL commands exposed through the `hpprime` MicroPython module.
4. Scrolling adjusts a vertical offset and re-renders the visible portion. Touch drag uses `strblit` pixel-shifting for smooth, responsive scrolling.
5. Text width measurements and RGB color strings are cached to minimize costly PPL eval calls during rendering.

## Limitations

- Tables wider than 5 columns display a warning instead of rendering
- Syntax highlighting supports Python, C/C++, and PPL; other languages render as plain text
- Internal links work for `.md` files only; web URLs are displayed but not openable
- Images must be in the custom base64-encoded raw RGB format described above, or loaded from image files in the app folder
- Search highlights matches in paragraphs, lists, and blockquotes (not in headers, tables, or code fences)
- Bold is simulated via 1px-offset double-draw (no true bold font on HP Prime)
- Italic is rendered as a distinct color (no slanted font available)

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

Some ideas for future improvements:

- Horizontal scrolling for wide tables and code blocks
- Draggable scrollbar for fast navigation
- Font size selector
- Search result count and navigation
- More syntax highlighting languages

## License

This project is provided as-is for educational and personal use.

## Author

**Andrea Baccin**

---

*Built with ❤️ for the HP Prime community.*
