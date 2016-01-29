# upvm
Leverage virt-builder &amp; virt-install to spin up new VMs with ease

### Upcoming release

Date of [first release](https://github.com/ryran/upvm/milestones/0.10.0%20albino%20salamander%20%28first%20release%29) (including rpm for RHEL7/Fedora): Sunday January 31st

### Requirements

You need:

- libvirt, libguestfs-tools (`virt-builder`), virt-install

These two are not required, but are highly recommended:
 
1. `pip install argcomplete; activate-global-python-argcomplete`
1. `pip install configargparse`


### Help page

```
$ upvm --help
usage: upvm [--debug] [--nocolor] [--quiet] [--noconsole]
            [--cachedir VBCACHEDIR] [-h] [--help] [-l]
            [--arch {x86_64,i386,i686,ia64,armv71,ppc,ppc64,ppc64le,aarch64,sparc64,s390,s390x}]
            [--info] [-n VMNAME] [--os-variant OS] [--root-password SELECTOR]
            [--dnsdomain DOMAIN] [--hostname HOSTNAME | --hostname-prompt]
            [--no-dhcphostname] [--imgdir DIR] [--size SIZE]
            [--format {auto,raw,qcow2}] [--rhsm-key ORGID:KEY]
            [--ssh-pubkey FILE] [--upload FILE:DEST] [--run SCRIPT]
            [--run-command CMD+ARGS] [--firstboot SCRIPT]
            [--firstboot-command CMD+ARGS] [--install PKG,PKG,@GROUP...]
            [--firstboot-install PKG,PKG,@GROUP...] [--selinux-relabel]
            [-m OPTIONS] [-c OPTIONS] [-d OPTIONS] [-w OPTIONS]
            [TEMPLATE]

Leverage virt-builder & virt-install to spin up new VMs with ease

Note: Args that start with '--' (eg. --debug) can also be set in a config file
(/usr/share/upvm/example.conf or /etc/upvm.conf or ~/.config/upvm.conf or ). The recognized
syntax for setting (key, value) pairs is based on the INI and YAML formats (e.g. key=value or
foo=TRUE). For full documentation of the differences from the standards please refer to the
ConfigArgParse documentation. If an arg is specified in more than one place, then commandline
values override config file values which override defaults.

SIMPLE OPTIONS:
  Tweak runtime behavior of upvm.

  --debug               Enable printing extra debug messages (once: all
                        external command-calls and cache-writing/loading;
                        twice: adds '-v' to virt-builder; 3 times: adds '-x'
                        option to virt-builder and triggers exit before
                        execution of virt-install
  --nocolor             Disable all color terminal enhancements
  --quiet               Hide most non-critical INFO/WARN messages
  --noconsole           Disable post-install auto-execution of 'sudo virsh
                        console VMNAME' (automatically disabled when running
                        with no tty)
  --cachedir VBCACHEDIR
                        Set the directory for virt-builder cached templates
                        (default: '/var/cache/upvm' which is only writable by
                        members of the 'libvirt' group; note that this
                        contrasts with virt-builder's default more secure &
                        more wasteful behavior of saving per-user cache in
                        homedirs)
  -h                    Show short usage summary and exit
  --help                Show this help message and exit

SELECTING INITIAL IMAGE TO BUILD:
  Choose template to build with virt-builder.

  TEMPLATE              Specify the template to install from
  -l, --list            List available templates
  --arch {x86_64,i386,i686,ia64,armv71,ppc,ppc64,ppc64le,aarch64,sparc64,s390,s390x}
                        Specify architecture (defaults to same architecture
                        you're running)
  --info                Print virt-builder metadata for chosen template

IMPORTANT HARDWARE-LEVEL (VM) OPTIONS:
  Guest hardware configured by virt-install (after image is built).

  -n, --name VMNAME     Guest name will be VMNAME (defaults to value of
                        TEMPLATE)
  --os-variant OS       Optionally override auto-detected os-type to disable
                        virt-io (default is 'auto', unlike virt-install
                        itself; see virt-install --os-variant)

TOTALLY OPTIONAL OS-LEVEL OPTIONS:
  Disk image modifications done by virt-builder.

  --root-password SELECTOR
                        If this option is not used (either on cmdline or via
                        config file), upvm will prompt for the root password
                        at runtime and optionally save it to per-user config-
                        file for future use; syntax: use 'password:PASSWORD'
                        or 'file:FILENAME' or 'random' (see virt-builder
                        --root-password for more)
  --dnsdomain DOMAIN    Set DNS domain name to be appended to auto-generated
                        HOSTNAME (default: 'example.com'; keep in mind however
                        that this option has no effect if --hostname is
                        specified)
  --hostname HOSTNAME   Set system hostname inside the OS (default:
                        automatically uses VM name; specify '!' to prevent
                        changing the hostname, which implies --no-dhcphostname
                        option)
  --hostname-prompt     Configure upvm to always prompt for system hostname
                        when not specified (default: automatically use VM name
                        + value of DOMAIN with no prompt)
  --no-dhcphostname     Disable the default behavior of adding
                        'DHCP_HOSTNAME=<HOSTNAME>' to ifcfg-eth0
  --imgdir DIR          Set directory where image file will be saved to and
                        launched from (default: '/var/lib/upvm' which is a
                        simple directory-backed libvirt storage pool named
                        'upvm')
  --size SIZE           Set output disk image size (default: native template
                        size; example: '7G')
  --format {auto,raw,qcow2}
                        Set output disk image format (default: 'auto', to
                        auto-detect based on input image format; however,
                        until this is implemented in virt-builder, it will
                        fallback to qcow2)
  --rhsm-key ORGID:KEY  With or without this option, upvm creates a
                        /root/register script inside the guest which can be
                        used to interactively register to RHN Classic or RHSM;
                        this option edits that script to include an RHSM
                        activation key created by you at
                        access.redhat.com/management/activation_keys -- i.e.,
                        so the script can be run without requiring a
                        user/password (to use this option, specify both the
                        organization ID and the activation key, e.g.,
                        '0123456789:my_activation_key'); IMPORTANT NOTE: this
                        does not run the /root/register script for you
  --ssh-pubkey FILE     Inject specific ssh pubkeys (option may be used more
                        than once) into the /root/.ssh/authorized_keys file of
                        the guest (default: contents of local
                        '~/.ssh/authorized_keys' and all present pubkeys with
                        standard filenames -- see man page explanation for ssh
                        -i option -- will be automatically injected)
  --upload FILE:DEST    Upload local FILE to DEST in disk image; warning:
                        directories in DEST must exist and file uid/gid &
                        perms are preserved (may be used more than once)
  --run SCRIPT          Launch disk image inside small container, copy local
                        SCRIPT into disk image and execute it chrooted into
                        guest filesystem (may be used more than once)
  --run-command CMD+ARGS
                        Launch disk image inside small container, and execute
                        command chrooted into guest filesystem (may be used
                        more than once)
  --firstboot SCRIPT    Install SCRIPT inside disk image such that it will run
                        on first boot (may be used more than once)
  --firstboot-command CMD+ARGS
                        Configure disk image such that when guest first boots
                        it will execute command (may be used more than once)
  --install PKG,PKG,@GROUP...
                        Launch disk image inside small container and execute
                        'yum/apt-get install' against named package(s),
                        chrooted into guest filesystem (using this auto-
                        triggers SELinux relabel; may be used more than once)
  --firstboot-install PKG,PKG,@GROUP...
                        Configure disk image such that when guest first boots
                        it will install named package(s) (may be used more
                        than once)
  --selinux-relabel     Trigger an SELinux relabel on first boot (critical if
                        any important files are changed)

TOTALLY OPTIONAL HARDWARE-LEVEL (VM) OPTIONS:
  Guest hardware configured by virt-install (after image is built). Each option
  corresponds with virt-install option of same name. More configurability is
  possible than described. See virt-install man page.

  -m, --memory OPTIONS  If this option is omitted, the guest will be defined
                        with a RAM allocation of 1024 MiB; in its simplest
                        form OPTIONS can be the amount of RAM in MiB; more
                        complicated example: '-m 512,maxmemory=4096' (which
                        would set the default to 512 MiB but allow raising up
                        to 4 GiB without powering off)
  -c, --vcpus OPTIONS   If this option is omitted, the guest will be allocated
                        a single virtual CPU; in its simplest form OPTIONS can
                        be the number of CPUs; more complicated example: '-c
                        1,maxvcpus=4' (which would set the default 1 CPU but
                        allow raising to 4 without powering off)
  -d, --disk OPTIONS    In its simplest form OPTIONS can be 'size=N' to add a
                        new disk of size N GiB to the guest
  -w, --network OPTIONS
                        If this option is omitted, a single NIC will be
                        created in the guest and connected to a bridge (if one
                        exists) or the 'default' virtual network; if this
                        option is used once it will modify the default NIC;
                        this option can be specified multiple times to setup
                        more than one NIC; in its simplest form OPTIONS can be
                        'bridge=BRIDGE' (where BRIDGE is a bridge device name,
                        e.g., 'br0') or 'network=NAME' (where NAME is a
                        virtual network, e.g., 'default'); more complicated
                        example: '-w network=default -w bridge=br0' (where the
                        1st NIC would be connected to the default private
                        network and the 2nd would be connected to the
                        [presumably public] bridge br0)

VERSION:
  upvm v0.0.9~beta4 last mod 2016/01/28
  See <http://github.com/ryran/upvm> to report bugs or RFEs
```
