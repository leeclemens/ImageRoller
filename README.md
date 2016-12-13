ImageRoller
===========

[![Build Status](https://travis-ci.org/leeclemens/imageroller.svg?branch=master)](https://travis-ci.org/leeclemens/imageroller)
[![Coverage Status](https://coveralls.io/repos/leeclemens/imageroller/badge.svg?branch=master&service=github)](https://coveralls.io/github/leeclemens/imageroller?branch=master)
[![Code Climate](https://codeclimate.com/github/leeclemens/imageroller/badges/gpa.svg)](https://codeclimate.com/github/leeclemens/imageroller)
[![Issue Count](https://codeclimate.com/github/leeclemens/imageroller/badges/issue_count.svg)](https://codeclimate.com/github/leeclemens/imageroller)

A simple to manage saved images of Rackspace cloud servers.

- Allows for the configuration of multiple servers with varying retention specifications

- Can easily be scheduled via crond, etc to maintain a number of images/retention for your Rackspace cloud servers


Installation
------------

```Shell
git clone https://github.com/leeclemens/imageroller.git
cd imageroller
pip install .
```

Usage
-----

```Shell
imageroller -c /root/imageroller_config.conf -a /root/imageroller_auth.conf
```

Support
-------

Create an Issue at https://github.com/leeclemens/imageroller/issues


Contribute
----------

1. Fork the repo
  * Preferably create a new feature branch
2. Make your edits and push
3. Create a Pull Request
