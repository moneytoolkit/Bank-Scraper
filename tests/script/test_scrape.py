#!/usr/bin/env python

import sys
import unittest
import logging

from controllers import post_controller
from controllers.front_controller import FrontController

class TestScrape(unittest.TestCase):

    def nontest_1_listy(self):
        user = 'danm'
        
        cc = post_controller.POSTController(user)
        
        #file = open('./tests/data/test-creds.json', 'r')
        
        #file = open('./tests/data/smile-creds.json', 'r')
        file = open('./tests/data/lloyds-creds2.json', 'r')
        
        body = file.read();
        
        
        fc = FrontController()
        
        # get the credentials passed in the request
        credentials = fc.from_json(body)
        
        # load a person record from file if needed
        #person = self.from_json(person_resp)
        
        # get the account list
        scrape_result = cc.do_list_creds(credentials)
        
        # and construct the response
        logging.debug("got account list response: " + scrape_result)
        
        if scrape_result == 'good':
            credentials[0]['accountlist'] = cc.scc.myAccounts
            credentials[0]['message'] = scrape_result
        
            print fc.to_json(credentials, 2) 
        else:
            result = '{"message": "' + scrape_result + '", "bankid": "' + bankId + '", "accounts": [] }'
            code = 200
            print result
        
        a = 200
        self.assertEqual(a, 200)
        
    def test_2_scrapy(self):
        user = 'danm'
        
        cc = post_controller.POSTController(user)
        
        #file = open('./tests/data/test-creds.json', 'r')
        
        #file = open('./tests/data/smile-creds.json', 'r')
        file = open('./tests/data/lloyds-creds.json', 'r')
        #file = open('./tests/data/lloyds-creds-wrong.json', 'r')
        #file = open('./tests/data/lloyds-creds-offshore.json', 'r')
        
        body = file.read();
        
        
        fc = FrontController()
        
        # get the credentials passed in the request
        credentials = fc.from_json(body)
        
        # load a person record from file if needed
        #person = self.from_json(person_resp)
        
        # and do the synchronisation
        scrape_result = cc.do_synch_creds(fc, credentials, None)
        
        # now construct the response
        if scrape_result != "good":
            result = cc.response
            print result
        else:
            logging.debug( "last sync old enough to do a sync")

            credentials[0]['accountlist'] = cc.getStatementLists()
            credentials[0]['message'] = scrape_result
            credentials[0]['builder'] = cc.scc.getBuilder();
            print user
            print fc.to_json(credentials, 2)
            

        a = 200
        self.assertEqual(a, 200)