"""Guard for PPL eval calls — ensures dot decimal separator mode.

HP Prime's Home Settings include a Digit Grouping / Decimal Mark option
(HSeparator) that controls whether dot or comma is used as the decimal
separator and whether commas or semicolons separate function arguments.

When comma-decimal mode is active, PPL function calls that use commas
as argument separators (e.g. TEXTSIZE("hi",2)) or dots in decimal
numbers (e.g. wait(0.05)) will silently fail or produce wrong results.

This module saves the current HSeparator setting, forces dot-decimal
mode (HSeparator:=0), and provides cleanup to restore the original
setting on exit.

Usage — call once at startup:
    import ppl_guard
    ppl_guard.init()      # force dot mode
    ...                   # all PPL eval calls are now safe
    ppl_guard.cleanup()   # restore original setting on exit

Or use the context manager for scoped protection:
    with ppl_guard.PPLSafe():
        result = heval('TEXTSIZE("hello",2)')

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


class PPLSafe:
    """Context manager for safe PPL eval calls.

    Temporarily forces dot decimal separator mode:

        with PPLSafe():
            result = heval('TEXTSIZE("hello",2)')
    """
    def __enter__(self):
        try:
            self._prev = int(heval('HSeparator'))
        except:
            self._prev = 0
        try:
            heval('HSeparator:=0')
        except:
            pass
        return self

    def __exit__(self, *args):
        try:
            heval('HSeparator:=%d' % self._prev)
        except:
            pass
        return False
