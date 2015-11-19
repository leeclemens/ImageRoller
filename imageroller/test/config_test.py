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

"""Test Cases related to reading configuration files
"""

import configparser
import os
import tempfile
import unittest

import imageroller.main
import imageroller.test
from imageroller import ConfigError

AUTH_NO_SECTION = """
[DEFAULT]
ApiUser = {ApiUser}
ApiKey = {ApiKey}
"""

AUTH_NO_USER = """
[AUTH]
ApiUserABSENT = {ApiUser}
ApiKey = {ApiKey}
"""

AUTH_BLANK_USER = """
[AUTH]
ApiUser =
ApiKey = {ApiKey}
"""

AUTH_NO_KEY = """
[AUTH]
ApiUser = {ApiUser}
ApiKeyABSENT = {ApiKey}
"""

AUTH_BLANK_KEY = """
[AUTH]
ApiUser = {ApiUser}
ApiKey =
"""

AUTH_VALID = """
[AUTH]
ApiUser = {ApiUser}
ApiKey = {ApiKey}
"""


def _get_parser(path):
    """Helper function to return a ConfigParser
    """
    with open(path) as path_f:
        cfg_parser = configparser.ConfigParser()
        cfg_parser.read_file(path_f)
        return cfg_parser


class AuthConfigTestCase(unittest.TestCase):
    """Test Case related to reading and parsing the Auth Config
    """

    @classmethod
    def setUpClass(cls):
        """Gets temp file paths for our config files
        """
        cls._auth_no_section = tempfile.mkstemp(suffix=".conf",
                                                prefix="imageroller_auth_")[1]
        cls._auth_no_user = tempfile.mkstemp(suffix=".conf",
                                             prefix="imageroller_auth_")[1]
        cls._auth_blank_user = tempfile.mkstemp(suffix=".conf",
                                                prefix="imageroller_auth_")[1]
        cls._auth_no_key = tempfile.mkstemp(suffix=".conf",
                                            prefix="imageroller_auth_")[1]
        cls._auth_blank_key = tempfile.mkstemp(suffix=".conf",
                                               prefix="imageroller_auth_")[1]
        cls._auth_valid = tempfile.mkstemp(suffix=".conf",
                                           prefix="imageroller_auth_")[1]
        cls._api_data = {"ApiUser": "SomeTestRAXUsername",
                         "ApiKey": imageroller.test.generate_api_key()}
        cls._write_config(cls._auth_no_section, AUTH_NO_SECTION)
        cls._write_config(cls._auth_no_user, AUTH_NO_USER)
        cls._write_config(cls._auth_blank_user, AUTH_BLANK_USER)
        cls._write_config(cls._auth_no_key, AUTH_NO_KEY)
        cls._write_config(cls._auth_blank_key, AUTH_BLANK_KEY)
        cls._write_config(cls._auth_valid, AUTH_VALID)

    @classmethod
    def tearDownClass(cls):
        """Cleans up our test config files
        """
        os.remove(cls._auth_no_section)
        os.remove(cls._auth_no_user)
        os.remove(cls._auth_blank_user)
        os.remove(cls._auth_no_key)
        os.remove(cls._auth_blank_key)
        os.remove(cls._auth_valid)

    @classmethod
    def _write_config(cls, config_path, config_text):
        """Helper function to write the test config data
        """
        with open(config_path, "w") as config_f:
            config_f.writelines(config_text.format(**cls._api_data))

    def test_no_section(self):
        """Test auth config with no [AUTH] section
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_authconfig(
                _get_parser(self._auth_no_section))
        self.assertEqual(str(cm.exception), "AuthConfig must contain [AUTH]")

    def test_no_user(self):
        """Test auth config with no ApiUser key
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_authconfig(
                _get_parser(self._auth_no_user))
        self.assertEqual(str(cm.exception), "AuthConfig must contain ApiUser")

    def test_blank_user(self):
        """Test auth config with a blank user
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_authconfig(
                _get_parser(self._auth_blank_user))
        self.assertEqual(str(cm.exception), "AuthConfig must contain ApiUser")

    def test_no_key(self):
        """Test auth config with no ApiKey key
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_authconfig(
                _get_parser(self._auth_no_key))
        self.assertEqual(str(cm.exception), "AuthConfig must contain ApiKey")

    def test_blank_key(self):
        """Test auth config with no a blank key
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_authconfig(
                _get_parser(self._auth_blank_key))
        self.assertEqual(str(cm.exception), "AuthConfig must contain ApiKey")

    def test_valid(self):
        """Test reading the correct values from a valid auth config
        """
        auth_tuple = imageroller.main.read_authconfig(
            _get_parser(self._auth_valid))
        self.assertTupleEqual(auth_tuple, (self._api_data["ApiUser"],
                                           self._api_data["ApiKey"]))
