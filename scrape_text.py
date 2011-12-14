#!/usr/bin/env python

# 


import logging
import sys
import os
import re

import simplejson

from urlparse import urlparse

from BeautifulPoop.BeautifulSoup import BeautifulSoup
from BeautifulPoop.BeautifulSoup import NavigableString
from BeautifulPoop.termcolor import colored, cprint

from BeautifulPoop.UglySoup import UglySoup
from utils.dateparser import DateParser

import mechanize
from mechanize import FormNotFoundError


#*** (1) debugging a particular bank - import the right one....

from scrapers.natwest_scraper import NatWestScraper

# from scrapers.lloyds_scraper import LloydsScraper 
# from scrapers.halifax_scraper import HalifaxScraper 

class Facade:

    def __init__(self, user):
        self.user = user


# yes i want to see it all!!

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
d = logging.debug



#*** (2) the bank to test
# override the scaper of choice to set up some settings
# class TestBankScraper(LloydsScraper):
# class TestBankScraper(NatWestScraper):

class TestBankScraper(NatWestScraper):

  # override
  def _setupBrowser(self):
    #*** (3) initialise the right base!
    #LloydsScraper._setupBrowser(self)
    NatWestScraper._setupBrowser(self)

    #>>>>>>>>>>>>>>>>>>>>>>>> Some debug things

    #self.b.set_debug_redirects(True)
    # Log HTTP response bodies (ie. the HTML, most of the time).
    #self.b.set_debug_responses(True)
    # Print HTTP headers.
    #self.b.set_debug_http(True)


#>>>>>>>>>>>>>>>>>>>>>>>>>> Next bit important for NatWest iFrames

    # Don't handle Refresh redirections
    #self.b.set_handle_refresh(False)


  def _pp(self, name, page):

    soup = UglySoup(page)

    print "\n>>>>>>>>>>>>>>>>>" + name



class WebBrowse():


  #accountList is the list of accounts a user has
  def doAccountList(self, opts):

    creds = {}

    scraper = TestBankScraper(creds)

    # are we parsing a raw file..........
    
    file = open('./pagedump/' + opts[0], 'r')
    raw = file.read();
    file.close()

    soup = UglySoup(raw)

    print soup.ppp("test file loaded")

    scraper.myAccounts = []
    scraper.accountLinks = []

    #***(5) call the right function

    print scraper.doStep4({}, raw)
    #scraper._parseLinks(raw)
    #scraper._parseNatWestLinks

    print str(scraper.myAccounts)

    return 'good'


  def doSynchro(self, opts):

    
    file = open('./tests/data/natwest-creds.json', 'r')
    raw = file.read();
    file.close()

    creds = simplejson.loads(raw)
    cb = creds[0]['credentials']
    print cb



    scraper = TestBankScraper(cb)
    scraper.facade = Facade('danm')
    scraper.token = 'splat'

    scraper._setupBrowser()


    #file = open('./tests/data/account1.html', 'r')
    file = open('./tests/data/account2.html', 'r')
    raw = file.read();
    file.close()

    soup = UglySoup(raw)

    print soup.ppp("test file loaded")


    scraper._processNormAccount( raw, ['Person','DanM','Account','a1'], 2304 )

    #scraper._processCCAccount( raw, ['Person','DanM','Account','a2'], -456.09 )

    s = scraper.statementlist[0]

    sm = {}
    sm['balance'] = s.getSynchBalance()
    sm['xacts'] = s.getxactlist()
    sm['path'] = s.get_s_path()

    print simplejson.dumps(sm, indent = 4)



  def display(self, opts):
    file = open(opts[0], 'r')
    raw = file.read();
    file.close()

    soup = UglySoup(raw)

    print soup.ppp("test file loaded")



if __name__ == "__main__":



    browse = WebBrowse()
    

    # just text display out a grabbed page as passed in on the command line

    #  browse.display(sys.argv[1:])


    # or do a real list or a grab


    #browse.doSynchro(sys.argv[1:])

    browse.doAccountList(sys.argv[1:])


