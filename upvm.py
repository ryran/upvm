#!/usr/bin/python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
#-------------------------------------------------------------------------------
# Copyright 2015, 2016 upvm Contributors (see CONTRIBUTORS.md file in source)
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
import os
from sys import stdout, exit
from time import sleep
import json

# Custom modules
from modules import string_ops as c
from modules import cfg, argparser

def update_cache_file(outfile, input):
    outfile = "{}/{}".format(cfg.tabCacheDir, outfile)
    c.debug("Updating cache file {}".format(outfile))
    with open(outfile, 'w') as f:
        json.dump(input, f)

def get_all_osvariants():
    cmd = ['osinfo-query', 'os', '-f', 'short-id']
    c.debug("Executing: {}".format(" ".join(cmd)))
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
    c.debug("Building initial cache")
    refresh_cache()

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
    # Prompt user for any missing (required) input
    from modules import finalprompter
    finalprompter.prompt_final_checks()
    # Launch virt-builder
    from modules import builder
    builder.build()
    # Quit if requested
    if cfg.opts.build_image_only:
        exit()
    # Launch virt-install
    from modules import installer
    installer.install()
    # Optionally launch serial connection
    if cfg.opts.autoconsole and stdout.isatty():
        if cfg.opts.loglevel < 20:
            sleep(5.0)
        subprocess.call(['virsh', 'console', cfg.opts.vmname])

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nReceived KeyboardInterrupt. Exiting.")
        exit()
