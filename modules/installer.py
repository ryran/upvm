# -*- coding: utf-8 -*-
# Copyright 2016 upvm Contributors (see CONTRIBUTORS.md file in source)
# License: Apache License 2.0 (see LICENSE file in source)

# Modules from standard library
from __future__ import print_function
import subprocess
import os

# Custom modules
from . import cfg
from . import string_ops as c

def purge_matching_ssh_known_hosts():
    hostsfile = os.path.expanduser('~/.ssh/known_hosts')
    regex = '^{0}(,|\s)|^{0}\.{1}(,|\s)'.format(cfg.opts.vmname, cfg.opts.dnsdomain)
    cmd = ['grep', '-q', '-E', regex, hostsfile]
    rc = subprocess.call(cmd)
    if rc != 0:
        return
    cmd = ['sed', '-r', '-i', '/{}/d'.format(regex), hostsfile]
    subprocess.call(cmd)
    c.verbose("Purged ~/.ssh/known_hosts of existing [matching] host entry")

def install():
    purge_matching_ssh_known_hosts()
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
        '{},format={}'.format(o.outFile, o.img_format),
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
    if o.boot:
        cmd.extend(['--boot', o.boot])
    else:
        o.boot = cfg.virtinstall_default_bootopts
        if o.uefi:
            o.boot += ',uefi'
        cmd.extend(['--boot', o.boot])
    if o.vinstall_arg:
        for a in o.vinstall_arg:
            cmd.append(a)
    c.verbose("Starting virt-install")
    c.debug("Executing:\n    {}\n".format(" \ \n    ".join(cmd)))
    subprocess.check_call(cmd)
