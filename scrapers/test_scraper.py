#!/usr/bin/env python
# coding: utf-8

import cookielib, urllib, urllib2

from urlparse import urlparse

from utils.dateparser import DateParser
  
import logging                             

#from BeautifulSoup.BeautifulSoup import BeautifulSoup

from models.statementbuilder import StatementBuilder

from scraper import Scraper

from utils.utilfuncs import unescape


xacts1 = [
            {'date': "2010-06-13", 'display': 'TEST Xact1', 'amount': 2222, 'type': 'Debit'},
            {'date': "2010-06-14", 'display': 'TEST1 Xact2', 'amount': 4444, 'type': 'Debit'},
            {'date': "2010-06-15", 'display': 'TEST2 Xact1', 'amount': 1322, 'type': 'Debit'},
            {'date': "2010-06-16", 'display': 'TEST3 Xact2', 'amount': 3545, 'type': 'Debit'},
            {'date': "2010-06-19", 'display': 'TEST4 Xact1', 'amount': 222, 'type': 'Debit'},
            {'date': "2010-06-21", 'display': 'TEST5 Xact2', 'amount': 44, 'type': 'Debit'},
            {'date': "2010-06-23", 'display': 'TEST6 Xact3', 'amount': 13226, 'type': 'Credit'},
            {'date': "2010-06-25", 'display': 'TEST-snot Xact4', 'amount': 5544, 'type': 'Debit'}
        ]

class MockLink():
    string = ''
    href = ''
    def __getitem__(self, i):
        if "href" == i:
            return self.href
    
class TestScraper(Scraper):

    filledCredentials = {}
    statementbuilder = None
    
    realUrlChunk = ""
    urlBase = ""
    
    version = '1.01'
    display = 'Test'
    
    questionlist = [{'id': '01', 'display':'Sort Code', 'x':'0', 'l': '6', 't': 'n'},
                   {'id': '02', 'display':'Account Number', 'x':'0', 'l':'8', 't': 'n'}
                ]
    account_names = [{'id':'1', 'htmlkey': 'test current', 'display': 'Current Account', 'compound': 'Test Current', 'type': 'Cheque', 'parser': 'simple'},
                    {'id':'2', 'htmlkey': 'smilemore account', 'display': 'SmileMore Account', 'compound': 'Test More', 'type': 'Cheque', 'parser': 'simple'},
                    {'id':'3', 'htmlkey': 'test saving', 'display': 'Savings Account', 'compound': 'Test Savings', 'type': 'Cheque', 'parser': 'simple'},
                    {'id':'4', 'htmlkey': 'visa classic', 'display': 'Visa', 'compound': 'Test Visa', 'type': 'Credit', 'parser': 'simple'}
                ]
    
    def __lookupAccount(self, htmlkey):
        for row in self.account_names:
            if row['htmlkey'] == htmlkey:
                return row['id']
        self.unFoundAccount(htmlkey)
        return '0'
    
    def processAccount(self, aclink, acCount, acName, account_path):
        
        logging.debug('ac link - ' + aclink )
            
        logging.debug('ac path - ' + str(account_path) + ' - end' )
        
        if account_path != "":
            
            # delete existing current xactions
            
            logging.debug('Processing account ' )
            
            builder = StatementBuilder(self.facade, account_path, self.token)
            self.statementlist.append(builder)
            
            self.statementbuilder = self.statementlist[self.current_statement]
            
            currentBalance = 34505
            
            isVisa = False
                
            
            self.statementbuilder.make_recent_statement('Smile-recent', 'Scraper', None) #TODO change this 
                
            self.statementbuilder.set_current_balance(currentBalance) 
                
            
            for row in xacts1:
                self.statementbuilder.make_xact(row)
                
                
            #self.statementbuilder.set_balance(atts['amount']) #TODO - still use this?
    
            self.statementbuilder.put_statement()
            self.current_statement = self.current_statement + 1
        
    
        return "http:\\blah2.com"
    
        
    def dologin(self, cookiejar, facade, accountList, token):
        # this purely parses html and returns a status after filling in 
        # the list of accounts self.accountLinks
        # eg self.accountLinks=soup.findAll('a',....
        
        self.accountLinks = []
        
        link = MockLink()
        link.string = 'test current'
        link.href ='http://blah.com'
        self.accountLinks.append(link)
        
        link = MockLink()
        link.string = 'test saving'
        link.href ='http://blah.com'
        self.accountLinks.append(link)
        
        
        link = MockLink()
        link.string = 'test no equiv'
        link.href ='http://blah_broke.com'
        self.accountLinks.append(link)
        
        return 'good'
    
    def doscrape(self, facade, accountList, token):
        # acountList = dict of accountname and account paths e.g. /person/dan/account/a1
        scrape_result = 'good'
        self.facade = facade
        self.token = token
    
        logging.info("TestScraper doscrape-" + str(accountList))
        
        # List of statementbuilder - the main thing to return
        self.statementlist = []
        
        cookiejar = None
        
        scrape_result = self.dologin(cookiejar, facade, accountList, token);
        
        logging.debug(scrape_result)

        if scrape_result == "good":
            # test that we have some account links
            
            if len(self.accountLinks) == 0:
                #got some kind of message
                logging.info('Still got no accounts')
                scrape_result = 'credentials incorrect'
                logging.warn('Smile bank credentials incorrect')
    
            else:
                account = self.accountLinks[0]    
                acLink = self.accountLinks[0]['href']
                
            acCount = 0
                
            if scrape_result == 'good':
                #try:
                    for ac in self.accountLinks:
                        acName = self.accountLinks[acCount].string
                        
                        theAccountPath = ""
                        
                        logging.info('-------------->' + acName)
                        
                        
                        acID = self.__lookupAccount(acName)
                        
                        logging.info('-------------->' + str(acID))
                        
                        if acID == '0':
                            logging.warn("N-B - unknown account " + acName)
                        
                        if acID in accountList:
                            theAccountPath = accountList[acID]
                            acCount = acCount + 1
                            acLink = self.processAccount(acLink, acCount, acName, theAccountPath) #TODO - cant do this  - have to click back button redo this and click second one
                        else:
                            logging.warn("N-B - account not in users list" + acName )
                            
                    
        return scrape_result
    
    def getacclist(self, facade, accountList, token):    
        scrape_result = 'good'
        self.facade = facade
        self.token = token
        self.myAccounts = []
    
        logging.info("Finding accounts -" + str(accountList))
        cookiejar = None
        
        scrape_result = self.dologin(cookiejar, facade, accountList, token);
        
        logging.debug(scrape_result)


        if scrape_result == "good":
            # test that we have some account links
            
            if len(self.accountLinks) == 0:
                #got some kind of message
                logging.info('Still got no accounts')
                scrape_result = 'credentials incorrect'
                
            acCount = 0
            
            self.myAccounts = []
            if scrape_result == 'good':
                #try:
                    for ac in self.accountLinks:
                        acName = self.accountLinks[acCount].string
                        self.myAccounts.append(acName)
                        acCount = acCount + 1
                        
                    
        return scrape_result   
