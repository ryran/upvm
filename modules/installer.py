# -*- coding: utf-8 -*-
# Copyright 2016 upvm Contributors (see CONTRIBUTORS file in source)
# License: Apache License 2.0 (see LICENSE file in source)

# Modules from standard library
from __future__ import print_function
import subprocess

# Custom modules
from . import cfg
from . import string_ops as c

def install():
    o = cfg.opts
    cmd = [
        'virt-install',
        '--import',
        '--name',
        o.vmname,
        '--memory',
        str(o.memory),
        '--vcpus',
        str(o.vcpus),
        '--disk',
        '{},format={}'.format(o.outFile, o.format),
        '--noautoconsole',
        ]
    if o.os_variant:
        cmd.extend(['--os-variant', o.os_variant])
    if o.disk:
        for d in o.disk:
            cmd.extend(['--disk', d])
    if o.network:
        for n in o.network:
            cmd.extend(['--network', n])
    c.verbose("\n  INFO: Starting virt-install")
    cfg.debug("Executing:\n  {}\n".format(" \ \n  ".join(cmd)))
    subprocess.check_call(cmd)
