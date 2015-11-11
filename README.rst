ImageRoller
===========

A simple backup utility utilizing saved images for Rackspace virtual machines.

- Allows for the configuration of multiple servers with varying retention specifications.

- Can easily be scheduled via crond, etc to maintain a number of images/retention for your Rackspace hosted servers


Installation
------------

```
git clone https://github.com/leeclemens/imageroller.git
cd ImageRoller
pip install .
```

Usage
-----

```
imageroller -c /root/imageroller_config.conf -a /root/imageroller_auth.conf
```

Support
-------

Create an Issue at https://github.com/leeclemens/imageroller/issues


Contribute
----------

Fork the repo
Preferably create a new feature branch
Make your edits and push to your forked repo
Create a Pull Request
