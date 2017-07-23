# coding=utf-8

import six
import logging
import sys
from datetime import datetime
from quantdigger.config import ConfigLog
try:
    import curses  # type: ignore
except ImportError:
    curses = None
try:
    import codecs
except ImportError:
    codecs = None

PY3 = sys.version_info >= (3,)

bytes_type = bytes
if PY3:
    unicode_type = str
    basestring_type = str
else:
    # The names unicode and basestring don't exist in py3 so silence flake8.
    unicode_type = unicode  # noqa
    basestring_type = basestring  # noqa

gen_log = logging.getLogger("qd.general")


def _stderr_supports_color():
    color = False
    if curses and hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
        try:
            curses.setupterm()
            if curses.tigetnum("colors") > 0:
                color = True
        except Exception:
            pass
    return color


def _safe_unicode(s):
    try:
        return _unicode(s)
    except UnicodeDecodeError:
        return repr(s)


_TO_UNICODE_TYPES = (unicode_type, type(None))


def to_unicode(value):
    """Converts a string argument to a unicode string.
    If the argument is already a unicode string or None, it is returned
    unchanged.  Otherwise it must be a byte string and is decoded as utf8.
    """
    if isinstance(value, _TO_UNICODE_TYPES):
        return value
    if not isinstance(value, bytes):
        raise TypeError(
            "Expected bytes, unicode, or None; got %r" % type(value)
        )
    return value.decode("utf-8")


# to_unicode was previously named _unicode not because it was private,
# but to avoid conflicts with the built-in unicode() function/type
_unicode = to_unicode


class LogFormatter(logging.Formatter):
    """Log formatter used in Tornado.
    Key features of this formatter are:
    * Color support when logging to a terminal that supports it.
    * Timestamps on every log line.
    * Robust against str/bytes encoding problems.
    This formatter is enabled automatically by
    `tornado.options.parse_command_line` or `tornado.options.parse_config_file`
    (unless ``--logging=none`` is used).
    """
    DEFAULT_FORMAT = '%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s'
    DEFAULT_DATE_FORMAT = '%y%m%d %H:%M:%S'
    DEFAULT_COLORS = {
        logging.DEBUG: 4,  # Blue
        logging.INFO: 2,  # Green
        logging.WARNING: 3,  # Yellow
        logging.ERROR: 1,  # Red
    }

    def __init__(self, color=True, fmt=DEFAULT_FORMAT,
                 datefmt=DEFAULT_DATE_FORMAT, colors=DEFAULT_COLORS):
        r"""
        :arg bool color: Enables color support.
        :arg string fmt: Log message format.
          It will be applied to the attributes dict of log records. The
          text between ``%(color)s`` and ``%(end_color)s`` will be colored
          depending on the level if color support is on.
        :arg dict colors: color mappings from logging level to terminal color
          code
        :arg string datefmt: Datetime format.
          Used for formatting ``(asctime)`` placeholder in ``prefix_fmt``.
        .. versionchanged:: 3.2
           Added ``fmt`` and ``datefmt`` arguments.
        """
        logging.Formatter.__init__(self, datefmt=datefmt)
        self._fmt = fmt

        self._colors = {}
        if color and _stderr_supports_color():
            # The curses module has some str/bytes confusion in
            # python3.  Until version 3.2.3, most methods return
            # bytes, but only accept strings.  In addition, we want to
            # output these strings with the logging module, which
            # works with unicode strings.  The explicit calls to
            # unicode() below are harmless in python2 but will do the
            # right conversion in python 3.
            fg_color = (curses.tigetstr("setaf") or
                        curses.tigetstr("setf") or "")
            if (3, 0) < sys.version_info < (3, 2, 3):
                fg_color = unicode_type(fg_color, "ascii")

            for levelno, code in six.iteritems(colors):
                self._colors[levelno] = unicode_type(curses.tparm(fg_color, code), "ascii")
            self._normal = unicode_type(curses.tigetstr("sgr0"), "ascii")
        else:
            self._normal = ''

    def format(self, record):
        try:
            message = record.getMessage()
            assert isinstance(message, basestring_type)  # guaranteed by logging
            # Encoding notes:  The logging module prefers to work with character
            # strings, but only enforces that log messages are instances of
            # basestring.  In python 2, non-ascii bytestrings will make
            # their way through the logging framework until they blow up with
            # an unhelpful decoding error (with this formatter it happens
            # when we attach the prefix, but there are other opportunities for
            # exceptions further along in the framework).
            #
            # If a byte string makes it this far, convert it to unicode to
            # ensure it will make it out to the logs.  Use repr() as a fallback
            # to ensure that all byte strings can be converted successfully,
            # but don't do it by default so we don't add extra quotes to ascii
            # bytestrings.  This is a bit of a hacky place to do this, but
            # it's worth it since the encoding errors that would otherwise
            # result are so useless (and tornado is fond of using utf8-encoded
            # byte strings whereever possible).
            record.message = _safe_unicode(message)
        except Exception as e:
            record.message = "Bad message (%r): %r" % (e, record.__dict__)

        record.asctime = self.formatTime(record, self.datefmt)

        if record.levelno in self._colors:
            record.color = self._colors[record.levelno]
            record.end_color = self._normal
        else:
            record.color = record.end_color = ''

        formatted = self._fmt % record.__dict__

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            # exc_text contains multiple lines.  We need to _safe_unicode
            # each line separately so that non-utf8 bytes don't cause
            # all the newlines to turn into '\n'.
            lines = [formatted.rstrip()]
            lines.extend(_safe_unicode(ln) for ln in record.exc_text.split('\n'))
            formatted = '\n'.join(lines)
        return formatted.replace("\n", "\n    ")


class DaemonFileLogHandler(logging.FileHandler):

    _LOG_FILEFORMAT = '%Y%m%d'

    def __init__(self, filename, mode='a', encoding=None, delay=0):
        super(DaemonFileLogHandler, self).__init__(filename, mode, encoding, delay)

    def get_cur_filename(self):
        t = datetime.now()
        newlogfile = "%s/%s.log" % (self.baseFilename, t.strftime(self._LOG_FILEFORMAT))
        return newlogfile

    def _open(self):
        if self.encoding is None:
            stream = open(self.get_cur_filename(), self.mode)
        else:
            stream = codecs.open(self.get_cur_filename(), self.mode, self.encoding)
        return stream

    def _get_stream(self):
        if self.stream is None:
            self.stream = self._open()
        else:
            cur_filename = self.get_cur_filename()
            if cur_filename != self.stream.name:
                self.stream = self._open()

        return self.stream

    def emit(self, record):
        try:
            self._get_stream()
        except:
            return
        return logging.StreamHandler.emit(self, record)


def add_log_handler(path, log_level=None):

    for l in [gen_log, ]:
        if l.handlers:
            for h in l.handlers:
                if h.__class__ == DaemonFileLogHandler:
                    return
        handler = DaemonFileLogHandler(path)
        handler.setFormatter(LogFormatter())
        l.addHandler(handler)
        if log_level:
            l.setLevel(log_level)


def add_stdout_handler():
    for l in [gen_log, ]:
        if l.handlers:
            for h in l.handlers:
                if h.__class__ == logging.StreamHandler:
                    return
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(LogFormatter())
        l.addHandler(handler)
        l.setLevel(logging.DEBUG)


if ConfigLog.log_to_console:
    add_stdout_handler()

# if ConfigDefault.log_to_file:
    # add_log_handler(ConfigDefault.log_path)
gen_log.setLevel(ConfigLog.log_level)
