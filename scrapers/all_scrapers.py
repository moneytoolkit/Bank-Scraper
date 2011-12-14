#!/usr/bin/env python
# coding: utf-8

from scrapers.first_direct_scraper import FirstDirectScraper
from scrapers.natwest_scraper import NatWestScraper
from scrapers.rbs_scraper import RbsScraper

from scrapers.test_scraper import TestScraper
from scrapers.test_scraper_acnum import TestScraperAcNum

import logging

class AllScrapers():

    version = '1.100';


    __new_banklist = {

        
        'www.firstdirect.com':{'id': 'www.firstdirect.com', 'display':'First Direct', 'classname':'FirstDirectScraper',
                'url': 'https://www1.firstdirect.com/1/2/idv.Logoff?nextPage=fsdtBalances',
                'parser': 'synchronised',
                'builder': 'sliding',
                'accounts': [{'id':'1', 'htmlkey': 'current account', 'display': 'Current Account'},
                             {'id':'2', 'htmlkey': 'savings account', 'display': 'Savings Account'}]
            },
        'www.natwest.com':{'id': 'www.natwest.com', 'display':'NatWest', 'classname':'NatWestScraper',
                    'url': 'https://www.nwolb.com/default.aspx',
                    'parser': 'synchronised',
                    'builder': 'sliding',
                    'accounts': [{'id':'1', 'htmlkey': 'current account', 'display': 'Current Account'},
                                {'id':'2', 'htmlkey': 'savings account', 'display': 'Savings Account'}]
                    },

        'www.rbsdigital.com':{'id': 'www.rbsdigital.com', 'display':'RBS', 'classname':'RbsScraper',
                    'url': 'https://www.rbsdigital.com/default.aspx',
                    'parser': 'synchronised',
                    'builder': 'sliding',
                    'accounts': [{'id':'1', 'htmlkey': 'current account', 'display': 'Current Account'},
                                {'id':'2', 'htmlkey': 'savings account', 'display': 'Savings Account'}]
                    }

    }

    
    __private_banklist = {
        'www.mtk_test.com':{'id': 'www.mtk_test.com', 'display':'Test Scrape', 'classname':'TestScraper',
            'url': 'http://www.moneytoolkit.com',
            'parser': 'simple',
            'accounts': []
        },
        'www.mtk_test_acnum.com':{'id': 'www.mtk_test.com', 'display':'Test Scrape', 'classname':'TestScraperAcNum',
            'url': 'http://www.moneytoolkit.com',
            'parser': 'simple',
            'accounts': []
        }


    }

    def __init__(self):
        pass


    def getNewScraperList(self):
        # dont return the test ones
        return self.__new_banklist


    def getStartUrl(self, id):
        bl = None
        if id in self.__new_banklist:
            bl = self.__new_banklist
        
        if bl != None:
            return bl['url']
        else:
            return ''


    def getScraperType(self, id):
        if id == None:
            return 'simple'
        # make sure we have the latest banks
        self.getScraperListAndroid()

        bl = None
        if id in self.__new_banklist:
            bl = self.__new_banklist
        if id in self.__private_banklist:
            bl = self.__private_banklist

        if bl != None:
            if id in bl:
                return bl[id]['parser']
            else:
                return 'simple'


    def getScraper(self, key, creds):
        returnBank = None

        logging.debug('looking for ' + key)

        bl = None
        if key in self.__new_banklist:
            bl = self.__new_banklist
        if key in self.__private_banklist:
            bl = self.__private_banklist

        if bl != None:
            if key in bl:
                matching_accounts = bl[key]
                try:
                    bankob = globals()[matching_accounts["classname"]]
                    returnBank = bankob(creds)

                except KeyError, e:
                    logging.warn("Key error " + e.message)
                    returnBank = None

        return returnBank