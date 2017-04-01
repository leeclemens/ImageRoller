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

"""Objects used for data storage
"""

import collections
import configparser
import datetime

RAX_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class ConfigData(object):
    """ConfigData
    """

    def __init__(self, concurrent_workers):
        """Configuration data (global)

        :type concurrent_workers: int
        :param concurrent_workers: Number of concurrent workers
        """
        self._concurrent_workers = int(concurrent_workers)
        if self._concurrent_workers <= 0:
            raise ValueError('Concurrent workers must be greater than 0')
        self._server_data = collections.OrderedDict()

    @property
    def concurrent_workers(self):
        """Concurrent Workers property

        :return: The number of concurrent workers
        """
        return self._concurrent_workers

    @property
    def server_data(self):
        """Server Data property

        :rtype list
        :return: The values from the internal Server Data dict
        """
        return self._server_data.values()

    @server_data.setter
    def server_data(self, value):
        """Server Data property setter

        :type value: ServerData
        :param value: The Server Data to set in the internal dict

        :raises ValueError if an invalid value is attempted to be set
        """
        if hasattr(value, 'name') and hasattr(value, 'enabled'):
            if value.enabled:
                self._server_data[value.name] = value
        else:
            raise ValueError('Invalid object set as server data'
                             ' (name and/or enabled attrs missing)')


class ServerData(object):
    """Server Data
    """
    INDEX_SERVER_ID = 0
    INDEX_TOKEN = 1
    INDEX_SERVERS_URL = 2
    INDEX_IMAGES_URL = 3

    def __init__(self, name, config, auto_enable, force):
        """Server Data object

        :type name: str
        :param name: The server's FQDN
        :type config: configparser.SectionProxy or dict
        :param config: The server's configparser object or dict
        :type auto_enable: bool
        :param auto_enable: True if the server was specified on command-line
        :type force: bool
        :param force: -f, --force specified on command-line
        """
        self._name = name
        self._config = config
        self._auto_enable = auto_enable
        self._force = force
        # server_id, token, servers_url, images_url
        self._identity_info = [None, None, None, None]

    def __str__(self):
        return '%s  Region: %s  AutoEnable: %s  Force: %s' % (
            self.name, self.region, self.auto_enable, self.force)

    @property
    def name(self):
        """Server Data's name property

        :return: The name
        """
        return self._name

    @property
    def auto_enable(self):
        """Server Data's auto_enable property

        :return: True if should be auto-enabled, otherwise False
        """
        return self._auto_enable

    @property
    def force(self):
        """Server Data's force property

        :return: True if a new image should be forced, otherwise False
        """
        return self._force

    @property
    def enabled(self):
        """Server Data's enabled property

        :return: True if auto-enabled or configured to be enabled
        """
        if self.auto_enable:
            return self.auto_enable
        else:
            if isinstance(self._config, configparser.SectionProxy):
                return self._config.getboolean('Enabled',
                                               fallback=False)
            else:
                return self._config['Enabled']

    @property
    def region(self):
        """Server Data's region property

        :return: The region configured for this server (e.g. DFW)
        """
        if isinstance(self._config, configparser.SectionProxy):
            return self._config.get('Region')
        else:
            return self._config['Region']

    @property
    def server_id(self):
        """Server Data's server_id property

        :return: The server ID for this server
        """
        return self._identity_info[ServerData.INDEX_SERVER_ID]

    @server_id.setter
    def server_id(self, value):
        """Server Data's server_id property's setter

        :type value: str
        :param value: The server's ID
        """
        self._identity_info[ServerData.INDEX_SERVER_ID] = value

    @property
    def token(self):
        """Server Data's token property

        :return: The token for this server
        """
        return self._identity_info[ServerData.INDEX_TOKEN]

    @token.setter
    def token(self, value):
        """Server Data's token property setter

        :type value: str
        :param value: The server's token
        """
        self._identity_info[ServerData.INDEX_TOKEN] = value

    @property
    def servers_url(self):
        """Server Data's servers_url property

        :return: The server's servers url
        """
        return self._identity_info[ServerData.INDEX_SERVERS_URL]

    @servers_url.setter
    def servers_url(self, value):
        """Server Data's servers_url property setter

        :type value: str
        :param value: The server's servers url
        """
        self._identity_info[ServerData.INDEX_SERVERS_URL] = value

    @property
    def images_url(self):
        """Server Data's images_url property

        :return: The server's images url
        """
        return self._identity_info[ServerData.INDEX_IMAGES_URL]

    @images_url.setter
    def images_url(self, value):
        """Server Data's images_url property setter

        :type value: str
        :param value: The server's images url
        """
        self._identity_info[ServerData.INDEX_IMAGES_URL] = value

    @property
    def save_timeout_minutes(self):
        """Server Data's save_timeout_minutes property

        :return: The configured SaveTimeoutMinutes, in minutes
        """
        if isinstance(self._config, configparser.SectionProxy):
            return self._config.getint('SaveTimeoutMinutes')
        else:
            return self._config['SaveTimeoutMinutes']

    @property
    def save_timeout_seconds(self):
        """Server Data's save_timeout_seconds property

        :return: The configured SaveTimeoutMinutes, in seconds
        """
        return self.save_timeout_minutes * 60

    @property
    def retain_image_minutes(self):
        """Server Data's retain_image_minutes property

        :return: The configured RetainImageMinutes, in minutes
        """
        if isinstance(self._config, configparser.SectionProxy):
            return self._config.getint('RetainImageMinutes')
        else:
            return self._config['RetainImageMinutes']

    @property
    def retain_image_seconds(self):
        """Server Data's retain_image_seconds property

        :return: The configured RetainImageMinutes, in seconds
        """
        return self.retain_image_minutes * 60


class ImageData(object):
    """ImageData
    """

    def __init__(self, server_fqdn, image_dict):
        """Image Data object

        :param server_fqdn: The server's FQDN
        :param image_dict: The image data obtained from the API
        """
        self._server_fqdn = server_fqdn
        self._image_dict = image_dict
        self._created = datetime.datetime.strptime(
            self._image_dict['created'], RAX_DATE_FORMAT)
        self._updated = datetime.datetime.strptime(
            self._image_dict['updated'], RAX_DATE_FORMAT)

    def __str__(self):
        # noinspection PyCallByClass
        """Image Data's str representation

        :return: The server_fqdn, name, image_id, created, updated,
         status, progress values
        """
        return '<{}: {} [{}] C:{} U:{} [{}] {}%>'.format(
            self.server_fqdn, self.name, self.image_id,
            self.created, self.updated,
            self.status, self.progress)

    @property
    def server_fqdn(self):
        """Image Data's server_fqdn property

        :return: The server FQDN for this image
        """
        return self._server_fqdn

    @property
    def image_id(self):
        """Image Data's image_id property

        :return: The image's id
        """
        return self._image_dict['id']

    @property
    def name(self):
        """Image Data's name property

        :return: The image's name
        """
        return self._image_dict['name']

    @property
    def created(self):
        """Image Data's created property

        :return: The datetime of the image's created attribute
        """
        return self._created

    @property
    def updated(self):
        """Image Data's updated property

        :return: The datetime of the image's updated attribute
        """
        return self._updated

    @property
    def status(self):
        """Image Data's status property

        :return: The image's status attribute
        """
        return self._image_dict['status']

    @property
    def saving(self):
        """Image Data's saving property

        :return: True if the status is "SAVING", otherwise False
        """
        return self.status == 'SAVING'

    @property
    def active(self):
        """Image Data's active property

        :return: True if the status is "ACTIVE", otherwise False
        """
        return self.status == 'ACTIVE'

    @property
    def progress(self):
        """Image Data's progress property

        :return: The progress of the image
        """
        return self._image_dict['progress']
