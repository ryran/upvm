# upvm - Leverage virt-builder &amp; virt-install to spin up new VMs with ease

## What?
upvm aims to make it crazy easy to spin up new virtual machines using pre-installed OS-images provided by existing  [virt-builder](http://libguestfs.org/virt-builder.1.html) repos. Once an image is cached locally, the process of image creation + and guest instantiation should take less than a minute. Take a look:

![upvm screenshot](http://people.redhat.com/rsawhill/upvm-demo1.png)

#### Where?
upvm supervises `virt-builder` and `virt-install` commands that connect to your local libvirt daemon. Virtual machine images will be saved (by default) to `/var/lib/upvm` and virtual machines will be started on your system.

#### Why not vagrant? What about RHEV and OpenStack?
upvm might not be for you if:

- you've already invested the time to get vagrant to work for you
- you already have all the images you need in a RHEV environment
- you want to spin up new machines in an OpenStack cloud

#### I don't like image files! LVM is the best!
I used to use LVM for all my VMs too ... so upvm can use `virt-builder` to generate an image and then write that image out to a block device you specify with the `--primary-blockdev` option. This optional feature of course requires some sudo access (to run [dd-helper.py](https://github.com/ryran/upvm/blob/master/dd-helper.py) as root) which upvm will walk you through the first time you do it.

## Install

#### yum/dnf (RPM) install in RHEL 7.2+ or Fedora 22+:
```
command -v dnf && dnf=dnf || dnf=yum
sudo $dnf install http://people.redhat.com/rsawhill/rpms/latest-rsawaroha-release.rpm
sudo $dnf install upvm
sudo /usr/share/upvm/initial-setup
upvm -h
```

#### Non-rpm install:
1. Install libguestfs-tools (`virt-builder` command)
1. Make sure you have the `virsh` and `virt-install` commands as well
1. `git clone https://github.com/ryran/upvm.git`
1. `cd upvm`
1. `sudo ./initial-setup`
1. `./upvm.py -h`

#### Optional extras:
Regardless of install method, you will be missing 2 *HIGHLY-recommended* but *optional* python modules. One provides bash-tab-completion and the other provides config-file support. `upvm` will print warnings about this to stderr but if you want to get them now:

1. If RHEL7, ensure access to [EPEL](https://fedoraproject.org/wiki/EPEL)
1. `sudo $dnf install pip`
1. `sudo pip install argcomplete`
1. `sudo activate-global-python-argcomplete`
1. `sudo pip install configargparse`

## I have some VMs ...
Are you annoyed with always having to open the `virt-manager` GUI to do stuff with you VMs?

- Get [valine](https://github.com/ryran/valine).

## Help page

```
usage: upvm [--loglevel {debug,info,error}] [--build-image-only] [--nocolor]
            [--noconsole] [--cachedir VBCACHEDIR] [-h] [--help] [-l]
            [--arch {x86_64,i386,i686,ia64,armv71,ppc,ppc64,ppc64le,aarch64,sparc64,s390,s390x}]
            [--info] [-n VMNAME] [--os-variant OS] [--root-password SELECTOR]
            [--dnsdomain DOMAIN] [--hostname HOSTNAME | --hostname-prompt]
            [--no-dhcphostname] [--img-dir DIR] [--img-size SIZE]
            [--img-format {auto,raw,qcow2}] [--timezone TIMEZONE]
            [--ssh-pubkey FILE] [--upload FILE:DEST] [--run SCRIPT]
            [--run-command CMD+ARGS] [--firstboot SCRIPT]
            [--firstboot-command CMD+ARGS] [--install PKG,PKG,@GROUP...]
            [--firstboot-install PKG,PKG,@GROUP...] [--selinux-relabel]
            [--vbuilder-arg ARG] [--primary-blockdev BLOCKDEV] [-m OPTIONS]
            [-c OPTIONS] [-d OPTIONS] [-w OPTIONS] [--boot OPTIONS | --uefi]
            [--vinstall-arg ARG]
            [TEMPLATE]

Leverage virt-builder & virt-install to spin up new VMs with ease

SIMPLE OPTIONS:
  Tweak runtime behavior of upvm.

  --loglevel {debug,info,error}
                        Control verbosity during operation; with 'debug', all
                        external command-calls are logged, including full
                        virt-builder & virt-install cmdlines; with 'info',
                        tidbits of status messages are printing along the way
  --build-image-only    Quit after virt-builder finishes making the image file
  --nocolor             Disable all color terminal enhancements
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
                        Specify architecture in case there are multiple
                        choices (defaults to same architecture as upvm)
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
  --img-dir DIR         Set directory where image file will be saved to and
                        launched from (default: '/var/lib/upvm' which is a
                        simple directory-backed libvirt storage pool named
                        'upvm')
  --img-size SIZE       Set output disk image size (default: native template
                        size; example: '7G')
  --img-format {auto,raw,qcow2}
                        Set output disk image format (default: 'auto', to
                        auto-detect based on input image format; however,
                        until this is implemented in virt-builder, it will
                        fallback to qcow2)
  --timezone TIMEZONE   Set system timezone inside the OS (use traditional
                        syntax, i.e., paths rooted in /usr/share/zoneinfo,
                        e.g.: 'Europe/London' or 'America/Los_Angeles' or
                        'Asia/Calcutta')
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
  --vbuilder-arg, -B ARG
                        Add ARG as an extra option/argument to the virt-
                        builder command which creates the disk image (may be
                        used more than once; NOTE: to pass options that start
                        with a dash, use '--vbuilder-arg=--option' or '-B=-o',
                        for example: '-B=--verbose -B=--update -B=--copy-
                        in=/localpath:/mnt/remote')

TOTALLY OPTIONAL HARDWARE-LEVEL (VM) OPTIONS:
  Guest hardware configured by virt-install (after image is built). Most options
  correspond with virt-install options of same name. More configurability is
  possible than described. See virt-install man page.

  --primary-blockdev BLOCKDEV
                        To use this option, specify a BLOCKDEV like
                        '/dev/sdb2' or '/dev/vg/logvol' and then in that case,
                        the image generated by virt-builder [using the above
                        options] will be written to BLOCKDEV and then deleted;
                        the first time you try this as a non-root user, upvm
                        will exit with a warning explaining how to add the
                        appropriate sudo access to the dd helper-wrapper
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
                        new disk of size N GiB to the guest from the default
                        storage pool (which will likely result in a new auto-
                        named sparse qcow2 image file in
                        /var/lib/libvirt/images); more examples: '-d
                        device=cdrom' or '-d /path/iso,device=cdrom' or '-d
                        /path/existing/file' or '-d pool=storagepool,size=5'
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
  --boot OPTIONS        If this option is omitted, its value will default to
                        'cdrom,hd,network,menu=on,useserial=on'
  --uefi                This is option does not directly correspond to a virt-
                        install option of the same name; this option can only
                        be used if the above '--boot' is omitted; in that case
                        it will result in adding 'uefi' to the above-mentioned
                        default boot opts
  --vinstall-arg, -I ARG
                        Add ARG as an extra option/argument to the virt-
                        install command which creates a guest from the vb-
                        created disk image (may be used more than once; NOTE:
                        to pass options that start with a dash, use
                        '--vinstall-arg=--option' or '-I=-o', for example:
                        '-I=--cpu=core2duo -I=--video=cirrus
                        -I=--graphics=vnc,password=mypass')

ABOUT CONFIG FILES:
  All of the above options can also be set in config files /etc/upvm.conf or
  ~/.config/upvm.conf (e.g., 'loglevel = debug') or specified via environment
  variables capitalized and prefixed with 'UPVM_' (e.g., UPVM_LOGLEVEL=debug).
  See /usr/share/upvm/example.conf for examples of proper config-file syntax
  and keep in mind that cmdline values override environment variables which
  override config file values which override defaults.

VERSION:
  upvm v0.10.6 last mod 2016/02/16
  See <http://github.com/ryran/upvm> to report bugs or RFEs
```
