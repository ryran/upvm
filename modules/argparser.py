# -*- coding: utf-8 -*-
# Copyright 2016 upvm Contributors (see CONTRIBUTORS.md file in source)
# License: Apache License 2.0 (see LICENSE file in source)

# Modules from standard library
from __future__ import print_function
from sys import exit, stderr
try:
    import configargparse as argparse
    haveConfigargparse = True
except:
    print("Missing optional python module: configargparse\n"
          "Install it to allow use of config files:\n"
          "  yum/dnf install python-pip; pip install configargparse\n", file=stderr)
    import argparse
    haveConfigargparse = False
try:
    import argcomplete
    haveArgcomplete = True
except:
    print("Missing optional python module: argcomplete\n"
          "Install it to enable bash auto-magic tab-completion:\n"
          "  yum/dnf install python-pip; pip install argcomplete\n"
          "  activate-global-python-argcomplete; (Then restart shell)\n", file=stderr)
    haveArgcomplete = False
import json

# Custom modules
from . import string_ops as c
from . import cfg

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def read_cache_file(infile):
    with open('{}/{}'.format(cfg.tabCacheDir, infile), 'r') as f:
        out = json.load(f)
    return byteify(out)

class CustomFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)
            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            # change to 
            #    -s, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    #parts.append('%s %s' % (option_string, args_string))
                    parts.append('%s' % option_string)
                parts[-1] += ' %s'%args_string
            return ', '.join(parts)

def parse():
    fmt = lambda prog: CustomFormatter(cfg.prog)
    description = "Leverage virt-builder & virt-install to spin up new VMs with ease"
    version = "{} v{} last mod {}".format(cfg.prog, cfg.__version__, cfg.__date__)
    epilog = ""
    if haveConfigargparse:
        epilog += (
            "ABOUT CONFIG FILES:\n"
            "  All of the above options can also be set in config files {0} or\n"
            "  {1} (e.g., 'loglevel = debug') or specified via environment\n"
            "  variables capitalized and prefixed with '{2}_' (e.g., {2}_LOGLEVEL=debug).\n"
            "  See {3} for examples of proper config-file syntax\n"
            "  and keep in mind that cmdline values override environment variables which\n"
            "  override config file values which override defaults.\n\n").format(cfg.cfgfileSystem, cfg.cfgfileUser, cfg.prog.upper(), cfg.cfgfileExample)
    epilog += (
            "VERSION:\n"
            "  {}\n"
            "  See <http://github.com/ryran/upvm> to report bugs or RFEs").format(version)
    if haveConfigargparse:
        p = argparse.ArgumentParser(
            add_config_file_help=False,
            add_env_var_help=False,
            auto_env_var_prefix="{}_".format(cfg.prog.upper()),
            default_config_files=[cfg.cfgfileSystem, cfg.cfgfileUser],
            prog=cfg.prog,
            description=description,
            add_help=False,
            epilog=epilog,
            formatter_class=fmt)
            #formatter_class=argparse.RawDescriptionHelpFormatter)
    else:
        p = argparse.ArgumentParser(
            prog=cfg.prog,
            description=description,
            add_help=False,
            epilog=epilog,
            formatter_class=fmt)
    # Main modal options
    grp0 = p.add_argument_group(
        'SIMPLE OPTIONS',
        description="Tweak runtime behavior of {}.".format(cfg.prog))
    grp0.add_argument(
        '--loglevel', choices=['debug', 'info', 'error'], default='info',
        help="Control verbosity during operation; with 'debug', all external command-calls are logged, including full virt-builder & virt-install cmdlines; with 'info', tidbits of status messages are printing along the way")
    grp0.add_argument(
        '--build-image-only', action='store_true',
        help="Quit after virt-builder finishes making the image file")
    grp0.add_argument(
        '--nocolor', dest='enableColor', action='store_false',
        help="Disable all color terminal enhancements")
    grp0.add_argument(
        '--noconsole', dest='autoconsole', action='store_false',
        help="Disable post-install auto-execution of 'sudo virsh console VMNAME' (automatically disabled when running with no tty)")
    grp0.add_argument(
        '--cachedir', default='/var/cache/{}'.format(cfg.prog), dest='vbCachedir', metavar='VBCACHEDIR',
        help="Set the directory for virt-builder cached templates (default: '/var/cache/{}' which is only writable by members of the 'libvirt' group; note that this contrasts with virt-builder's default more secure & more wasteful behavior of saving per-user cache in homedirs)".format(cfg.prog))
    grp0.add_argument(
        '-h', dest='showUsage', action='store_true',
        help="Show short usage summary and exit")
    grp0.add_argument(
        '--help', dest='showHelp', action='store_true',
        help="Show this help message and exit")
    grpA = p.add_argument_group(
        'SELECTING INITIAL IMAGE TO BUILD',
        description="Choose template to build with virt-builder.")
    g1 = grpA.add_mutually_exclusive_group()
    g1.add_argument(
        'templateName', nargs='?', metavar='TEMPLATE', choices=read_cache_file('templates'),
        help="Specify the template to install from")
    g1.add_argument(
        '-l', '--list', action='store_true',
        help="List available templates")
    grpA.add_argument(
        '--arch', choices=['x86_64', 'i386', 'i686', 'ia64', 'armv71', 'ppc', 'ppc64', 'ppc64le', 'aarch64', 'sparc64', 's390', 's390x'],
        help="Specify architecture (defaults to same architecture you're running)")
    grpA.add_argument(
        '--info', dest='showMetadataOnly', action='store_true',
        help="Print virt-builder metadata for chosen template")
    # Critical virt-install options
    grpB = p.add_argument_group(
        'IMPORTANT HARDWARE-LEVEL (VM) OPTIONS',
        description="Guest hardware configured by virt-install (after image is built).")
    grpB.add_argument(
        '-n', '--name', metavar='VMNAME', dest='vmname',
        help="Guest name will be VMNAME (defaults to value of TEMPLATE)")
    grpB.add_argument(
        '--os-variant', metavar='OS', default='auto', choices=read_cache_file('osvariants'),
        help="Optionally override auto-detected os-type to disable virt-io (default is 'auto', unlike virt-install itself; see virt-install --os-variant)")
    # Optional virt-builder options
    grpAA = p.add_argument_group(
        'TOTALLY OPTIONAL OS-LEVEL OPTIONS',
        description="Disk image modifications done by virt-builder.")
    grpAA.add_argument(
        '--root-password', metavar='SELECTOR',
        help="If this option is not used (either on cmdline or via config file), {} will prompt for the root password at runtime and optionally save it to per-user config-file for future use; syntax: use 'password:PASSWORD' or 'file:FILENAME' or 'random' (see virt-builder --root-password for more)".format(cfg.prog))
    grpAA.add_argument(
        '--dnsdomain', metavar='DOMAIN', default='example.com',
        help="Set DNS domain name to be appended to auto-generated HOSTNAME (default: 'example.com'; keep in mind however that this option has no effect if --hostname is specified)")
    g2 = grpAA.add_mutually_exclusive_group()
    g2.add_argument(
        '--hostname',
        help="Set system hostname inside the OS (default: automatically uses VM name; specify '!' to prevent changing the hostname, which implies --no-dhcphostname option)")
    g2.add_argument(
        '--hostname-prompt', action='store_true',
        help="Configure {} to always prompt for system hostname when not specified (default: automatically use VM name + value of DOMAIN with no prompt)".format(cfg.prog))
    grpAA.add_argument(
        '--no-dhcphostname', dest='add_dhcp_hostname', action='store_false',
        help="Disable the default behavior of adding 'DHCP_HOSTNAME=<HOSTNAME>' to ifcfg-eth0")
    grpAA.add_argument(
        '--imgdir', metavar='DIR', default='/var/lib/{}'.format(cfg.prog),
        help="Set directory where image file will be saved to and launched from (default: '/var/lib/{0}' which is a simple directory-backed libvirt storage pool named '{0}')".format(cfg.prog))
    grpAA.add_argument(
        '--size',
        help="Set output disk image size (default: native template size; example: '7G')")
    grpAA.add_argument(
        '--format', choices=['auto', 'raw', 'qcow2'], default='auto',
        help="Set output disk image format (default: 'auto', to auto-detect based on input image format; however, until this is implemented in virt-builder, it will fallback to qcow2)")
    grpAA.add_argument(
        '--timezone',
        help="Set system timezone inside the OS (use traditional syntax, i.e., paths rooted in /usr/share/zoneinfo, e.g.: 'Europe/London' or 'America/Los_Angeles' or 'Asia/Calcutta')")
    grpAA.add_argument(
        '--rhsm-key', metavar='ORGID:KEY',
        help="With or without this option, {} creates a /root/register script inside the guest which can be used to interactively register to RHN Classic or RHSM; this option edits that script to include an RHSM activation key created by you at access.redhat.com/management/activation_keys -- i.e., so the script can be run without requiring a user/password (to use this option, specify both the organization ID and the activation key, e.g., '0123456789:my_activation_key'); IMPORTANT NOTE: this does not run the /root/register script for you".format(cfg.prog))
    grpAA.add_argument(
        '--ssh-pubkey', metavar='FILE', action='append',
        default=['~/.ssh/authorized_keys', '~/.ssh/id_[dr]sa.pub', '~/.ssh/id_ecdsa.pub', '~/.ssh/id_ed25519.pub'],
        help="Inject specific ssh pubkeys (option may be used more than once) into the /root/.ssh/authorized_keys file of the guest (default: contents of local '~/.ssh/authorized_keys' and all present pubkeys with standard filenames -- see man page explanation for ssh -i option -- will be automatically injected)")
    grpAA.add_argument(
        '--upload', metavar='FILE:DEST', action='append',
        help="Upload local FILE to DEST in disk image; warning: directories in DEST must exist and file uid/gid & perms are preserved (may be used more than once)")
    grpAA.add_argument(
        '--run', metavar='SCRIPT', action='append',
        help="Launch disk image inside small container, copy local SCRIPT into disk image and execute it chrooted into guest filesystem (may be used more than once)")
    grpAA.add_argument(
        '--run-command', metavar='CMD+ARGS', action='append',
        help="Launch disk image inside small container, and execute command chrooted into guest filesystem (may be used more than once)")
    grpAA.add_argument(
        '--firstboot', metavar='SCRIPT', action='append',
        help="Install SCRIPT inside disk image such that it will run on first boot (may be used more than once)")
    grpAA.add_argument(
        '--firstboot-command', metavar='CMD+ARGS', action='append',
        help="Configure disk image such that when guest first boots it will execute command (may be used more than once)")
    grpAA.add_argument(
        '--install', metavar='PKG,PKG,@GROUP...', action='append',
        help="Launch disk image inside small container and execute 'yum/apt-get install' against named package(s), chrooted into guest filesystem (using this auto-triggers SELinux relabel; may be used more than once)")
    grpAA.add_argument(
        '--firstboot-install', metavar='PKG,PKG,@GROUP...', action='append',
        help="Configure disk image such that when guest first boots it will install named package(s) (may be used more than once)")
    grpAA.add_argument(
        '--selinux-relabel', action='store_true',
        help="Trigger an SELinux relabel on first boot (critical if any important files are changed)")
    grpAA.add_argument(
        '--vbuilder-arg', '-B', metavar='ARG', action='append',
        help="Add ARG as an extra option/argument to the virt-builder command which creates the disk image (may be used more than once; NOTE: to pass options that start with a dash, use '--vbuilder-arg=--option' or '-B=-o', for example: '-B=--verbose -B=--update -B=--copy-in=/localpath:/mnt/remote')")
    # Optional virt-install options
    grpBB = p.add_argument_group(
        'TOTALLY OPTIONAL HARDWARE-LEVEL (VM) OPTIONS',
        description="Guest hardware configured by virt-install (after image is built). Each option\ncorresponds with virt-install option of same name. More configurability is\npossible than described. See virt-install man page.")
    grpBB.add_argument(
        '-m', '--memory', metavar='OPTIONS', default=1024,
        help="If this option is omitted, the guest will be defined with a RAM allocation of 1024 MiB; in its simplest form OPTIONS can be the amount of RAM in MiB; more complicated example: '-m 512,maxmemory=4096' (which would set the default to 512 MiB but allow raising up to 4 GiB without powering off)")
    grpBB.add_argument(
        '-c', '--vcpus', metavar='OPTIONS', default=1,
        help="If this option is omitted, the guest will be allocated a single virtual CPU; in its simplest form OPTIONS can be the number of CPUs; more complicated example: '-c 1,maxvcpus=4' (which would set the default 1 CPU but allow raising to 4 without powering off)")
    grpBB.add_argument(
        '-d', '--disk', metavar='OPTIONS', action='append',
        help="In its simplest form OPTIONS can be 'size=N' to add a new disk of size N GiB to the guest")
    grpBB.add_argument(
        '-w', '--network', metavar='OPTIONS', action='append',
        help="If this option is omitted, a single NIC will be created in the guest and connected to a bridge (if one exists) or the 'default' virtual network; if this option is used once it will modify the default NIC; this option can be specified multiple times to setup more than one NIC; in its simplest form OPTIONS can be 'bridge=BRIDGE' (where BRIDGE is a bridge device name, e.g., 'br0') or 'network=NAME' (where NAME is a virtual network, e.g., 'default'); more complicated example: '-w network=default -w bridge=br0' (where the 1st NIC would be connected to the default private network and the 2nd would be connected to the [presumably public] bridge br0)")
    grpBB.add_argument(
        '--vinstall-arg', '-I', metavar='ARG', action='append',
        help="Add ARG as an extra option/argument to the virt-install command which creates a guest from the vb-created disk image (may be used more than once; NOTE: to pass options that start with a dash, use '--vinstall-arg=--option' or '-I=-o', for example: '-I=--cpu=core2duo -I=--video=cirrus -I=--graphics=vnc,password=mypass')")
    # Parse and return
    if haveArgcomplete:
        argcomplete.autocomplete(p)
    o = p.parse_args()
    if o.showUsage:
        p.print_usage()
        print("\nRun {} --help for full help page".format(cfg.prog))
        exit()
    if o.showHelp:
        p.print_help()
        exit()
    # Respect cmdline requests about color
    c.enableColor = o.enableColor
    # And verbosity
    import logging
    o.loglevel = getattr(logging, o.loglevel.upper())
    if o.loglevel > 10:
        c.enableDebug = False
        if o.loglevel > 20:
            c.enableVerbose = False
    # Save namespace to global cfg module
    cfg.opts = o
