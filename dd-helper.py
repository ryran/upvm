#!/usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Copyright 2016 upvm Contributors (see CONTRIBUTORS.md file in source)
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

import subprocess
from sys import argv, exit
from os import devnull
outfile, infile = argv[1], argv[2]
null = open(devnull, 'w')
rc = subprocess.call(['findmnt', '-no', 'target', outfile], stdout=null, stderr=null)
if rc == 0:
    # If findmnt reports outfile is mounted
    exit(2)
lsof = subprocess.Popen(['nice', 'lsof', '-tlS', outfile], stdout=subprocess.PIPE, stderr=null)
output = lsof.communicate()[0]
if output:
    # If lsof reports anything using our outfile
    exit(3)
null.close()
dd = ['nice', 'dd', 'of={}'.format(outfile), 'if={}'.format(infile), 'bs=1M']
exit(subprocess.call(dd))
