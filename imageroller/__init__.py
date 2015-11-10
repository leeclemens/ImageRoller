# The MIT License (MIT)
#
# Copyright (c) 2015 Lee Clemens Computing Services, LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""ImageRoller module
"""

import logging


class Logger(logging.getLoggerClass()):
    """ImageRoller Logger class
    """
    TRACE = 5
    LOG_NAME_TRACE = "TRACE"

    def __init__(self, name, level=logging.NOTSET):
        """Add our custom level
        """
        super().__init__(name, level)
        logging.addLevelName(Logger.TRACE, Logger.LOG_NAME_TRACE)

    def trace(self, msg, *args, **kwargs):
        """Log at our custom level

        :param msg: msg passed to _log()
        :param args: args passed to _log()
        :param kwargs: kwargs passed to _log()
        """
        if self.isEnabledFor(Logger.TRACE):
            self._log(Logger.TRACE, msg, args, **kwargs)


logging.setLoggerClass(Logger)
