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

"""Tests for imageroller.utils
"""

import datetime
import unittest

import imageroller.test
import imageroller.test.config_test as config_test
import imageroller.utils


class HeaderTestCase(unittest.TestCase):
    """Header related tests
    """

    def test_json_content_header(self):
        """Test JSON Content-Header
        """
        self.assertDictEqual(
            imageroller.utils.get_json_content_header(),
            {"Content-Type": "application/json"}
        )

    def test_auth_token_header(self):
        """Test Auth Header
        """
        fake_token = imageroller.test.generate_api_key()
        self.assertDictEqual(
            imageroller.utils.get_auth_token_header(fake_token),
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Auth-Token": fake_token,
            }
        )


class ParseRaxIdTestCase(unittest.TestCase):
    """Rackspace Identity response related tests
    """

    @classmethod
    def setUpClass(cls):
        """Setup a Rackspace-like identity response
        """
        cls._servers_url_ord = \
            "https://ord.servers.api.rackspacecloud.com/v2/1100111"
        cls._images_url_ord = \
            "https://ord.images.api.rackspacecloud.com/v2"
        cls._servers_url_images_missing = \
            "https://hkg.servers.api.rackspacecloud.com/v2/1100111"
        cls._images_url_servers_missing = \
            "https://syd.images.api.rackspacecloud.com/v2"

        cls._test_token = imageroller.test.generate_token()

        cls._identity_response = {
            'access': {
                'serviceCatalog':
                    [
                        {
                            'endpoints': [
                                {
                                    'publicURL': '{0:s}'.format(
                                        cls._servers_url_ord),
                                    'region': 'ORD',
                                    'tenantId': '1100111',
                                    'versionId': '2',
                                    'versionInfo': 'version_info_ord',
                                    'versionList': 'version_list_ord'},
                                {
                                    'publicURL': '{0:s}'.format(
                                        cls._servers_url_images_missing),
                                    'region': 'HKG',
                                    'tenantId': '1100111',
                                    'versionId': '2',
                                    'versionInfo': 'version_info_hkg',
                                    'versionList': 'version_list_hkg'}
                            ],
                            'name': 'cloudServersOpenStack',
                            'type': 'compute'},
                        {
                            'endpoints': [
                                {
                                    'publicURL': '{0:s}'.format(
                                        cls._images_url_ord),
                                    'region': 'ORD',
                                    'tenantId': '1100111'},
                                {
                                    'publicURL': '{0:s}'.format(
                                        cls._images_url_servers_missing),
                                    'region': 'SYD',
                                    'tenantId': '1100111'}
                            ],
                            'name': 'cloudImages',
                            'type': 'image'},
                    ],
                'token': {
                    'RAX-AUTH:authenticatedBy': ['APIKEY'],
                    'expires': '2015-11-28T16:20:30.222Z',
                    'id': '{0:s}'.format(cls._test_token),
                    'tenant': {'id': '1100111', 'name': '1100111'}},
                'user': {
                    'RAX-AUTH:defaultRegion': 'ORD',
                    'id': '{ApiKey}'.format(**config_test.AUTH_DATA),
                    'name': '{ApiUser}'.format(**config_test.AUTH_DATA),
                    'roles': [{'description': 'Default Role.', 'id': '2',
                               'name': 'identity:default'}]}}}

        cls._config_valid = imageroller.test.write_config(
            "config", config_test.CONFIG_SERVER_VALID_MINIMAL,
            config_test.CONFIG_DATA)
        cls._auth = imageroller.test.write_config(
            "auth", config_test.AUTH_VALID, config_test.AUTH_DATA)

    def test_valid(self):
        """Test the URLs are correctly parsed
        """
        servers_url, images_url = imageroller.utils.parse_rax_id_data(
            self._identity_response, "ORD")
        self.assertEqual(self._servers_url_ord, servers_url)
        self.assertEqual(self._images_url_ord, images_url)

    def test_missing_region(self):
        """Test that None is returned for both URLs
        """
        servers_url, images_url = imageroller.utils.parse_rax_id_data(
            self._identity_response, "DFW")
        self.assertIsNone(servers_url)
        self.assertIsNone(images_url)

    def test_missing_servers_url(self):
        """Test edge-case where only servers URL is missing
        """
        servers_url, images_url = imageroller.utils.parse_rax_id_data(
            self._identity_response, "SYD")
        self.assertIsNone(servers_url)
        self.assertEqual(self._images_url_servers_missing, images_url)

    def test_missing_images_url(self):
        """Test edge-case where only images URL is missing
        """
        servers_url, images_url = imageroller.utils.parse_rax_id_data(
            self._identity_response, "HKG")
        self.assertEqual(self._servers_url_images_missing, servers_url)
        self.assertIsNone(images_url)


class ImageNameTestCase(unittest.TestCase):
    """Image Name related tests
    """

    @classmethod
    def setUpClass(cls):
        """Setup the current time for comparison
        """
        cls._utcnow = datetime.datetime.utcnow()

    def check_field(self, parsed_time, field_name, not_set=False):
        """Helper function to check a datetime.datetime field

        :type parsed_time: datetime.datetime
        :param parsed_time: The result of strptime on the image name
        :type field_name: str
        :param field_name: the datetime.datetime attr to test
        :type not_set: bool
        :param not_set: True if the datetime.datetime attr
            is not expected to be set (tested to be 0),
          False if should be compared with self._utcnow
        """
        self.assertEqual(
            0 if not_set else getattr(self._utcnow, field_name),
            getattr(parsed_time, field_name))

    def test_default_template(self):
        """Test the default template
        """
        name_template = imageroller.utils.IMAGE_NAME_TEMPLATE
        image_name = imageroller.utils.get_image_name(
            self._utcnow, name_template=name_template)
        parsed_time = datetime.datetime.strptime(image_name, name_template)
        self.check_field(parsed_time, 'year')
        self.check_field(parsed_time, 'month')
        self.check_field(parsed_time, 'day')
        self.check_field(parsed_time, 'hour')
        self.check_field(parsed_time, 'minute')
        self.check_field(parsed_time, 'second', not_set=True)
        self.check_field(parsed_time, 'microsecond', not_set=True)

    def test_date_only(self):
        """Test setting only the date, and using prefix instead of suffix, text
        """
        name_template = "foobar-%Y-%m-%d"
        image_name = imageroller.utils.get_image_name(
            self._utcnow, name_template=name_template)
        parsed_time = datetime.datetime.strptime(image_name, name_template)
        self.check_field(parsed_time, 'year')
        self.check_field(parsed_time, 'month')
        self.check_field(parsed_time, 'day')
        self.check_field(parsed_time, 'hour', not_set=True)
        self.check_field(parsed_time, 'minute', not_set=True)
        self.check_field(parsed_time, 'second', not_set=True)
        self.check_field(parsed_time, 'microsecond', not_set=True)
