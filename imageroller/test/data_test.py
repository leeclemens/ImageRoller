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


"""Tests for imageroller.data
"""

import random
import unittest

import imageroller.data
import imageroller.utils


class ConfigDataTestCase(unittest.TestCase):
    """Test imageroller.data.ConfigData
    """

    # pylint: disable=invalid-name
    def test_concurrent_workers_value_invalid(self):
        """Test Concurrent Workers value is invalid
        """
        # noinspection PyTypeChecker
        self.assertRaises(ValueError, imageroller.data.ConfigData,
                          "invalid_value")

    # pylint: disable=invalid-name
    def test_concurrent_workers_value_zero(self):
        """Test Concurrent Workers value of 0 is invalid
        """
        self.assertRaises(ValueError, imageroller.data.ConfigData, 0)

    # pylint: disable=invalid-name
    def test_concurrent_workers_value_one(self):
        """Test Concurrent Workers value of of 1 is valid
        """
        config_data = imageroller.data.ConfigData(1)
        self.assertEqual(config_data.concurrent_workers, 1)

    # pylint: disable=invalid-name
    def test_concurrent_workers_value_random(self):
        """Test initializing Concurrent Workers value to a random value
        """
        num_workers = random.randint(2, 64)
        config_data = imageroller.data.ConfigData(num_workers)
        self.assertEqual(config_data.concurrent_workers, num_workers)

    def test_concurrent_workers_set(self):
        """Test setting a new Concurrent Workers value is invalid
        """
        config_data = imageroller.data.ConfigData(3)

        def set_concurrent_workers_test():
            """Function to facilitate unittest setting a property
            """
            # noinspection PyPropertyAccess
            config_data.concurrent_workers = 3

        self.assertRaises(AttributeError, set_concurrent_workers_test)

    def test_server_data_empty(self):
        """Test initial Server Data is empty
        """
        config_data = imageroller.data.ConfigData(1)
        self.assertEqual(len(config_data.server_data), 0)

    def test_server_data_invalid(self):
        """Test Setting ServerData to an invalid dict fails
        """
        config_data = imageroller.data.ConfigData(1)

        def set_server_data(server_data):
            """Function to facilitate unittest setting a property

            :type server_data: dict
            :param server_data: Empty dictionary for test
            """
            config_data.server_data = server_data

        self.assertRaises(ValueError, set_server_data, dict())

    def test_server_data_enabled(self):
        """Test setting ServerData as enabled and is added to the server_data
        """
        config_data = imageroller.data.ConfigData(1)
        self.assertEqual(len(config_data.server_data), 0)
        # Set auto_enable to True so it doesn't attempt to access ConfigData
        # noinspection PyTypeChecker
        config_data.server_data = imageroller.data.ServerData(
            "test", {'Region': 'US'}, True, False)
        self.assertEqual(len(config_data.server_data), 1)

    def test_server_data_not_enabled(self):
        """Test setting ServerData not enabled is not added to the server_data
        """
        # pylint: disable=fixme
        # TODO: Bug #267 - Create Valid Config object to pass to ServerData
        # config_data = imageroller.data.ConfigData(1)
        # self.assertEqual(len(config_data.server_data), 0)
        # noinspection PyTypeChecker
        # config_data.server_data = imageroller.data.ServerData("test", None,
        #                                                       False, False)
        # self.assertEqual(len(config_data.server_data), 1)
        pass

    def test_server_data_values(self):
        """Perform some verification of the value we just set
        """
        pass


class ServerDataTestCase(unittest.TestCase):
    """Write unittests for ServerData
    """
    pass


class ImageDataTestCase(unittest.TestCase):
    """Write unittests for ImageData
    """
    pass
