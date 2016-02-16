# -*- coding: utf-8 -*-
# Copyright 2016 upvm Contributors (see CONTRIBUTORS.md file in source)
# License: Apache License 2.0 (see LICENSE file in source)

# Modules from standard library
from __future__ import print_function
import subprocess
import os
from sys import exit

# Custom modules
from . import string_ops as c
from . import cfg

def write_and_cleanup_image():
    blockdev, imgfile = cfg.opts.primary_blockdev, cfg.opts.outFile
    cmd = ['sudo', cfg.blockdevHelper, blockdev, imgfile]
    print(c.GREEN("Starting write of image file '{}' to blockdev '{}'".format(imgfile, blockdev)))
    print(c.green("(This could take a while)"))
    rc = subprocess.call(cmd)
    if rc == 0:
        c.verbose("Successfully wrote intermediate image file to blockdev")
        cfg.cleanup_imagefile()
    else:
        print(c.RED("Error writing image file '{}' to block device '{}'".format(imgfile, blockdev)))
        cfg.cleanup_imagefile()
        exit(1)
