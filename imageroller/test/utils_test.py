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
import string
import unittest

import imageroller.utils


class HeaderTestCase(unittest.TestCase):
    def test_json_content_header(self):
        self.assertDictEqual(
            imageroller.utils.get_json_content_header(),
            {"Content-Type": "application/json"}
        )

    def test_auth_token_header(self):
        fake_token = ''.join(random.SystemRandom().choice(
            string.digits + string.ascii_lowercase[:6]) for _ in range(32))
        self.assertDictEqual(
            imageroller.utils.get_auth_token_header(fake_token),
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Auth-Token": fake_token,
            }
        )
