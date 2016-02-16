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

# Modules from standard library
from subprocess import call
from sys import argv, exit
if len(argv) != 3:
    print("Improper arguments")
    exit(2)
cmd = [
    'nice', '-n', '19',
    'dd',
    'of={}'.format(argv[1]),
    'if={}'.format(argv[2]),
    'bs=1M',
    ]
rc = call(cmd)
exit(rc)
