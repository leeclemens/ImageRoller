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

"""Static utility functions
"""

import datetime
import json
import pprint

import requests

import imageroller
import imageroller.data
import imageroller.threads.roller_runner as roller_runner

IMAGE_NAME_TEMPLATE = "%Y-%m-%d_%H-%M_imageroller"

JSON_MIME_TYPE = "application/json"

IDENTITY_URL = "https://identity.api.rackspacecloud.com/v2.0/tokens"


def get_json_content_header():
    """Returns the Content-Type, for use in the HTTP request header
    """
    return {"Content-Type": JSON_MIME_TYPE}


def get_auth_token_header(token):
    """Returns the Content-Type, Accept and X-Auth-Token headers for use
     in the HTTP request header for requests requiring authentication

     :type token: str
     :param token: The X-Auth-Token to append to header
    """
    header = get_json_content_header()
    header.update({
        "Accept": JSON_MIME_TYPE,
        "X-Auth-Token": str(token)
    })
    return header


def get_auth_body_data(auth_data, hide_key=False):
    """Private function for returning the API key in the header data

    :type auth_data: tuple
    :param auth_data: Auth data tuple of (username, API key)
    :type hide_key: bool
    :param hide_key: True to obfuscate the API key (for logging)
    """
    return json.dumps({
        "auth": {
            "RAX-KSKEY:apiKeyCredentials": {
                "username": auth_data[0],
                "apiKey": "HIDDEN_KEY" if hide_key else auth_data[1]}}
    })


def get_identity_response(auth_data):
    """Function for returned the raw response from the IDENTITY_URL

    :param auth_data:
    :return:
    """
    return requests.post(
        IDENTITY_URL,
        data=get_auth_body_data(auth_data),
        headers=get_json_content_header())


def parse_rax_id_data(rax_id_data, region):
    """Parse the Identity request for the region

    :type rax_id_data: dict
    :param rax_id_data: The raw data returned from identity request
    :type region: str
    :param region: The region
    :rtype : tuple
    :return: (Servers URL, Images URL) for the region
    """
    servers_url = None
    images_url = None
    for catalog in rax_id_data["access"]["serviceCatalog"]:
        servers_url = _lookup_public_url(
            catalog, "compute", "cloudServersOpenStack", region, servers_url)
        images_url = _lookup_public_url(
            catalog, "image", "cloudImages", region, images_url)
    return servers_url, images_url


def get_server_id(server_data, log):
    """Returns the server ID
    :type server_data: imageroller.data.ServerData
    :param server_data:
    :type log: logging.getLoggerClass()
    :param log: The logger instance
    """
    request_url = server_data.servers_url + "/servers"
    log.trace("Server Request: %s, headers=%s", request_url,
              get_auth_token_header("HIDDEN_TOKEN") if log.isEnabledFor(
                  imageroller.Logger.TRACE) else "")
    servers_response = requests.get(request_url, headers=get_auth_token_header(
        server_data.token))
    log.trace("Servers Response: %s", servers_response)
    # pylint: disable=no-member
    if servers_response.status_code == requests.codes.ok:
        try:
            servers = json.loads(servers_response.content.decode())
            _trace_json("Servers Response JSON", servers, log)
            for server in servers["servers"]:
                log.debug("Server: %s", server)
                if server["name"].lower() == server_data.name:
                    log.debug("Found Server ID: %s", server["id"])
                    return server["id"]
            return None
        except ValueError:
            raise Exception("Failed to parse images: %s" %
                            servers_response.content)
    else:
        raise Exception("Image request failed: %s %s" %
                        (servers_response.status_code,
                         servers_response.content))


def get_image_name(utcnow, name_template=IMAGE_NAME_TEMPLATE):
    """Determines the new image name, based upon the UTC time

    :type utcnow: datetime.datetime
    :param utcnow: The starting UTC time
    :type name_template: str
    :param name_template: The image name template to use
     default: IMAGE_NAME_TEMPLATE
    """
    return utcnow.strftime(name_template)


def process_server(server_data, log):
    """Process the given server

    :type server_data: imageroller.data.ServerData
    :param server_data: The server's data
    :type log: logging.getLoggerClass()
    :param log: The logger instance
    """
    utcnow = datetime.datetime.utcnow()
    images = get_images(server_data, log)
    if _is_any_in_progress(images, log):
        if _is_timed_out(utcnow, server_data, images, log):
            # Enhance: We can't delete it, but should we create a new one?
            log.error("Image is in progress but exceeded timeout"
                      " of: {}m".format(server_data.save_timeout_minutes))
        else:
            log.warning("Image is in progress, waiting")
    else:
        if _needs_image(utcnow, server_data, images, log):
            # Request a new image
            roller_runner_ = roller_runner.RollerRunner(server_data,
                                                        get_image_name(utcnow),
                                                        get_auth_token_header(
                                                            server_data.token))
            roller_runner_.start()
            roller_runner_.join()
        else:
            # Only delete images if active/complete non-stale image exists
            _delete_expired_images(utcnow, server_data, images, log)


def get_images(server_data, log):
    """Get the Image data for the server

    :type server_data: imageroller.data.ServerData
    :param server_data: The server data
    :type log: logging.getLoggerClass()
    :param log: The logger instance
    """
    request_url = "{}/images/detail?server={}".format(
        server_data.servers_url, server_data.server_id)
    log.trace("Images Request: %s headers=%s", request_url,
              get_auth_token_header("HIDDEN_TOKEN") if log.isEnabledFor(
                  imageroller.Logger.TRACE) else "")
    images_response = requests.get(request_url, headers=get_auth_token_header(
        server_data.token))
    log.trace("Images Response: %s", images_response)
    # Enhance: Query images detail for attributes such as 'protected'
    # pylint: disable=no-member
    if images_response.status_code == requests.codes.ok:
        images = json.loads(images_response.content.decode())
        try:
            return _get_images(server_data, images, log)
        except ValueError:
            raise Exception("Failed to parse images: %s" %
                            images_response.content)
    else:
        raise Exception("Image request failed: %s %s" %
                        (images_response.status_code,
                         images_response.content))


def _get_images(server_data, images, log):
    _trace_json("Images Response JSON", images, log)
    images_data = []
    for image in images["images"]:
        image_data = imageroller.data.ImageData(server_data.name,
                                                image)
        try:
            # This raises ValueError if format doesn't match
            datetime.datetime.strptime(image_data.name,
                                       IMAGE_NAME_TEMPLATE)
            log.debug("Found image %s", image_data)
            images_data.append(image_data)
        except ValueError:
            log.debug("Ignoring image %s", image_data)
    return images_data


def _is_any_in_progress(images, log):
    """Determine if any image is in progress

    :type images: list
    :param images: The server's images
    :type log: logging.getLoggerClass()
    :param log: The logger instance
    :rtype : bool
    :return: True if any image is in progress, False if no image is in progress
    """
    for image in images:
        if image.saving:
            log.info("Image is still saving [%s%%]: %s",
                     image.progress, image.name)
            return True
    return False


def _is_timed_out(utcnow, server_data, images, log):
    """Determine if an Image is timed out

    :type utcnow: datetime.datetime
    :param utcnow: The starting UTC time
    :type server_data: imageroller.data.ServerData
    :param server_data: The ServerData
    :type images: list
    :param images: The server's images
    :type log: logging.getLoggerClass()
    :param log: The logger instance
    :return: True if any image is timed out
    """
    timeout_timedelta = datetime.timedelta(
        seconds=server_data.save_timeout_seconds)
    for image in images:
        if image.saving and \
                        image.progress < 100 and \
                        (utcnow - image.updated) > timeout_timedelta:
            log.error("Image is timed out: %s" % image)
            return True
    return False


def _delete_expired_images(utcnow, server_data, images, log):
    """Delete the expired images

    :type utcnow: datetime.datetime
    :param utcnow: The starting UTC time
    :type server_data: imageroller.data.ServerData
    :param server_data:
    :type images: list
    :param images:
    :type log: logging.getLoggerClass()
    :param log: The logger instance
    :return: True if all delete requests return True, False if any did not
    """

    def delete_image(image):
        """Delete the given image

        :type image: imageroller.data.ImageData
        :param image: The image to delete
        :return: True if the delete request was successful, False if not
        """
        request_url = "{}/images/{}".format(server_data.images_url,
                                            image.image_id)
        log.trace("Delete Image request: %s headers=%s", request_url,
                  get_auth_token_header("HIDDEN_TOKEN") if log.isEnabledFor(
                      imageroller.Logger.TRACE) else "")
        delete_image_response = requests.delete(request_url,
                                                headers=get_auth_token_header(
                                                    server_data.token))
        log.trace("Delete Image response: %s", delete_image_response)
        if delete_image_response.status_code == 204:
            log.info("Successfully deleted image: %s", image)
            return True
        else:
            log.error("Failed to delete image. Code: %s Image:: %s",
                      delete_image_response.status_code, image)
            return False

    success = True
    if server_data.force:
        log.info("Force flag set - skipping delete")
    else:
        retain_timedelta = datetime.timedelta(
            seconds=server_data.retain_image_seconds)
        # Bug #264 - Support more than one non-stale image
        for image_ in images:
            if image_.active and (utcnow - image_.updated) > retain_timedelta:
                log.info("Deleting image: %s", image_)
                success &= delete_image(image_)
            else:
                log.debug("Not deleting non-stale image [%sm]: %s",
                          server_data.retain_image_minutes, image_)
    return success


def _needs_image(utcnow, server_data, images, log):
    """Determines if the server needs a new image to be created
    :type utcnow: datetime.datetime
    :param utcnow: The starting UTC time
    :type server_data: imageroller.data.ServerData
    :param server_data:
    :type images: list
    :param images:
    :type log: logging.getLoggingClass()
    :param log: The logger instance
    :return:
    """
    if server_data.force:
        log.info("Force flag set - ignoring existing images")
        return True
    retain_timedelta = datetime.timedelta(
        seconds=server_data.retain_image_seconds)
    for image in images:
        # Using created here,
        #  where updated is used elsewhere, may cause overlap?
        if image.active and (utcnow - image.created) < retain_timedelta:
            # Bug #264 - Support more than one non-stale image
            log.info("Found an active image within retention [%sm]: %s",
                     server_data.retain_image_minutes, image.name)
            return False
    log.debug("No active images within retention")
    return True


def _lookup_public_url(catalog, cat_type, cat_name, region, previous_url):
    """Parse to catalog and return the appropriate publicURL value
        Falls back to returning the previous_url
         so a value is not overridden while looping
    :param catalog: The catalog dictionary
    :param cat_type: The catalog's type key value
    :param cat_name: The catalog's name key value
    :param region: The endpoint's region key value
    :param previous_url: The current value for the publicURL
    :return: The publicURL value, or the previous_url if none was found
    """
    if catalog["type"] == cat_type and catalog["name"] == cat_name:
        for endpoint in catalog["endpoints"]:
            if endpoint["region"] == region:
                return endpoint["publicURL"]
    return previous_url


def _trace_json(message, json_data, log):
    log.trace("%s: %s",
              message,
              pprint.pformat(json_data) if log.isEnabledFor(
                  imageroller.Logger.TRACE) else "")
