#!/usr/bin/python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
#-------------------------------------------------------------------------------
# Copyright 2015, 2016 Ryan Sawhill Aroha <rsaw@redhat.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#-------------------------------------------------------------------------------

# Modules from standard library
from __future__ import print_function
import subprocess
import re
import os
import tempfile
from sys import stdin, stderr, stdout, exit
import pwd, grp
from time import sleep
import json

# Custom modules
from modules import string_ops as c
from modules import cfg, argparser, builder, installer


def update_cache_file(outfile, input):
    outfile = "{}/{}".format(cfg.tabCacheDir, outfile)
    cfg.debug("Updating cache file {}".format(outfile))
    with open(outfile, 'w') as f:
        json.dump(input, f)


def get_all_osvariants():
    cmd = ['osinfo-query', 'os', '-f', 'short-id']
    cfg.debug("Executing: {}".format(" ".join(cmd)))
    try:
        out = subprocess.check_output(cmd)
    except:
        print(c.RED("Error executing osinfo-query; install libosinfo rpm\n"))
        raise
    allVariants = ['auto']
    for line in out.splitlines()[2:]:
        allVariants.append(line.strip())
    return allVariants


def refresh_cache():
    if not cfg.osvariantChoices:
        cfg.osvariantChoices = get_all_osvariants()
    subprocess.call(['mkdir', '-p', cfg.tabCacheDir])
    update_cache_file('osvariants', cfg.osvariantChoices)
    if not cfg.templateList:
        cfg.templateList = cfg.get_virt_builder_list('json')
    for template in cfg.templateList:
        cfg.templateChoices.append(template['os-version'])
    update_cache_file('templates', cfg.templateChoices)


def build_initial_cache():
    if os.path.isdir(cfg.tabCacheDir):
        return
    cfg.debug("Building initial cache")
    refresh_cache()


def is_valid_os_variant(variant):
    if variant in cfg.osvariantChoices:
        return True
    else:
        return False


def final_interactive_setup():
    # Figure out guest VM name
    if cfg.opts.vmname:
        # If specified on cmdline, use it
        pass
    else:
        # Otherwise generate a guess
        _default_name = re.sub('[.]', '', cfg.opts.templateName)
        if stdout.isatty():
            # If have tty, prompt with default guess
            cfg.opts.vmname = raw_input(c.CYAN("Enter VMNAME ") + c.BOLD("[{}]".format(_default_name)) + c.CYAN(": "))
            if not cfg.opts.vmname:
                cfg.opts.vmname = _default_name
        else:
            # If no tty, use default guess
            print(c.yellow("VMNAME not specified; using '{}'".format(_default_name)))
            cfg.opts.vmname = _default_name
    # Validate selected guest name
    while True:
        match = re.search(r'^{}$'.format(cfg.opts.vmname), cfg.guestList, re.M)
        if match:
            print(c.YELLOW("Already have a VM with the name '{}'".format(cfg.opts.vmname)))
            print(c.BOLD("\nExisting VMs:"))
            print(c.cyan(cfg.guestList.strip()))
            if not stdout.isatty():
                exit(1)
            cfg.opts.vmname = raw_input(c.CYAN("Enter a unique VM name: "))
        else:
            break
    # Prompt for details about guest hostname if not specified on cmdline
    if not cfg.opts.hostname:
        _default_name = '{}.{}'.format(re.sub('[.]', '', cfg.opts.vmname), cfg.opts.dnsdomain)
        if cfg.opts.hostname_prompt and stdout.isatty():
            cfg.opts.hostname = raw_input(c.CYAN("Enter HOSTNAME ") + c.BOLD("[{}]".format(_default_name)) + c.CYAN(" or ") + c.BOLD("!") + c.CYAN(" to skip changing hostname: "))
            if not cfg.opts.hostname:
                cfg.opts.hostname = _default_name
        else:
            c.verbose("  INFO: HOSTNAME not specified; using '{}'".format(_default_name))
            cfg.opts.hostname = _default_name
    # Determine output image format
    if cfg.opts.format in 'auto':
        cfg.opts.format = cfg.templateInfo.get('format')
        if not cfg.opts.format or cfg.opts.format == 'qcow2' or cfg.opts.format == 'raw':
            c.verbose("  INFO: Unable to determine native format of chosen template")
            c.verbose("  INFO: Using qcow2 for output format (change with --format=raw)")
            cfg.opts.format = 'qcow2'
    # Set output image file path/name 
    cfg.opts.outFile = '{}/{}'.format(cfg.opts.imgdir, cfg.opts.vmname)
    if cfg.opts.format in 'qcow2':
        cfg.opts.outFile += '.qcow2'
    # Ensure image file doesn't exist
    while os.path.exists(cfg.opts.outFile):
        print(c.YELLOW("Already have an image file with the name '{}' (in dir '{}')".format(os.path.basename(cfg.opts.outFile), cfg.opts.imgdir)))
        if not stdout.isatty():
            exit(1)
        _x = raw_input(c.CYAN("\nEnter a unique image file name (not incl. path): "))
        cfg.opts.outFile = '{}/{}'.format(cfg.opts.imgdir, _x)
    # Determine image os-variant
    _verbiage = "Chosen"
    if cfg.opts.os_variant == 'auto':
        _verbiage = "Auto-detected"
        cfg.opts.os_variant = cfg.templateInfo.get('osinfo')
        if not cfg.opts.os_variant:
            c.verbose("  INFO: Chosen template doesn't include 'osinfo=' metadata")
            c.verbose("  INFO: Guest OS will not use any special hypervisor features like virt-io")
    # Validate os-variant choice (if one made)
    if cfg.opts.os_variant:
        o = cfg.opts.os_variant
        if is_valid_os_variant(o):
            c.verbose("  INFO: {} os-variant ('{}') was validated by osinfo-query command".format(_verbiage, o))
        else:
            if 'fedora' in o:
                o = 'fedora22'
            elif 'rhel7.' in o:
                o = 'rhel7.0'
            elif 'rhel6.' in o:
                o = 'rhel6.6'
            elif 'rhel5.' in o:
                o = 'rhel5.11'
            if is_valid_os_variant(o):
                c.verbose("  INFO: {} os-variant ('{}') was reset to latest ('{}') validated by osinfo-query".format(_verbiage, cfg.opts.os_variant, o))
                cfg.opts.os_variant = o
            else:
                print(c.yellow("  WARN: Invalid os-variant -- '{}' not listed by command: osinfo-query os -f short-id".format(o)))
                c.verbose("  INFO: Guest OS will not use any special hypervisor features like virt-io")
                cfg.opts.os_variant = None


def main():
    # On very first run, we need to get osinfo-query db & virt-builder template list
    # If tabCacheDir already exists, to speed execution when tab-completing, this does nothing
    build_initial_cache()
    # Parse cmdline arguments (If tab-completing, execution stops before returning)
    # options namespace saved to cfg.opts
    argparser.parse()
    # Get possible os-variants and virt-builder --list output
    if not cfg.osvariantChoices:
        refresh_cache()
    # Test for all needed system commands, appropriate permissions
    from modules import sysvalidator
    sysvalidator.check_system_config()
    # Prompt for any needed info & do final setup steps
    final_interactive_setup()
    # Launch virt-builder
    from modules import builder
    builder.build()
    # Quit if using --debug --debug
    if cfg.debugLvl > 2:
        exit()
    # Launch virt-install
    from modules import installer
    installer.install()
    # Optionally launch serial connection
    if cfg.opts.autoconsole and stdout.isatty():
        if cfg.debugLvl:
            sleep(5.0)
        subprocess.call(['virsh', 'console', cfg.opts.vmname])


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nReceived KeyboardInterrupt. Exiting.")
        exit()
