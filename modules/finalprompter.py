# -*- coding: utf-8 -*-
# Copyright 2016 upvm Contributors (see CONTRIBUTORS.md file in source)
# License: Apache License 2.0 (see LICENSE file in source)

# Modules from standard library
from __future__ import print_function
import subprocess
import os
import re
from sys import stdout, exit

# Custom modules
from . import cfg
from . import string_ops as c

def is_valid_os_variant(variant):
    if variant in cfg.osvariantChoices:
        return True
    else:
        return False

def check_prompt_root_pw():
    if not cfg.opts.root_password:
        if stdout.isatty():
            # If have tty, prompt for pass
            while True:
                passwd = raw_input(c.CYAN("Enter root password for new VM or enter '") + c.BOLD("random") + c.CYAN("' or '") + c.BOLD("disabled") + c.CYAN("' or file path : "))
                if passwd:
                    break
            cfg.opts.root_password = ''
            if passwd == 'random':
                c.verbose("Password for root will be randomly generated")
            elif passwd == 'disabled':
                c.verbose("Password auth for root will be disabled")
            elif os.path.isfile(os.path.expanduser(passwd)):
                passwd = os.path.expanduser(passwd)
                c.verbose("Password for root will be set by reading first line of file '{}'".format(passwd))
                cfg.opts.root_password = 'file:'
            else:
                c.verbose("Password for root will be set to string '{}'".format(passwd))
                cfg.opts.root_password = 'password:'
            cfg.opts.root_password += passwd
            save_passwd = raw_input(c.CYAN("Save password choice as default to '{}'? ".format(cfg.cfgfileUser)) + c.BOLD("[y]/n") + c.CYAN(" : "))
            if save_passwd != 'n':
                subprocess.call(['mkdir', '-p', os.path.dirname(cfg.cfgfileUser)])
                with open(os.path.expanduser(cfg.cfgfileUser), 'a') as f:
                    f.write('# Added by {}:\nroot-password = {}\n'.format(cfg.prog, cfg.opts.root_password))
                c.verbose("Wrote 'root-password = {}' to {}".format(cfg.opts.root_password, cfg.cfgfileUser))
        else:
            print(c.RED("No root password specified; aborting"))
            print("Either run with stdin/stdout connected to tty to interactively enter password or\n"
                  "  Use '--root-password password:PASSWORDSTRING' or\n"
                  "  Use '--root-password file:PASSWORDFILE' or\n"
                  "  Use '--root-password random'\n"
                  "  Note that any of these can be specified in config file as well")
            exit(1)

def check_prompt_vm_name():
    if cfg.opts.vmname:
        # If specified on cmdline, use it
        pass
    else:
        # Otherwise generate a guess
        _default_name = re.sub('[.]', '', cfg.opts.templateName)
        if stdout.isatty():
            # If have tty, prompt with default guess
            cfg.opts.vmname = raw_input(c.CYAN("Enter VMNAME ") + c.BOLD("[{}]".format(_default_name)) + c.CYAN(" : "))
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
            cfg.opts.vmname = raw_input(c.CYAN("Enter a unique VM name : "))
        else:
            break

def check_prompt_hostname():
    if not cfg.opts.hostname:
        _default_name = '{}.{}'.format(re.sub('[.]', '', cfg.opts.vmname), cfg.opts.dnsdomain)
        if cfg.opts.hostname_prompt and stdout.isatty():
            cfg.opts.hostname = raw_input(c.CYAN("Enter HOSTNAME ") + c.BOLD("[{}]".format(_default_name)) + c.CYAN(" or ") + c.BOLD("!") + c.CYAN(" to skip changing hostname : "))
            if not cfg.opts.hostname:
                cfg.opts.hostname = _default_name
        else:
            c.verbose("HOSTNAME not specified; using '{}'".format(_default_name))
            cfg.opts.hostname = _default_name

def checkset_img_format():
    if cfg.opts.img_format in 'auto':
        cfg.opts.img_format = cfg.templateInfo.get('format')
        if not cfg.opts.img_format or cfg.opts.img_format == 'qcow2' or cfg.opts.img_format == 'raw':
            c.verbose("Unable to determine native format of chosen template")
            c.verbose("Using qcow2 for output format (change with --format=raw)")
            cfg.opts.img_format = 'qcow2'

def check_prompt_img_outfilepath():
    cfg.opts.outFile = '{}/{}'.format(cfg.opts.img_dir, cfg.opts.vmname)
    if cfg.opts.img_format in 'qcow2':
        cfg.opts.outFile += '.qcow2'
    # Ensure image file doesn't exist
    while os.path.exists(cfg.opts.outFile):
        print(c.YELLOW("Already have an image file with the name '{}' (in dir '{}')".format(os.path.basename(cfg.opts.outFile), cfg.opts.img_dir)))
        if not stdout.isatty():
            exit(1)
        _x = raw_input(c.CYAN("\nEnter a unique image file name (not incl. path) : "))
        cfg.opts.outFile = '{}/{}'.format(cfg.opts.img_dir, _x)

def checkset_validate_osvariant():
    _adjective = "Chosen"
    if cfg.opts.os_variant == 'auto':
        _adjective = "Auto-detected"
        cfg.opts.os_variant = cfg.templateInfo.get('osinfo')
        if not cfg.opts.os_variant:
            c.verbose("Chosen template doesn't include 'osinfo=' metadata")
            c.verbose("Guest OS will not use any special hypervisor features like virt-io")
    # Validate os-variant choice (if one made)
    if cfg.opts.os_variant:
        o = cfg.opts.os_variant
        if is_valid_os_variant(o):
            c.verbose("{} os-variant ('{}') was validated by osinfo-query command".format(_adjective, o))
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
                c.verbose("{} os-variant ('{}') was reset to latest ('{}') validated by osinfo-query".format(_adjective, cfg.opts.os_variant, o))
                cfg.opts.os_variant = o
            else:
                print(c.yellow("  WARN: Invalid os-variant -- '{}' not listed by command: osinfo-query os -f short-id".format(o)))
                c.verbose("Guest OS will not use any special hypervisor features like virt-io")
                cfg.opts.os_variant = None

def prompt_final_checks():
    # Prompt for root password if none specified
    check_prompt_root_pw()
    # Prompt for VM name if none specified and ensure no collision with existing
    check_prompt_vm_name()
    # Set default hostname or prompt for guest hostname if --hostname-prompt used
    check_prompt_hostname()
    # Auto-detect output image format
    checkset_img_format()
    # Set output image file path/name & prompt if collision
    check_prompt_img_outfilepath()
    # Auto-detect image os-variant and validate that against os-info command
    checkset_validate_osvariant()

