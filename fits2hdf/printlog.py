# -*- coding: utf-8 -*-

"""
printlog.py
===========

Printing and logging utilities.

"""

import sys
from colorama import Fore


class LinePrint(object):
    """
    Print things to stdout on one line dynamically

    Instead of creating multiple lines, update current line with new data.
    """

    def __init__(self, data):
        sys.stdout.write("\r\x1b[K" + data.__str__())
        sys.stdout.flush()


class PrintLog(object):
    """
    Print / log based on verbosity level

    Verbosity level: 0 - 4
    0: Print errors and pa only
    1: Print H1
    2: Print H1 + H2
    3: Print H1 + H2 + H3
    4: Print all
    5: Print all + debugging info
    """

    def __init__(self, verbosity=4):
        self.vlevel = verbosity

    def h1(self, headstr):
        """ Print a string as a header """
        if self.vlevel >= 1:
            print(Fore.GREEN + '\n%s' % headstr)
            line = ""
            for ii in range(len(headstr)):
                line += "-"
            print(Fore.GREEN + line)
            print(Fore.WHITE)

    def h2(self, headstr):
        """ Print a string as a header """
        if self.vlevel >= 2:
            print('\n###  ', headstr)

    def h3(self, headstr):
        """ Print a string as a 3rd level header """
        if self.vlevel >= 3:
            print("\t", headstr)

    def pp(self, text):
        """ Print a text string """
        if self.vlevel >= 4:
            print(text)

    def pa(self, text):
        """ Always print """
        print(text)

    def debug(self, text):
        """ Print debug information to screen """
        if self.vlevel >= 5:
            print(text)

    def err(self, text):
        """ Print out an error message / warning string """
        print(Fore.RED + "ERROR: " + str(text) + Fore.WHITE)

    def warn(self, text):
        """ Print out a warning message """
        print("WARN: " + str(text))


