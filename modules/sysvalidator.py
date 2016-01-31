# -*- coding: utf-8 -*-
# Copyright 2016 upvm Contributors (see CONTRIBUTORS.md file in source)
# License: Apache License 2.0 (see LICENSE file in source)

# Modules from standard library
from __future__ import print_function
import subprocess
import os
import tempfile
from sys import exit
import pwd, grp
import json

# Custom modules
from . import cfg
from . import string_ops as c

# Set username
myUser = pwd.getpwuid(os.getuid()).pw_name

def ret(returnCode):
    """Return True if *returnCode* is 0."""
    if returnCode == 0:
        return True
    else:
        return False

def call(cmd, showStdout=False, showStderr=False, shell=False):
    """Execute *cmd* and return True on success."""
    c.debug("Executing: {}".format(" ".join(cmd)))
    null = open(os.devnull, 'w')
    out = err = None
    if not showStdout:
        out = null
    if not showStderr:
        err = null
    rc = subprocess.call(cmd, shell=shell, stdout=out, stderr=err)
    null.close()
    return ret(rc)

def print_template_metadata(template):
    print("{0:17}: {1}".format("template", template['os-version']))
    for key in template:
        if not key in 'notes' and not key in 'os-version':
            print("{0:17}: {1}".format(key, template[key]))
    if template.get('notes'):
        if template['notes'].get('C'):
            print("notes:\n{}".format(template['notes']['C']))
        else:
            print("notes:\n{}".format(template['notes']))

def check_virtbuilder_version():
    if not call(['virt-builder', '--version']):
        print(c.RED("Error executing virt-builder; try installing libguestfs-tools rpm\n"))
        exit(1)

def if_no_template_requested_then_print_vblist_and_quit():
    if cfg.opts.list:
        # If cmdline -l/--list: print virt-builder --list & quit
        print(cfg.get_virt_builder_list())
        exit()
    if not cfg.opts.templateName:
        # No template specified: print error & give choice to show virt-builder --list & quit
        print(c.YELLOW("No template specified"))
        cfg.prompt_for_template_and_exit()

def check_if_requested_template_exists():
    if not cfg.opts.templateName in cfg.templateChoices:
        print(c.YELLOW("Invalid template specified"))
        cfg.prompt_for_template_and_exit()

def isolate_metadata_for_chosen_vb_template():
    """Save json for chosen virt-builder template."""
    for template in cfg.templateList:
        if template['os-version'] == cfg.opts.templateName:
            cfg.templateInfo = template

def if_metadata_requested_then_print_and_quit():
    if cfg.opts.showMetadataOnly:
        print_template_metadata(cfg.templateInfo)
        exit()

def check_virsh_version():
    if not call(['virsh', '--version']):
        print(c.RED("Error executing virsh; try installing libvirt-client rpm\n"))
        exit(1)

def check_virtinstall_version():
    if not call(['virt-install', '--version']):
        print(c.RED("Error executing virt-install; try installing virt-install rpm\n"))
        exit(1)

def testconnect_hypervisor():
    """Exit if unable to connect via virsh to default URI."""
    # Set default libvirt hypervisor connection to local system if unset
    os.environ['LIBVIRT_DEFAULT_URI'] = os.environ.get('LIBVIRT_DEFAULT_URI', 'qemu:///system')
    if not call(['virsh', 'uri'], showStderr=True):
        print(c.RED("Error connecting to {}".format(os.environ['LIBVIRT_DEFAULT_URI'])))
        if os.environ['LIBVIRT_DEFAULT_URI'] == 'qemu:///system':
            print("You need to execute the initial setup program -- as root run:")
            print(c.green("  /usr/share/{}/initial-setup".format(cfg.prog)))
        else:
            print("The environment variable 'LIBVIRT_DEFAULT_URI' is customized")
            print("If this is not intentional, remove the declaration from your shell config")
        exit(1)

def check_for_missing_imgdir():
    if not os.path.isdir(cfg.opts.img_dir):
        print(c.RED("Image dir '{}' does not exist".format(cfg.opts.img_dir)))
        if cfg.opts.img_dir == '/var/lib/{}'.format(cfg.prog):
            print("You need to execute the initial setup program -- as root run:")
            print(c.green("  /usr/share/{}/initial-setup".format(cfg.prog)))
        exit(1)

def check_user_in_libvirt_group():
    if os.getuid() and myUser not in grp.getgrnam('libvirt').gr_mem:
        print(c.RED("Current user ({}) not in the 'libvirt' system group".format(myUser)))
        if os.path.isdir('/var/lib/{}'.format(cfg.prog)):
            print("As root, run:")
            print(c.green("  usermod -aG libvirt {}".format(myUser)))
        else:
            print("You need to execute the initial setup program -- as root run:")
            print(c.green("  /usr/share/{}/initial-setup".format(cfg.prog)))
        exit(1)

def check_for_writable_imgdir():
    c.debug("Testing write perms by creating tempfile in {}".format(cfg.opts.img_dir))
    try:
        f = tempfile.TemporaryFile(dir=cfg.opts.img_dir)
        f.close()
    except:
        dirstat = os.stat(cfg.opts.img_dir)
        user = pwd.getpwuid(dirstat.st_uid).pw_name
        group = grp.getgrgid(dirstat.st_gid).gr_name
        print(c.RED("Unable to create new file in image dir '{}' owned by {}:{}".format(cfg.opts.img_dir, user, group)))
        if myUser in grp.getgrnam(group).gr_mem:
            print("Your user ({}) *is* a member of the appropriate group ({}); however ...\n"
                  "Your current login session is not running with that group credential\n"
                  "To fix this, open a new session (ssh/su -) or log out & log back in (GUI)".format(myUser, group))
        else:
            print("Either fix directory permissions as root or specify alternate dir with '--img-dir' option")
        exit(1)

def try_capture_existing_vm_names():
    """Capture list of existing VM names and exit on failure."""
    cmd = ['virsh', 'list', '--all', '--name']
    c.debug("Executing: {}".format(" ".join(cmd)))
    try:
        cfg.guestList = subprocess.check_output(cmd)
    except:
        print(c.RED("\nUnknown error executing '{}'".format(" ".join(cmd))))
        exit(1)

def check_system_config():
    check_virtbuilder_version()
    if_no_template_requested_then_print_vblist_and_quit()
    check_if_requested_template_exists()
    isolate_metadata_for_chosen_vb_template()
    if_metadata_requested_then_print_and_quit()
    check_virsh_version()
    check_virtinstall_version()
    testconnect_hypervisor()
    check_for_missing_imgdir()
    ##check_user_in_libvirt_group()
    check_for_writable_imgdir()
    try_capture_existing_vm_names()
