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

"""RollerRunner Thread for requesting a new image
"""

import json
import logging
import threading

import requests


class RollerRunner(threading.Thread):
    """Thread for requesting a new image
    """

    def __init__(self, server_data, image_name, headers):
        super().__init__()
        self.log = logging.getLogger(
            "imageroller.rollerrunner.%s" % server_data.name)
        self._server_data = server_data
        self._image_name = image_name
        self._headers = headers
        self.__create_url = "{}/servers/{}/action".format(
            server_data.servers_url, server_data.server_id)

    def run(self):
        def get_create_data(image_name_):
            """Create the request data
            """
            return json.dumps({
                "createImage": {
                    "name": image_name_}
            })

        self.log.debug("Create URI: %s Header: %s Data: %s", self.__create_url,
                       self._headers, self._image_name)
        create_response = requests.post(
            self.__create_url,
            data=get_create_data(self._image_name),
            headers=self._headers)
        if create_response.status_code == 202:
            self.log.info("New image request completed successfully: %s",
                          self._image_name)
        else:
            self.log.error(
                "Failed to create new image for %s with name %s. Code: %s",
                self._server_data.name, self._image_name,
                create_response.status_code)
