#!/usr/bin/env python

import logging
import sys
import os
import re

from urlparse import urlparse

from BeautifulPoop.BeautifulSoup import BeautifulSoup
from BeautifulPoop.BeautifulSoup import NavigableString

from utils.dateparser import DateParser


from BeautifulPoop.termcolor import colored, cprint


class UglySoup(BeautifulSoup):

  # use this to revert to previous type
  printAsText = True;

  def __init__(self, markup=""):
        BeautifulSoup.__init__(self, markup)

  def ppp(self, url):
    if self.printAsText:
        c = "\n" * 4
        c = c + '~' * 120
        c = c + colored("\n    START OF DOCUMENT", 'red', attrs=['bold']) + " --> " + url + "\n"
        c = c + '~' * 120



        for tag in self.html.contents:

            if isinstance(tag, NavigableString):
              c = c + tag + "<-ns\n"
            elif tag.name == 'head':
              c = c + ">>>>HEADER<<<<\n"
            else:
              c = c + tag.__str__(None, False) + "\n"



        c = c + '~' * 120
        c = c + colored("\n    END OF DOCUMENT\n", 'red', attrs=['bold'])
        c = c + '~' * 120
        c = c + "\n" * 4

        return c
    else:
      return self.prettify()
