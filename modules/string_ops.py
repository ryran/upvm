# -*- coding: utf-8 -*-
# Copyright 2015 Ravshello Authors
# License: Apache License 2.0 (see LICENSE or http://apache.org/licenses/LICENSE-2.0.html)

# Modules from standard library
from __future__ import print_function
from time import sleep
from re import sub
from sys import stdout

# Configure if color should be enabled, verbose messages printed
enableColor = True
enableVerbose = True

def slow_print(string, interval=.02):
    """Print input *string* 1 char at a time w/ *interval* secs between."""
    for char in string:
        sleep(interval)
        print(char, end='')
        stdout.flush()
    print()

def replace_bad_chars_with_underscores(string,
        pattern='[^A-Za-z0-9:_.-]', repl='_', count=0):
    """Perform some simple character substitution on *string*."""
    return sub(pattern, repl, string, count)

def verbose(message, end='\n'):
    """Print *message* in magenta only if verboseMessages is True."""
    if enableVerbose:
        print(magenta(message), end=end)

def REVERSE(txt):
    """Return text in reverse (& bolded)."""
    if enableColor:
        return '\033[1;1m' + '\033[7m' + str(txt) + '\033[0m'
    return txt

def BOLD(txt):
    """Return text in bold."""
    if enableColor:
        return '\033[1;1m' + str(txt) + '\033[0m'
    return txt

def red(txt):
    """Return text in red."""
    if enableColor:
        return '\033[31m' + str(txt) + '\033[0m'
    return txt

def RED(txt):
    """Return text in bolded red."""
    if enableColor:
        return '\033[1;1m' + '\033[31m' + str(txt) + '\033[0m'
    return txt

def bgRED(txt):
    """Return text in red background (& bolded)."""
    if enableColor:
        return '\033[1;1m' + '\033[41m' + str(txt) + '\033[0m'
    return txt

def yellow(txt):
    """Return text in yellow."""
    if enableColor:
        return '\033[33m' + str(txt) + '\033[0m'
    return txt

def YELLOW(txt):
    """Return text in bolded yellow."""
    if enableColor:
        return '\033[1;1m' + '\033[33m' + str(txt) + '\033[0m'
    return txt

def blue(txt):
    """Return text in blue."""
    if enableColor:
        return '\033[34m' + str(txt) + '\033[0m'
    return txt

def BLUE(txt):
    """Return text in bolded blue."""
    if enableColor:
        return '\033[1;1m' + '\033[34m' + str(txt) + '\033[0m'
    return txt

def bgBLUE(txt):
    """Return text in blue background (& bolded)."""
    if enableColor:
        return '\033[1;1m' + '\033[44m' + str(txt) + '\033[0m'
    return txt

def green(txt):
    """Return text in green."""
    if enableColor:
        return '\033[32m' + str(txt) + '\033[0m'
    return txt

def GREEN(txt):
    """Return text in bolded green."""
    if enableColor:
        return '\033[1;1m' + '\033[32m' + str(txt) + '\033[0m'
    return txt

def cyan(txt):
    """Return text in cyan."""
    if enableColor:
        return '\033[36m' + str(txt) + '\033[0m'
    return txt

def CYAN(txt):
    """Return text in bolded cyan."""
    if enableColor:
        return '\033[1;1m' + '\033[36m' + str(txt) + '\033[0m'
    return txt

def magenta(txt):
    """Return text in magenta."""
    if enableColor:
        return '\033[35m' + str(txt) + '\033[0m'
    return txt

def MAGENTA(txt):
    """Return text in bolded magenta."""
    if enableColor:
        return '\033[1;1m' + '\033[35m' + str(txt) + '\033[0m'
    return txt
