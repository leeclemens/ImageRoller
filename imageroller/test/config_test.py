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
import os
import random
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

AUTH_DATA = {
    "ApiUser": "TestRAXUsername",
    "ApiKey": imageroller.test.generate_api_key()}
CONFIG_DATA = {
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


class ReadConfigsTestCase(unittest.TestCase):
    """Test Case calling parent function for reading configs

    Specific test cases are handled by more specific test cases
    """

    @classmethod
    def setUpClass(cls):
        """Gets temp file paths for our config files
        """
        cls._config = imageroller.test.write_config(
            "config", CONFIG_SERVER_VALID_MINIMAL, CONFIG_DATA)
        cls._auth = imageroller.test.write_config(
            "auth", AUTH_VALID, AUTH_DATA)

    @classmethod
    def tearDownClass(cls):
        """Cleans up our test config files
        """
        os.remove(cls._config)
        os.remove(cls._auth)

    def test_read_valid_configs(self):
        """Test main call to read_configs() which returns both config and auth
        """
        args = argparse.Namespace(server=None, force=False)
        with open(self._config) as config_f:
            with open(self._auth) as auth_config_f:
                (config_data, auth_tuple) = imageroller.main.read_configs(
                    args,
                    config_f,
                    auth_config_f)
                self.assertEqual(config_data.concurrent_workers,
                                 CONFIG_DATA["ConcurrentWorkers"])
                self.assertEqual(len(config_data.server_data), 1)
                self.assertTupleEqual(auth_tuple, (AUTH_DATA["ApiUser"],
                                                   AUTH_DATA["ApiKey"]))


class ServerConfigTestCase(unittest.TestCase):
    """Test Case related to reading and parsing the Auth Config
    """

    @classmethod
    def setUpClass(cls):
        """Gets temp file paths for our config files
        """
        cls._no_default = imageroller.test.write_config(
            "config", CONFIG_NO_DEFAULT, CONFIG_DATA)
        cls._no_workers = imageroller.test.write_config(
            "config", CONFIG_NO_WORKERS, CONFIG_DATA)
        cls._zero_workers = imageroller.test.write_config(
            "config", CONFIG_ZERO_WORKERS, CONFIG_DATA)
        cls._no_server = imageroller.test.write_config(
            "config", CONFIG_NO_SERVER, CONFIG_DATA)
        cls._server_no_save_timeout = imageroller.test.write_config(
            "config", CONFIG_SERVER_NO_SAVE_TIMEOUT, CONFIG_DATA)
        cls._server_no_retain_image = imageroller.test.write_config(
            "config", CONFIG_SERVER_NO_RETAIN_IMAGE, CONFIG_DATA)
        cls._server_no_region = imageroller.test.write_config(
            "config", CONFIG_SERVER_NO_REGION, CONFIG_DATA)
        cls._server_valid_minimal = imageroller.test.write_config(
            "config", CONFIG_SERVER_VALID_MINIMAL, CONFIG_DATA)
        cls._server_valid_override = imageroller.test.write_config(
            "config", CONFIG_SERVER_VALID_OVERRIDE, CONFIG_DATA)

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
        # Our test command-line args (functions may safely alter values)
        self._cmd_args = argparse.Namespace(server=None, force=False)

    def test_no_default(self):
        """Test config with no [DEFAULT] section

        Subsequently, the ConcurrentWorkers will not be defined
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_config(
                self._cmd_args,
                imageroller.test.get_config_parser(self._no_default))
        # ConcurrentWorkers is the first value that is checked
        self.assertEqual(str(cm.exception),
                         "Config must contain ConcurrentWorkers")

    def test_no_workers(self):
        """Test config with no ConcurrentWorkers key
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_config(
                self._cmd_args,
                imageroller.test.get_config_parser(self._no_workers))
        self.assertEqual(str(cm.exception),
                         "Config must contain ConcurrentWorkers")

    def test_zero_workers(self):
        """Test config with ConcurrentWorkers = 0
        """
        with self.assertRaises(ValueError) as cm:
            imageroller.main.read_config(
                self._cmd_args,
                imageroller.test.get_config_parser(self._zero_workers))
        self.assertEqual(str(cm.exception),
                         "Concurrent workers must be greater than 0")

    def test_no_server(self):
        """Test config with no server sections
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_config(
                self._cmd_args,
                imageroller.test.get_config_parser(self._no_server))
        self.assertEqual(str(cm.exception),
                         "You must configure at least one server")

    def test_no_server_cmdline(self):
        """Test config with no server sections - cmdline

        Server is specified on the command line that is not configured
        """
        invalid_server = "invalid.example.com"
        self._cmd_args.server = invalid_server
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_config(
                self._cmd_args,
                imageroller.test.get_config_parser(self._no_server))
        self.assertEqual(
            str(cm.exception),
            "The specified server is not configured: %s" % invalid_server)

    def test_server_no_save_timeout(self):
        """Test server config with no SaveTimeoutMinutes
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_config(self._cmd_args,
                                         imageroller.test.get_config_parser(
                                             self._server_no_save_timeout))
        self.assertEqual(
            str(cm.exception),
            "Server Config for %s is missing SaveTimeoutMinutes" %
            CONFIG_DATA["TestServerFQDN"])

    def test_server_no_retain_image(self):
        """Test server config with no RetainImageMinutes
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_config(self._cmd_args,
                                         imageroller.test.get_config_parser(
                                             self._server_no_retain_image))
        self.assertEqual(
            str(cm.exception),
            "Server Config for %s is missing RetainImageMinutes" %
            CONFIG_DATA["TestServerFQDN"])

    def test_server_no_region(self):
        """Test server config with no Region
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_config(self._cmd_args,
                                         imageroller.test.get_config_parser(
                                             self._server_no_region))
        self.assertEqual(
            str(cm.exception),
            "Server Config for %s is missing Region" %
            CONFIG_DATA["TestServerFQDN"])

    def test_server_valid_minimal(self):
        """Test config with minimal configs

        Also tests auto_enable property being set properly
        """
        config_data = imageroller.main.read_config(
            self._cmd_args,
            imageroller.test.get_config_parser(self._server_valid_minimal))
        self.assertEqual(config_data.concurrent_workers,
                         CONFIG_DATA["ConcurrentWorkers"])
        self.assertEqual(len(config_data.server_data), 1)
        # Test minutes -> seconds in property getters
        # pylint: disable=not-an-iterable
        for server_data in config_data.server_data:
            self.assertEqual(server_data.save_timeout_seconds,
                             int(CONFIG_DATA["SaveTimeoutMinutes"]) * 60)
            self.assertEqual(server_data.retain_image_seconds,
                             int(CONFIG_DATA["RetainImageMinutes"]) * 60)
            self.assertFalse(server_data.auto_enable)

    def test_server_valid_cmdline(self):
        """Test config with minimal configs, but specified on command-line

        Also tests auto_enable property being set properly
        """
        self._cmd_args.server = CONFIG_DATA["TestServerFQDN"]
        config_data = imageroller.main.read_config(
            self._cmd_args,
            imageroller.test.get_config_parser(self._server_valid_minimal))
        # pylint: disable=not-an-iterable
        for server_data in config_data.server_data:
            self.assertEqual(server_data.save_timeout_seconds,
                             int(CONFIG_DATA["SaveTimeoutMinutes"]) * 60)
            self.assertEqual(server_data.retain_image_seconds,
                             int(CONFIG_DATA["RetainImageMinutes"]) * 60)
            self.assertTrue(server_data.auto_enable)

    # pylint: disable=not-an-iterable
    def test_server_override_general(self):
        """Test that config values are overridden properly
        """
        # Sanity check our override values do not overlap
        self.assertNotEqual(CONFIG_DATA["ConcurrentWorkers"],
                            CONFIG_DATA["OverrideConcurrentWorkers"])
        self.assertNotEqual(CONFIG_DATA["SaveTimeoutMinutes"],
                            CONFIG_DATA["OverrideSaveTimeoutMinutes"])
        self.assertNotEqual(CONFIG_DATA["RetainImageMinutes"],
                            CONFIG_DATA["OverrideRetainImageMinutes"])
        self.assertNotEqual(CONFIG_DATA["Region"],
                            CONFIG_DATA["OverrideRegion"])
        config_data = imageroller.main.read_config(
            self._cmd_args,
            imageroller.test.get_config_parser(
                self._server_valid_override))
        # Verify default disabled server is not included
        self.assertNotIn(
            CONFIG_DATA["OverrideNotExistFQDN"],
            [server_data.name for server_data in
             config_data.server_data])
        # Sanity check we have every server's config we expect to have
        self.assertSetEqual(
            set([server_data.name for server_data in
                 config_data.server_data]),
            {CONFIG_DATA["OverrideWorkersFQDN"],
             CONFIG_DATA["OverrideSaveTimeoutFQDN"],
             CONFIG_DATA["OverrideRetainImageFQDN"],
             CONFIG_DATA["OverrideRegionFQDN"]},
        )
        # Smoke test they are all enabled
        self.assertTrue(all([server_data.enabled
                             for server_data in
                             config_data.server_data]))

    # pylint: disable=not-an-iterable
    def test_server_override_workers(self):
        """Test that config values are overridden properly
        """
        # Sanity check our override values do not overlap
        self.assertNotEqual(CONFIG_DATA["ConcurrentWorkers"],
                            CONFIG_DATA["OverrideConcurrentWorkers"])
        config_data = imageroller.main.read_config(
            self._cmd_args,
            imageroller.test.get_config_parser(self._server_valid_override))
        # ConcurrentWorkers is required to be set in [DEFAULT] (globally)
        # Smoke test we can't override it in the first enabled server config
        self.assertEqual(config_data.concurrent_workers,
                         CONFIG_DATA["ConcurrentWorkers"])

    # pylint: disable=not-an-iterable, invalid-name
    def test_server_override_save_timeout(self):
        """Test that config values are overridden properly
        """
        # Sanity check our override values do not overlap
        self.assertNotEqual(CONFIG_DATA["SaveTimeoutMinutes"],
                            CONFIG_DATA["OverrideSaveTimeoutMinutes"])
        config_data = imageroller.main.read_config(
            self._cmd_args,
            imageroller.test.get_config_parser(self._server_valid_override))
        # Test Save Timeout Minutes was overridden
        self.assertEqual(
            CONFIG_DATA["OverrideSaveTimeoutMinutes"],
            [server_data.save_timeout_minutes
             for server_data in config_data.server_data
             if server_data.name ==
             CONFIG_DATA["OverrideSaveTimeoutFQDN"]]
            [0])

    # pylint: disable=not-an-iterable
    def test_server_override_retain(self):
        """Test that config values are overridden properly
        """
        # Sanity check our override values do not overlap
        self.assertNotEqual(CONFIG_DATA["RetainImageMinutes"],
                            CONFIG_DATA["OverrideRetainImageMinutes"])
        config_data = imageroller.main.read_config(
            self._cmd_args,
            imageroller.test.get_config_parser(
                self._server_valid_override))
        # Test Retain Image Minutes was overridden
        self.assertEqual(
            CONFIG_DATA["OverrideRetainImageMinutes"],
            [server_data.retain_image_minutes
             for server_data in config_data.server_data
             if server_data.name ==
             CONFIG_DATA["OverrideRetainImageFQDN"]]
            [0])

    # pylint: disable=not-an-iterable
    def test_server_override_region(self):
        """Test that config values are overridden properly
        """
        # Sanity check our override values do not overlap
        self.assertNotEqual(CONFIG_DATA["Region"],
                            CONFIG_DATA["OverrideRegion"])
        config_data = imageroller.main.read_config(
            self._cmd_args,
            imageroller.test.get_config_parser(
                self._server_valid_override))
        # Test Region was overridden
        self.assertEqual(
            CONFIG_DATA["OverrideRegion"],
            [server_data.region
             for server_data in config_data.server_data
             if server_data.name ==
             CONFIG_DATA["OverrideRegionFQDN"]]
            [0])


class AuthConfigTestCase(unittest.TestCase):
    """Test Case related to reading and parsing the Auth Config
    """

    @classmethod
    def setUpClass(cls):
        """Gets temp file paths for our config files
        """
        cls._no_section = imageroller.test.write_config(
            "auth", AUTH_NO_SECTION, AUTH_DATA)
        cls._no_user = imageroller.test.write_config(
            "auth", AUTH_NO_USER, AUTH_DATA)
        cls._blank_user = imageroller.test.write_config(
            "auth", AUTH_BLANK_USER, AUTH_DATA)
        cls._no_key = imageroller.test.write_config(
            "auth", AUTH_NO_KEY, AUTH_DATA)
        cls._blank_key = imageroller.test.write_config(
            "auth", AUTH_BLANK_KEY, AUTH_DATA)
        cls._valid = imageroller.test.write_config(
            "auth", AUTH_VALID, AUTH_DATA)

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
                imageroller.test.get_config_parser(self._no_section))
        self.assertEqual(str(cm.exception), "AuthConfig must contain [AUTH]")

    def test_no_user(self):
        """Test auth config with no ApiUser key
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_authconfig(
                imageroller.test.get_config_parser(self._no_user))
        self.assertEqual(str(cm.exception), "AuthConfig must contain ApiUser")

    def test_blank_user(self):
        """Test auth config with a blank user
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_authconfig(
                imageroller.test.get_config_parser(self._blank_user))
        self.assertEqual(str(cm.exception), "AuthConfig must contain ApiUser")

    def test_no_key(self):
        """Test auth config with no ApiKey key
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_authconfig(
                imageroller.test.get_config_parser(self._no_key))
        self.assertEqual(str(cm.exception), "AuthConfig must contain ApiKey")

    def test_blank_key(self):
        """Test auth config with no a blank key
        """
        with self.assertRaises(ConfigError) as cm:
            imageroller.main.read_authconfig(
                imageroller.test.get_config_parser(self._blank_key))
        self.assertEqual(str(cm.exception), "AuthConfig must contain ApiKey")

    def test_valid(self):
        """Test reading the correct values from a valid auth config
        """
        auth_tuple = imageroller.main.read_authconfig(
            imageroller.test.get_config_parser(self._valid))
        self.assertTupleEqual(auth_tuple, (AUTH_DATA["ApiUser"],
                                           AUTH_DATA["ApiKey"]))
