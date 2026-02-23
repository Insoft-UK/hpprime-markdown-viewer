# Changelog

All notable changes to MarkdownViewer for HP Prime are documented in this file.

---

## [1.1.0] — 2026-02-23

### Added

#### Viewer — More Menu (F5)
- **Font Size Toggle** — cycle body text through 10px, 12px, and 14px; headers scale proportionally.
- **Word Wrap Toggle** — turn word wrap on/off; when off, long lines are clipped at the right edge instead of wrapping.
- **Split View / TOC Pane** — toggle a mini table-of-contents pane at the top of the screen showing up to 5 headers around the current position. Tap a header to jump to that section.
- **Go to %** — jump to a specific position in the document by entering a percentage (0–100).
- **Keyboard Shortcuts Overlay** — full-screen reference of all keyboard shortcuts; dismiss with any key or tap.
- **Doc Info** — view filename, line count, word count, and estimated reading time (moved from former F5 slot).
- **Forward navigation** — when available, navigate forward after using back navigation.

#### Viewer — Navigation
- **Back / Forward nav stack** — press Left arrow to go back, Right arrow to go forward through browsing history. Forward stack is cleared on new link navigation.
- **Collapsible Sections** — tap any header to collapse or expand its content. Collapsed headers show ▶, expanded show ▼. All content under the header (up to the next header of equal or higher level) is hidden.

#### Viewer — Context Menu (Long Press)
- **Copy Line** — copy the text line at the long-press position to the PPL clipboard (`AVars("Clipboard")`).
- **Tag cycling** — cycle the current file's tag category directly from the viewer context menu.

#### File Browser
- **Help button (F5)** — opens the built-in help file directly from the browser menu bar.
- **Multi-language Help** — the app detects the calculator's language setting and loads a translated help file (e.g. `help_es.md` for Spanish) when available, falling back to `help.md`.
- **File Tags / Categories** — long-press a file in the browser to assign a colored tag. Six categories: None, Math (blue), Science (green), Notes (orange), Work (red), Personal (purple). Tagged files display a colored dot before the filename. Tags persist across app restarts.

#### Persistence
- **Per-file scroll position** — scroll positions are saved per-file in a `.positions` file. Reopening a document restores the last reading position automatically.

### Changed
- Viewer menu bar changed from `Find | Next | Marks | TOC | Info | Theme` to `Find | Next | Marks | TOC | More | Theme`.
- Browser menu bar changed from `Recent | | | | | Theme` to `Recent | | | | Help | Theme`.
- Long-press context menu in the viewer expanded from `[Add Bookmark]` to `[Add Bookmark, Copy Line, Tag: <name>]`.

### Fixed
- **Locale / decimal separator** — added `ppl_guard.py` to save and restore `HSeparator`, forcing dot-decimal mode during execution. Changed `wait()` calls to use integer fractions to avoid locale-dependent float parsing errors.
- **G2 hardware crash** — replaced `_draw_pie` (which used `math.sin`/`cos` and arc drawing that could crash certain firmware versions) with a safe `_draw_progress_bar`. Cached theme colors with `.get()` defaults. Added `gc.collect()` before viewer creation.

### Documentation
- Updated `help.md` with all new features (More menu, collapsible sections, tags, split view, shortcuts, etc.).
- Updated `help_es.md` (Spanish translation) with matching content.

---

## [1.0.0] — Initial Release

### Features
- Markdown rendering: headers (H1–H6), bold, italic, strikethrough, inline code, code blocks, blockquotes (nested), ordered/unordered lists (nested), task lists, tables, horizontal rules, links, images (base64 and file).
- CAS formula rendering via ` ```math ` code blocks.
- File browser with sortable columns (Name, Size, Star), favorites, recent files list.
- Search with highlighting and next-match navigation.
- Table of Contents from document headers.
- Document Info (line count, word count, reading time).
- Bookmarks with red scrollbar marks and bookmark manager.
- Reading progress percentage indicator.
- Internal `.md` link navigation with back-stack.
- Light / Dark theme toggle.
- File organization via underscore-to-slash naming convention.
- Touch scrolling with drag support and scrollbar tap/drag.
- Last-file and scroll position persistence.
