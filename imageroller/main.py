#!/usr/bin/env python3
#  The MIT License (MIT)
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

"""This is the main script for imageroller
"""

import argparse
import configparser
import logging
import sys
import warnings

import imageroller.data
import imageroller.threads.roller_manager
from imageroller import ConfigError

CONFIG_REQUIRED_DEFAULT = ["ConcurrentWorkers"]
CONFIG_REQUIRED_SERVER = [
    "SaveTimeoutMinutes",
    "RetainImageMinutes",
    "Region",
]

AUTHCONFIG_SECTION = "AUTH"
AUTHCONFIG_USER = "ApiUser"
AUTHCONFIG_KEY = "ApiKey"

LOG = logging.getLogger("imageroller")


def main_func():
    """Main function
    """
    start_logger()
    args = get_args()
    try:
        with open(args.config, "r") as config_f:
            try:
                with open(args.authconfig, "r") as auth_config_f:
                    config_data, auth_tuple = read_configs(
                        args, config_f, auth_config_f)
                    execute(args.log_level, config_data, auth_tuple)
            except ConfigError as exc_config_error:
                LOG.error("Configuration error: %s", exc_config_error)
                sys.exit(1)
            except OSError as exc_authconfig:
                _exit_config_oserror("authconfig", args.authconfig,
                                     exc_authconfig)
    except OSError as exc_config:
        _exit_config_oserror("config", args.config, exc_config)


def _exit_config_oserror(config_name, config_file, exc):
    LOG.error("Failed to open %s: %s", config_name, config_file)
    LOG.exception(exc)
    sys.exit(1)


def execute(log_level, config_data, auth_tuple):
    """Start the RollerManager and wait for it to complete

    :type log_level: int
    :param log_level: The logging level
    :type config_data: imageroller.data.ConfigData
    :param config_data: The processed server config
    :type auth_tuple: tuple
    :param auth_tuple: The processed auth config
    """
    try:
        # Now use the formatted logger
        format_logger(log_level)
        roller_mgr = imageroller.threads.roller_manager.RollerManager(
            config_data, auth_tuple)
        roller_mgr.start()
        # pylint: disable=fixme
        # TODO: Bug #263 - Add signal handler to exit
        roller_mgr.join()
        LOG.info("All Rollers and Roller Manager exited")
    # pylint: disable=broad-except
    except Exception as ex:
        LOG.error("Uncaught exception in main()")
        LOG.exception(ex)
        sys.exit(1)


def read_configs(args, config_f, auth_config_f):
    """Read all of the configs

    :type args: argparse.Namespace
    :param args: The commandline args
    :type config_f: io.TextIOWrapper
    :param config_f: The file object of the config file
    :type auth_config_f: io.TextIOWrapper
    :param auth_config_f: The file object of the auth config file
    """
    cfg_parser = configparser.ConfigParser()
    cfg_parser.read_file(config_f)
    config_data = read_config(args, cfg_parser)
    authcfg_parser = configparser.ConfigParser()
    authcfg_parser.read_file(auth_config_f)
    auth_tuple = read_authconfig(authcfg_parser)
    return config_data, auth_tuple


def read_config(args, cfg_parser):
    """Read and process the server config

    :type args: argparse.Namespace
    :param args: The commandline args
    :type cfg_parser: configparser.ConfigParser
    :param cfg_parser: The ConfigParser for the server config
    """
    for required_key in CONFIG_REQUIRED_DEFAULT:
        if required_key not in cfg_parser["DEFAULT"]:
            raise ConfigError("Config must contain %s" % required_key)
    # Initialize our ConfigData object
    config_data = imageroller.data.ConfigData(
        cfg_parser["DEFAULT"].getint("ConcurrentWorkers"))
    if args.server:
        if args.server in cfg_parser:
            # Server was specified on the command line, only include it
            # If specified, the server will always be 'enabled'
            config_data.server_data = imageroller.data.ServerData(
                args.server, cfg_parser[args.server], True, args.force)
        else:
            raise ConfigError(
                "The specified server is not configured: %s" % args.server)
    else:
        # Iterate all configured servers
        for server in cfg_parser.sections():
            for required_key in CONFIG_REQUIRED_SERVER:
                if required_key not in cfg_parser[server]:
                    raise ConfigError(
                        "Server Config for %s is missing %s" % (
                            server, required_key))
            config_data.server_data = imageroller.data.ServerData(
                server, cfg_parser[server], False, args.force)
    # Check that we have at least one configured server
    if len(config_data.server_data) > 0:
        return config_data
    else:
        raise ConfigError("You must configure at least one server")


def read_authconfig(authcfg_parser):
    """Read and process the auth config

    :type authcfg_parser: configparser.ConfigParser
    :param authcfg_parser: The ConfigParser for the auth config
    """
    if AUTHCONFIG_SECTION in authcfg_parser:
        if _has_auth_config(AUTHCONFIG_USER, authcfg_parser):
            if _has_auth_config(AUTHCONFIG_KEY, authcfg_parser):
                return (authcfg_parser[AUTHCONFIG_SECTION][AUTHCONFIG_USER],
                        authcfg_parser[AUTHCONFIG_SECTION][AUTHCONFIG_KEY])
            else:
                raise ConfigError(
                    "AuthConfig must contain %s" % AUTHCONFIG_KEY)
        else:
            raise ConfigError("AuthConfig must contain %s" % AUTHCONFIG_USER)
    else:
        raise ConfigError("AuthConfig must contain [%s]" % AUTHCONFIG_SECTION)


def get_args():
    """Process and return the arguments from the command line

    :rtype: argparse.Namespace
    :returns: Parsed args
    """
    parser = argparse.ArgumentParser(
        description='Image Roller - Manages Rackspace Images',
        prog="imageroller")
    parser.add_argument('-c', '--config', type=str, dest="config",
                        required=True, help='config file')
    parser.add_argument('-a', '--authconfig', type=str, dest="authconfig",
                        required=True, help='authconfig file')
    parser.add_argument('-s', '--server', type=str, dest="server",
                        default=None, required=False,
                        help='server to image [all]')
    parser.add_argument('-f', '--force', dest="force", action='store_true',
                        default=False, required=False,
                        help='force server [false]')
    parser.add_argument('-l', '--log', type=str, dest="log_level",
                        default="INFO", required=False,
                        help="log level [INFO]")
    args = parser.parse_args()
    if args.server is None and args.force:
        LOG.error("You must specify a server when using --force\n")
        parser.print_help()
        sys.exit(1)
    try:
        # Use supplied an int, use it
        args.log_level = int(args.log_level)
    except ValueError:
        try:
            # Try to lookup the integer value,
            #  int() will raise if getLevelName() returns "Level %s" (unknown)
            args.log_level = int(
                logging.getLevelName(str(args.log_level).upper()))
        except ValueError:
            LOG.error("Unrecognized logging level: %s\n", args.log_level)
            parser.print_help()
            sys.exit(1)
    return args


def start_logger():
    """Start the logger, using sys.stderr and logging all messages
    """
    # Log everything to stderr initially
    _config_logger("%(message)s", sys.stderr, logging.NOTSET)


def format_logger(level):
    """Formats the logger

    :type level: int
    :param level: The logging level
    """
    # If it is >= WARNING (e.g. ERROR), hide SubjectAltNameWarning from urllib3
    # SubjectAltNameWarning:
    #  Certificate for identity.api.rackspacecloud.com has no `subjectAltName`,
    #  falling back to check for a `commonName` for now.
    #  This feature is being removed by major browsers and deprecated by RFC
    #  2818. (See https://github.com/shazow/urllib3/issues/497 for details.)
    if level >= logging.WARNING:
        # pylint: disable=fixme
        # TODO: Bug #262 - Handle urllib3 SubjectAltNameWarning
        warnings.filterwarnings("ignore")
        # import urllib3
        # import urllib3.exceptions
        # urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)
        # warnings.simplefilter('ignore',
        #                       urllib3.exceptions.SubjectAltNameWarning,
        #                       append=True)
    # Called after command-line and config reading is done
    _config_logger("%(asctime)s %(name)-56s: %(levelname)-6s: %(message)s",
                   sys.stdout, level)


def _has_auth_config(auth_config_key, authcfg_parser):
    """Check that auth_config_key is set and has at least one element

    :param auth_config_key: AUTHCONFIG_USER or AUTHCONFIG_KEY to check
    :param authcfg_parser: The authcfg_parser
    :return: True if auth_config_key exists and has at least one element
    """
    return auth_config_key in authcfg_parser[AUTHCONFIG_SECTION] and len(
        authcfg_parser[AUTHCONFIG_SECTION][auth_config_key]) > 0


def _config_logger(log_format, stream, level):
    """Configure the logger instance

    :type log_format: str
    :param log_format: The log format to use
    :type stream: _io.TextIOWrapper
    :param stream: The stream to log to
    :type level: int
    :param level: The logging level
    """
    root_logger = logging.getLogger("imageroller")
    root_logger.setLevel(level)
    for hdlr in root_logger.handlers:
        root_logger.removeHandler(hdlr)
    formatter = logging.Formatter(log_format)
    hdlr = logging.StreamHandler(stream)
    hdlr.setFormatter(formatter)
    root_logger.addHandler(hdlr)


if __name__ == "__main__":
    main_func()
