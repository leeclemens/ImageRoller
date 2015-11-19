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

import argparse
import configparser
import os
import random
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

CONFIG_NO_DEFAULT = """
[DEFAULT_ABSENT]
foo = bar
"""

CONFIG_NO_WORKERS = """
[DEFAULT]
ConcurrentWorkers_ABSENT = {ConcurrentWorkers}
"""

CONFIG_ZERO_WORKERS = """
[DEFAULT]
ConcurrentWorkers = 0
"""

CONFIG_NO_SERVER = """
[DEFAULT]
ConcurrentWorkers = {ConcurrentWorkers}
"""

CONFIG_SERVER_NO_SAVE_TIMEOUT = """
[DEFAULT]
ConcurrentWorkers = {ConcurrentWorkers}

[{TestServerFQDN}]
RetainImageMinutes = {RetainImageMinutes}
Region = {Region}
"""

CONFIG_SERVER_NO_RETAIN_IMAGE = """
[DEFAULT]
ConcurrentWorkers = {ConcurrentWorkers}

[{TestServerFQDN}]
SaveTimeoutMinutes = {SaveTimeoutMinutes}
Region = {Region}
"""

CONFIG_SERVER_NO_REGION = """
[DEFAULT]
ConcurrentWorkers = {ConcurrentWorkers}

[{TestServerFQDN}]
SaveTimeoutMinutes = {SaveTimeoutMinutes}
RetainImageMinutes = {RetainImageMinutes}
"""

CONFIG_SERVER_VALID_MINIMAL = """
[DEFAULT]
ConcurrentWorkers = {ConcurrentWorkers}
SaveTimeoutMinutes = {SaveTimeoutMinutes}
RetainImageMinutes = {RetainImageMinutes}

[{TestServerFQDN}]
Enabled = True
Region = {Region}
"""

CONFIG_SERVER_VALID_OVERRIDE = """
[DEFAULT]
ConcurrentWorkers = {ConcurrentWorkers}
SaveTimeoutMinutes = {SaveTimeoutMinutes}
RetainImageMinutes = {RetainImageMinutes}
Region = {Region}

[{OverrideNotExistFQDN}]
ConcurrentWorkers = {OverrideConcurrentWorkers}

[{OverrideWorkersFQDN}]
Enabled = True
ConcurrentWorkers = {OverrideConcurrentWorkers}

[{OverrideSaveTimeoutFQDN}]
Enabled = True
SaveTimeoutMinutes = {OverrideSaveTimeoutMinutes}

[{OverrideRetainImageFQDN}]
Enabled = True
RetainImageMinutes = {OverrideRetainImageMinutes}

[{OverrideRegionFQDN}]
Enabled = True
Region = {OverrideRegion}
"""


def _mkstemp(conf_type):
    return tempfile.mkstemp(suffix=".conf",
                            prefix="imageroller_%s_" % conf_type)[1]


def _write_config(config_path, config_text, args):
    """Helper function to write the test config data
    """
    with open(config_path, "w") as config_f:
        config_f.writelines(config_text.format(**args))


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
        cls._no_section = _mkstemp("auth")
        cls._no_user = _mkstemp("auth")
        cls._blank_user = _mkstemp("auth")
        cls._no_key = _mkstemp("auth")
        cls._blank_key = _mkstemp("auth")
        cls._valid = _mkstemp("auth")
        cls._auth_data = {"ApiUser": "SomeTestRAXUsername",
                          "ApiKey": imageroller.test.generate_api_key()}
        _write_config(cls._no_section, AUTH_NO_SECTION, cls._auth_data)
        _write_config(cls._no_user, AUTH_NO_USER, cls._auth_data)
        _write_config(cls._blank_user, AUTH_BLANK_USER, cls._auth_data)
        _write_config(cls._no_key, AUTH_NO_KEY, cls._auth_data)
        _write_config(cls._blank_key, AUTH_BLANK_KEY, cls._auth_data)
        _write_config(cls._valid, AUTH_VALID, cls._auth_data)

    @classmethod
    def tearDownClass(cls):
        """Cleans up our test config files
        """
        os.remove(cls._no_section)
        os.remove(cls._no_user)
        os.remove(cls._blank_user)
        os.remove(cls._no_key)
        os.remove(cls._blank_key)
        os.remove(cls._valid)

    def test_no_section(self):
        """Test auth config with no [AUTH] section
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_authconfig(
                _get_parser(self._no_section))
        self.assertEqual(str(cm.exception), "AuthConfig must contain [AUTH]")

    def test_no_user(self):
        """Test auth config with no ApiUser key
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_authconfig(
                _get_parser(self._no_user))
        self.assertEqual(str(cm.exception), "AuthConfig must contain ApiUser")

    def test_blank_user(self):
        """Test auth config with a blank user
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_authconfig(
                _get_parser(self._blank_user))
        self.assertEqual(str(cm.exception), "AuthConfig must contain ApiUser")

    def test_no_key(self):
        """Test auth config with no ApiKey key
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_authconfig(
                _get_parser(self._no_key))
        self.assertEqual(str(cm.exception), "AuthConfig must contain ApiKey")

    def test_blank_key(self):
        """Test auth config with no a blank key
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_authconfig(
                _get_parser(self._blank_key))
        self.assertEqual(str(cm.exception), "AuthConfig must contain ApiKey")

    def test_valid(self):
        """Test reading the correct values from a valid auth config
        """
        auth_tuple = imageroller.main.read_authconfig(
            _get_parser(self._valid))
        self.assertTupleEqual(auth_tuple, (self._auth_data["ApiUser"],
                                           self._auth_data["ApiKey"]))


class ServerConfigTestCase(unittest.TestCase):
    """Test Case related to reading and parsing the Auth Config
    """

    @classmethod
    def setUpClass(cls):
        """Gets temp file paths for our config files
        """
        cls._no_default = _mkstemp("config")
        cls._no_workers = _mkstemp("config")
        cls._zero_workers = _mkstemp("config")
        cls._no_server = _mkstemp("config")
        cls._server_no_save_timeout = _mkstemp("config")
        cls._server_no_retain_image = _mkstemp("config")
        cls._server_no_region = _mkstemp("config")
        cls._server_valid_minimal = _mkstemp("config")
        cls._server_valid_override = _mkstemp("config")
        cls._config_data = {
            "ConcurrentWorkers": random.randint(4, 32),
            "TestServerFQDN": "test.example.com",
            "SaveTimeoutMinutes": 60,
            "RetainImageMinutes": 120,
            "Region": "DFW",
            # Overridden values for test_server_override()
            "OverrideConcurrentWorkers": 3,
            "OverrideSaveTimeoutMinutes": 20,
            "OverrideRetainImageMinutes": 45,
            "OverrideRegion": "IAD",
            "OverrideNotExistFQDN": "not.exist.example.com",
            "OverrideWorkersFQDN": "workers.example.com",
            "OverrideSaveTimeoutFQDN": "save.example.com",
            "OverrideRetainImageFQDN": "retain.example.time",
            "OverrideRegionFQDN": "region.example.time",
        }
        _write_config(cls._no_default, CONFIG_NO_DEFAULT, cls._config_data)
        _write_config(cls._no_workers, CONFIG_NO_WORKERS, cls._config_data)
        _write_config(cls._zero_workers, CONFIG_ZERO_WORKERS, cls._config_data)
        _write_config(cls._no_server, CONFIG_NO_SERVER, cls._config_data)
        _write_config(cls._server_no_save_timeout,
                      CONFIG_SERVER_NO_SAVE_TIMEOUT, cls._config_data)
        _write_config(cls._server_no_retain_image,
                      CONFIG_SERVER_NO_RETAIN_IMAGE, cls._config_data)
        _write_config(cls._server_no_region, CONFIG_SERVER_NO_REGION,
                      cls._config_data)
        _write_config(cls._server_valid_minimal, CONFIG_SERVER_VALID_MINIMAL,
                      cls._config_data)
        _write_config(cls._server_valid_override, CONFIG_SERVER_VALID_OVERRIDE,
                      cls._config_data)

    @classmethod
    def tearDownClass(cls):
        """Cleans up our test config files
        """
        os.remove(cls._no_default)
        os.remove(cls._no_workers)
        os.remove(cls._zero_workers)
        os.remove(cls._no_server)
        os.remove(cls._server_no_save_timeout)
        os.remove(cls._server_no_retain_image)
        os.remove(cls._server_no_region)
        os.remove(cls._server_valid_minimal)
        os.remove(cls._server_valid_override)

    def setUp(self):
        # Our test command-line args (may safely be altered per test func)
        self._cmd_args = argparse.Namespace(server=None, force=False)

    def test_no_default(self):
        """Test config with no [DEFAULT] section

        Subsequently, the ConcurrentWorkers will not be defined
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_config(self._cmd_args,
                                         _get_parser(self._no_default))
        # ConcurrentWorkers is the first value that is checked
        self.assertEqual(str(cm.exception),
                         "Config must contain ConcurrentWorkers")

    def test_no_workers(self):
        """Test config with no ConcurrentWorkers key
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_config(self._cmd_args,
                                         _get_parser(self._no_workers))
        self.assertEqual(str(cm.exception),
                         "Config must contain ConcurrentWorkers")

    def test_zero_workers(self):
        """Test config with ConcurrentWorkers = 0
        """
        with self.assertRaises(ValueError) as cm:
            imageroller.main.read_config(self._cmd_args,
                                         _get_parser(self._zero_workers))
        self.assertEqual(str(cm.exception),
                         "Concurrent workers must be greater than 0")

    def test_no_server(self):
        """Test config with no server sections
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_config(self._cmd_args,
                                         _get_parser(self._no_server))
        self.assertEqual(str(cm.exception),
                         "You must configure at least one server")

    def test_no_server_cmdline(self):
        """Test config with no server sections - cmdline

        Server is specified on the command line that is not configured
        """
        invalid_server = "invalid.example.com"
        self._cmd_args.server = invalid_server
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_config(self._cmd_args,
                                         _get_parser(self._no_server))
        self.assertEqual(
            str(cm.exception),
            "The specified server is not configured: %s" % invalid_server)

    def test_server_no_save_timeout(self):
        """Test server config with no SaveTimeoutMinutes
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_config(self._cmd_args, _get_parser(
                self._server_no_save_timeout))
        self.assertEqual(
            str(cm.exception),
            "Server Config for %s is missing SaveTimeoutMinutes" %
            self._config_data["TestServerFQDN"])

    def test_server_no_retain_image(self):
        """Test server config with no RetainImageMinutes
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_config(self._cmd_args, _get_parser(
                self._server_no_retain_image))
        self.assertEqual(
            str(cm.exception),
            "Server Config for %s is missing RetainImageMinutes" %
            self._config_data["TestServerFQDN"])

    def test_server_no_region(self):
        """Test server config with no Region
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_config(self._cmd_args,
                                         _get_parser(self._server_no_region))
        self.assertEqual(
            str(cm.exception),
            "Server Config for %s is missing Region" %
            self._config_data["TestServerFQDN"])

    def test_server_valid_minimal(self):
        """Test config with minimal configs

        Also tests auto_enable property being set properly
        """
        config_data = imageroller.main.read_config(
            self._cmd_args,
            _get_parser(self._server_valid_minimal))
        self.assertEqual(config_data.concurrent_workers,
                         self._config_data["ConcurrentWorkers"])
        self.assertEqual(len(config_data.server_data), 1)
        # Test minutes -> seconds in property getters
        for server_data in config_data.server_data:
            self.assertEqual(server_data.save_timeout_seconds,
                             int(self._config_data["SaveTimeoutMinutes"]) * 60)
            self.assertEqual(server_data.retain_image_seconds,
                             int(self._config_data["RetainImageMinutes"]) * 60)
            self.assertFalse(server_data.auto_enable)

    def test_server_valid_cmdline(self):
        """Test config with minimal configs, but specified on command-line

        Also tests auto_enable property being set properly
        """
        self._cmd_args.server = self._config_data["TestServerFQDN"]
        config_data = imageroller.main.read_config(
            self._cmd_args,
            _get_parser(self._server_valid_minimal))
        for server_data in config_data.server_data:
            self.assertEqual(server_data.save_timeout_seconds,
                             int(self._config_data["SaveTimeoutMinutes"]) * 60)
            self.assertEqual(server_data.retain_image_seconds,
                             int(self._config_data["RetainImageMinutes"]) * 60)
            self.assertTrue(server_data.auto_enable)

    def test_server_override(self):
        """Test that config values are overridden properly
        """
        # Sanity check our override values do not overlap
        self.assertNotEqual(self._config_data["ConcurrentWorkers"],
                            self._config_data["OverrideConcurrentWorkers"])
        self.assertNotEqual(self._config_data["SaveTimeoutMinutes"],
                            self._config_data["OverrideSaveTimeoutMinutes"])
        self.assertNotEqual(self._config_data["RetainImageMinutes"],
                            self._config_data["OverrideRetainImageMinutes"])
        self.assertNotEqual(self._config_data["Region"],
                            self._config_data["OverrideRegion"])
        config_data = imageroller.main.read_config(
            self._cmd_args,
            _get_parser(self._server_valid_override))
        # Verify default disabled server is not included
        self.assertNotIn(
            self._config_data["OverrideNotExistFQDN"],
            [server_data.name for server_data in config_data.server_data])
        # Sanity check we have every server's config we expect to have
        self.assertSetEqual(
            set([server_data.name for server_data in config_data.server_data]),
            {self._config_data["OverrideWorkersFQDN"],
             self._config_data["OverrideSaveTimeoutFQDN"],
             self._config_data["OverrideRetainImageFQDN"],
             self._config_data["OverrideRegionFQDN"]},
        )
        # Smoke test they are all enabled
        self.assertTrue(all([server_data.enabled
                             for server_data in config_data.server_data]))
        # ConcurrentWorkers is required to be set in [DEFAULT] (globally)
        # Smoke test we can't override it in the first enabled server config
        self.assertEqual(config_data.concurrent_workers,
                         self._config_data["ConcurrentWorkers"])
        # Test Save Timeout Minutes was overridden
        self.assertEqual(
            self._config_data["OverrideSaveTimeoutMinutes"],
            [server_data.save_timeout_minutes
             for server_data in config_data.server_data
             if server_data.name ==
             self._config_data["OverrideSaveTimeoutFQDN"]]
            [0])
        # Test Retain Image Minutes was overridden
        self.assertEqual(
            self._config_data["OverrideRetainImageMinutes"],
            [server_data.retain_image_minutes
             for server_data in config_data.server_data
             if server_data.name ==
             self._config_data["OverrideRetainImageFQDN"]]
            [0])
        # Test Region was overridden
        self.assertEqual(
            self._config_data["OverrideRegion"],
            [server_data.region
             for server_data in config_data.server_data
             if server_data.name ==
             self._config_data["OverrideRegionFQDN"]]
            [0])
