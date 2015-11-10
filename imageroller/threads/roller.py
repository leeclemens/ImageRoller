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

"""Roller Thread for consuming data from the queue, produced by RollerManager
"""

import logging
import threading

import imageroller.utils


class Roller(threading.Thread):
    """Roller Thread processes data queued by RollerManager
    """

    def __init__(self, server_queue, barrier):
        super().__init__()
        self.log = logging.getLogger("imageroller.roller")
        self._server_queue = server_queue
        self.__barrier = barrier
        self.__is_running = False

    def run(self):
        self.__is_running = True
        while self.__is_running:
            server_data = self._server_queue.get()
            if server_data is None:
                self.log = logging.getLogger("imageroller.roller")
                self.log.debug("Received poison, stopping")
                self.stop()
            else:
                try:
                    self.log = logging.getLogger(
                        "imageroller.roller.%s" % server_data.name)
                    imageroller.utils.process_server(server_data, self.log)
                    self.log.info("Completed processing")
                # pylint: disable=broad-except
                except Exception as ex:
                    self.log.error("Uncaught exception processing %s",
                                   server_data.name)
                    self.log.exception(ex)
        self.log.debug("Waiting for other Rollers to finish")
        self.__barrier.wait()
        self.log.info("Exiting")

    def stop(self):
        """Set __is_running to False to stop this Thread's run loop
        """
        self.__is_running = False
