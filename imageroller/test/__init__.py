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

"""imageroller.test shared functions
"""
import configparser
import random
import string
import tempfile


def generate_api_key():
    """Generates and returns a random Rackspace-like API Key/token
    """
    return ''.join(random.SystemRandom().choice(
        string.digits + string.ascii_lowercase[:6]) for _ in range(32))


def generate_token():
    """Generates and returns a random Rackspace-like Authentication token
    """
    return ''.join(random.SystemRandom().choice(
        string.digits + string.ascii_letters) for _ in range(136))


def write_config(conf_type, config_text, args):
    """Helper function which calls get_config_path() and do_write_config()

    :type conf_type: str
    :param conf_type: Type of configuration file 'config' or 'auth'
    :type config_text: str
    :param config_text: Text to write to the config file
    :type args: dict
    :param args: kwargs to format config_text
    :return: Absolute path to the temp config file
    """
    path = get_config_path(conf_type)
    do_write_config(path, config_text, args)
    return path


def get_config_path(conf_type):
    """Acquires and returns a standard named temp file

    :type conf_type: str
    :param conf_type: Type of configuration file 'config' or 'auth'
    :return: Absolute path to the temp config file
    """
    return tempfile.mkstemp(suffix=".conf",
                            prefix="imageroller_%s_" % conf_type)[1]


def do_write_config(config_path, config_text, args):
    """Helper function to write the test config data

    :type config_path: str
    :param config_path: Absolute path to the temp config file
    :type config_text: str
    :param config_text: Text to write to the config file
    :type args: dict
    :param args: kwargs to format config_text
    """
    with open(config_path, "w") as config_f:
        config_f.writelines(config_text.format(**args))


def get_config_parser(path):
    """Helper function to return a ConfigParser

    :type path: str
    :param path: Absolute path to the temp config file
    """
    with open(path) as path_f:
        cfg_parser = configparser.ConfigParser()
        cfg_parser.read_file(path_f)
        return cfg_parser
