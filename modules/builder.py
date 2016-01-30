# -*- coding: utf-8 -*-
# Copyright 2016 upvm Contributors (see CONTRIBUTORS.md file in source)
# License: Apache License 2.0 (see LICENSE file in source)

# Modules from standard library
from __future__ import print_function
from textwrap import dedent
import tempfile
import subprocess
import json
import os
import glob
from time import sleep
from sys import exit

# Custom modules
from . import cfg
from . import string_ops as c

firstBootScriptStart = dedent("""\
    #!/bin/bash
    echo "Installing authorized ssh pubkey(s) for root user ..."
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    touch ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    restorecon -R ~/.ssh
    cat >> ~/.ssh/authorized_keys <<\EOF
    """)

firstBootScriptEnd = dedent("""\
    EOF
    echo Done.
    #echo Running cron.daily scripts ...
    #run-parts /etc/cron.daily
    #echo Done.
    systemctl disable firstboot 2>/dev/null
    rm /etc/rc?.d/S99virt-sysprep-firstboot
    echo One-time firstboot script finished.
    """)

def initialize_libvirt_qemu_session():
    cmd = ['virsh', '-c', 'qemu:///session', 'uri']
    loopCount = 0
    while True:
        if loopCount > 5:
            print(c.RED("Reached maximum number of attempts (unable to open qemu:///session)\nProbably some problem with virsh command or libvirtd service"))
            print("(Contact rsaw@redhat.com)")
            exit(1)
        try:
            c.debug("Executing: {}".format(" ".join(cmd)))
            with open(os.devnull, 'w') as n:
                subprocess.check_call(cmd, stdout=n)
        except subprocess.CalledProcessError:
            print(c.yellow("Connect to qemu:///session failed; trying again in 1sec ..."))
            sleep(1.0)
        else:
            break
        loopCount += 1

def build():
    c.verbose("Initializing libvirt connection to qemu:///session")
    initialize_libvirt_qemu_session()
    o = cfg.opts
    cmd = [
        'virt-builder', o.templateName,
        '--output', o.outFile
        ]
    if o.vbCachedir:
        cmd.extend(['--cache', o.vbCachedir])
    if not o.hostname in '!':
        cmd.extend(['--hostname', o.hostname])
        if o.add_dhcp_hostname:
            cmd.extend([
                '--run-command',
                'echo -e "DHCP_HOSTNAME={}\nDEVICE=eth0" >> /etc/sysconfig/network-scripts/ifcfg-eth0'.format(o.hostname),
                ])
    if o.arch:
        cmd.extend(['--arch', o.arch])
    if o.root_password:
        cmd.extend(['--root-password', o.root_password])
    if o.size:
        cmd.extend(['--size', o.size])
    if o.format:
        cmd.extend(['--format', o.format])
    if o.upload:
        for upfile in o.upload:
            cmd.extend(['--upload', upfile])
    if o.run:
        for rscript in o.run:
            cmd.extend(['--run', rscript])
    if o.run_command:
        for rcmd in o.run_command:
            cmd.extend(['--run-command', rcmd])
    if o.firstboot:
        for fbscript in o.firstboot:
            cmd.extend(['--firstboot', fbscript])
    if o.firstboot_command:
        for fbcmd in o.firstboot_command:
            cmd.extend(['--firstboot-command', fbcmd])
    if o.install:
        for pkgs in o.install:
            cmd.extend(['--install', pkgs])
    if o.firstboot_install:
        for pkgs in o.firstboot_install:
            cmd.extend(['--firstboot-install', pkgs])
    if o.selinux_relabel or o.install:
        cmd.append('--selinux-relabel')
    # if o.cmdlineArgs:
    #     for arg in o.cmdlineArgs[1:]:
    #         cmd.append(arg)
    tmp1 = tempfile.NamedTemporaryFile(delete=True)
    tmp1.write(firstBootScriptStart)
    if o.ssh_pubkey:
        for item in o.ssh_pubkey:
            for keyfile in glob.glob(os.path.expanduser(item)):
                with open(keyfile, 'r') as f:
                    tmp1.write(f.read())
    tmp1.write(firstBootScriptEnd)
    tmp1.flush()
    cmd.extend(['--firstboot', tmp1.name])
    if os.path.isfile(cfg.defaultRegisterScript):
        cmd.extend(['--upload', '{}:/root/register.sh'.format(cfg.defaultRegisterScript)])
    c.verbose("Starting virt-builder")
    c.debug("Executing:\n    {}\n".format(" \ \n    ".join(cmd)))
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        print(c.yellow("\nFirst execution of 'virt-builder' failed; trying once more ...\n"))
        sleep(2.0)
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError:
            print(c.RED("virt-builder execution failed; unable to continue"))
            print(c.green("(Please send rsaw@redhat.com this output)\n"))
            raise
