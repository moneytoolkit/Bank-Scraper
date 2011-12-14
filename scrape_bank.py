#!/usr/bin/env python


import sys
import logging
import simplejson

from scrape_loop import ScrapeHTTPLoop

# yes i want to see it all!!

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
d = logging.debug


class WebBrowse():
    """Our main object to set up the browser loop.
    """

  #accountList is the list of accounts a user has
  def doAccountList(self, opts):
    """call the loop to log into our accounts.

    opts: the command line array minus the program name - the first value is the name of a credential file.
    """


    # we set up a folder for our own private credentials outside our code path- NEVER check in any credentials
    
    file = open('../secure_data/' + opts[0], 'r')
    raw = file.read();
    file.close()
    creds = simplejson.loads(raw)
    
    print creds


    url = 'https://www.nwolb.com/default.aspx'


    HTTPloop = ScrapeHTTPLoop()

    scrape_result = HTTPloop.loop(url, creds)

    print simplejson.dumps(scrape_result, indent=2)
    

  def doSynchro(self, opts):

    
    file = open('./tests/data/natwest-creds.json', 'r')
    raw = file.read();
    file.close()

    creds = simplejson.loads(raw)
    cb = creds[0]['credentials']
    print cb







    scraper = TestBankScraper(cb)
    scraper.facade = Facade('danm')
    scraper.token = 'nobsack'

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
    
    #browse.doSynchro(sys.argv[1:])

    browse.doAccountList(sys.argv[1:])


