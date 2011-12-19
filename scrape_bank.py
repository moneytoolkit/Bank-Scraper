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
        1: command [add, sync] add = add banks to bank file, sync = get recent transactions
        2: credentials and bank id file
        3: bank list file - to update on an
        """


        # we set up a folder for our own private credentials outside our code path- NEVER check in any credentials
        
        mfile = open('../secure_data/' + opts[1], 'r')
        raw = mfile.read();
        mfile.close()
        creds = simplejson.loads(raw)
        

        if opts[0] =='add':
            # call the loop that gets pages and hands them to the individual scrapers
            HTTPloop = ScrapeHTTPLoop()

            scrape_result = HTTPloop.loop(False, creds, None)

            bank_data_string = simplejson.dumps(scrape_result, indent=2)

            # accs = {}
            # for acc in bank_data_string['accounts']
            #     accs[acc.]

            mfile = open('../secure_data/' + opts[2], 'w')
            raw = mfile.write(bank_data_string);
            mfile.close()

            print 'writing ..........'
            print bank_data_string

        else:

            mfile = open('../secure_data/' + opts[2], 'r')
            raw = mfile.read();
            mfile.close()

            response = simplejson.loads(raw)
            account_list = response['accounts'];

            # call the loop that gets pages and hands them to the individual scrapers
            HTTPloop = ScrapeHTTPLoop()

            scrape_result = HTTPloop.loop(True, creds, account_list)

            bank_data_string = simplejson.dumps(scrape_result, indent=2)

            mfile = open('../secure_data/' + opts[3], 'w')
            raw = mfile.write(bank_data_string);
            mfile.close()

            print 'writing xacts ..........'
            print bank_data_string
        

if __name__ == "__main__":

    browse = WebBrowse()
    
    #browse.doSynchro(sys.argv[1:])

    browse.doAccountList(sys.argv[1:])


