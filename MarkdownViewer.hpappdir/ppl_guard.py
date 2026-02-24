"""Guard for PPL eval calls — ensures dot decimal separator mode.

HP Prime's Home Settings include a Digit Grouping / Decimal Mark option
(HSeparator) that controls whether dot or comma is used as the decimal
separator and whether commas or semicolons separate function arguments.

When comma-decimal mode is active, PPL function calls that use commas
as argument separators (e.g. TEXTSIZE("hi",2)) or dots in decimal
numbers (e.g. wait(0.05)) will silently fail or produce wrong results.

This module saves the current HSeparator setting at startup and forces
dot-decimal mode (HSeparator:=0).  The original value is restored once
on application exit via cleanup().  HSeparator is never modified in
between — all PPL eval calls are safe for the entire app lifetime.

Usage — call once at startup, restore once at exit:
    import ppl_guard
    ppl_guard.init()      # force dot mode
    ...                   # all PPL eval calls are now safe
    ppl_guard.cleanup()   # restore original setting on exit

Reference: https://www.hpmuseum.org/forum/thread-23501.html
"""

from hpprime import eval as heval

_saved_separator = None


def init():
    """Save current HSeparator and force dot decimal mode.

    Call this ONCE at app startup, before any PPL eval calls
    that use decimal numbers or multi-argument PPL functions.
    """
    global _saved_separator
    try:
        _saved_separator = int(heval('HSeparator'))
    except:
        _saved_separator = 0
    # Force dot decimal separator (option 0 = 123,456.789)
    # HSeparator:=0 uses only integers, so it works safely
    # regardless of the current decimal separator setting.
    try:
        heval('HSeparator:=0')
    except:
        pass


def cleanup():
    """Restore the original HSeparator setting.

    Call this on app exit to leave the calculator in its
    original state.
    """
    global _saved_separator
    if _saved_separator is not None:
        try:
            heval('HSeparator:=%d' % _saved_separator)
        except:
            pass
