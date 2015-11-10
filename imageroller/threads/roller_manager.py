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

"""Manages the RollerRunner's and queues up the servers we configured
"""

import json
import logging
import os
import pprint
import queue
import threading

import requests

import imageroller
import imageroller.data
import imageroller.threads.roller
import imageroller.utils

IDENTITY_URL = "https://identity.api.rackspacecloud.com/v2.0/tokens"


class RollerManager(threading.Thread):
    """Manager Thread for processing all of the configured servers
    """

    def __init__(self, config_data, auth_data):
        super().__init__()
        self.log = logging.getLogger(
            "imageroller.rollermanager.%s" % os.getpid())
        self.config_data = config_data
        self.__get_identity_info(auth_data)
        self.server_queue = queue.Queue()
        self.__roller_barrier = threading.Barrier(
            self.config_data.concurrent_workers + 1)
        self._rollers = []
        self.log.debug("Creating %s Rollers",
                       self.config_data.concurrent_workers)
        for _ in range(self.config_data.concurrent_workers):
            self._rollers.append(
                imageroller.threads.roller.Roller(self.server_queue,
                                                  self.__roller_barrier))
        self.__stop_lock = threading.Lock()
        self.__is_stopping = False

    def __get_identity_info(self, auth_data):
        """Set the identity info in the server_data, raising if error occurs

        :type auth_data: tuple
        :param auth_data: Auth data tuple of (username, API key)
        """

        def get_auth_body_data(hide_key=False):
            """Private function for returning the API key in the header data

            :type hide_key: bool
            :param hide_key: True to obfuscate the API key (for logging)
            """
            return json.dumps({
                "auth": {
                    "RAX-KSKEY:apiKeyCredentials": {
                        "username": auth_data[0],
                        "apiKey": "HIDDEN_KEY" if hide_key else auth_data[1]}}
            })

        # pylint: disable=no-member
        self.log.trace("Identity Request: %s data=%s headers=%s",
                       IDENTITY_URL,
                       get_auth_body_data(hide_key=True)
                       if self.log.isEnabledFor(
                           imageroller.Logger.TRACE) else "",
                       imageroller.utils.get_json_content_header()
                       if self.log.isEnabledFor(
                           imageroller.Logger.TRACE) else "")
        ident_response = requests.post(
            IDENTITY_URL,
            data=get_auth_body_data(),
            headers=imageroller.utils.get_json_content_header())
        # pylint disable=no-member
        self.log.trace("Identity Response: %s", ident_response)
        if ident_response.status_code == requests.codes.ok:
            try:
                rax_id_data = json.loads(ident_response.content.decode())
                # Enhance: This logs the Authentication Token
                self.log.trace(
                    "Identity Response JSON: %s",
                    pprint.pformat(rax_id_data) if self.log.isEnabledFor(
                        imageroller.Logger.TRACE) else "")
                for server_data in self.config_data.server_data:
                    server_data.token = rax_id_data["access"]["token"]["id"]
                    servers_url, images_url = imageroller.utils. \
                        parse_rax_id_data(rax_id_data, server_data.region)
                    if servers_url is not None and images_url is not None:
                        server_data.servers_url = servers_url
                        server_data.images_url = images_url
                    else:
                        raise Exception(
                            "Failed to determine servers_url ({})"
                            " or images_url ({}) for {} in region {}".format(
                                servers_url, images_url, server_data.name,
                                server_data.region))
            except ValueError:
                raise Exception("Failed to parse Authentication Data: %s" %
                                ident_response.content)
        else:
            raise Exception("Authentication Failure: %s %s" %
                            (ident_response.status_code,
                             ident_response.content))

    def start(self):
        super().start()
        self.log.info("Starting %s Rollers",
                      self.config_data.concurrent_workers)
        for roller_ in self._rollers:
            roller_.start()

    def run(self):
        try:
            for server_data in self.config_data.server_data:
                server_data.server_id = imageroller.utils.get_server_id(
                    server_data, self.log)
                if server_data.server_id is not None:
                    self.server_queue.put(server_data)
                else:
                    self.log.error("Unable to determine server id for %s",
                                   server_data.name)
        # pylint: disable=broad-except
        except Exception as ex:
            self.log.error("Uncaught exception during run()")
            self.log.exception(ex)
        self.stop()
        self.log.debug("Waiting for Rollers to finish")
        self.__roller_barrier.wait()
        self.log.info("Past barrier, exiting")

    def stop(self):
        """Stop the RollerManager, poisoning the workers
        """
        with self.__stop_lock:
            if not self.__is_stopping:
                self.log.info("Stopping %s Rollers",
                              self.config_data.concurrent_workers)
                for _ in range(self.config_data.concurrent_workers):
                    self.server_queue.put(None)
                self.__is_stopping = True
