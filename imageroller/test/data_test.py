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


import random
import unittest

import imageroller.data
import imageroller.utils


class ConfigDataTestCase(unittest.TestCase):
    def testConcurrentValueInvalid(self):
        # noinspection PyTypeChecker
        self.assertRaises(ValueError, imageroller.data.ConfigData,
                          "invalid_value")

    def testConcurrentWorkersValueZero(self):
        self.assertRaises(ValueError, imageroller.data.ConfigData, 0)

    def testConcurrentWorkersValueOne(self):
        config_data = imageroller.data.ConfigData(1)
        self.assertEqual(config_data.concurrent_workers, 1)

    def testConcurrentWorkersValueRandom(self):
        num_workers = random.randint(2, 64)
        config_data = imageroller.data.ConfigData(num_workers)
        self.assertEqual(config_data.concurrent_workers, num_workers)

    def testConcurrentWorkersSet(self):
        config_data = imageroller.data.ConfigData(3)

        def set_concurrent_workers_test():
            # noinspection PyPropertyAccess
            config_data.concurrent_workers = 3

        self.assertRaises(AttributeError, set_concurrent_workers_test)

    def testServerDataEmpty(self):
        config_data = imageroller.data.ConfigData(1)
        self.assertEqual(len(config_data.server_data), 0)

    def testServerDataInvalid(self):
        config_data = imageroller.data.ConfigData(1)

        def set_server_data(server_data):
            config_data.server_data = server_data

        self.assertRaises(ValueError, set_server_data, dict())

    def testServerDataEnabled(self):
        config_data = imageroller.data.ConfigData(1)
        self.assertEqual(len(config_data.server_data), 0)
        # Set auto_enable to True so it doesn't attempt to access ConfigData
        # noinspection PyTypeChecker
        config_data.server_data = imageroller.data.ServerData("test", None,
                                                              True, False)
        self.assertEqual(len(config_data.server_data), 1)

    def testServerDataNotEnabled(self):
        # TODO: Create Valid Config object to pass to ServerData()
        # config_data = imageroller.data.ConfigData(1)
        # self.assertEqual(len(config_data.server_data), 0)
        # noinspection PyTypeChecker
        # config_data.server_data = imageroller.data.ServerData("test", None,
        #                                                       False, False)
        # self.assertEqual(len(config_data.server_data), 1)
        pass

    def testServerDataValues(self):
        # TODO: Perform some verification of the value we just set
        pass


class ServerDataTestCase(unittest.TestCase):
    # TODO: Write unittests for ServerData
    pass


class ImageDataTestCase(unittest.TestCase):
    # TODO: Write unittests for ImageData
    pass
