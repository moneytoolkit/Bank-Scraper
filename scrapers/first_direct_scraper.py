#!/usr/bin/env python
# coding: utf-8

import cookielib, urllib, urllib2

from utils.dateparser import DateParser
from urlparse import urlparse

from utils.utilfuncs import unescape
  
import logging                             

from BeautifulSoup.BeautifulSoup import BeautifulSoup

from models.statementbuilder import StatementBuilder

from scraper import Scraper

#class ReportOpener:
#    def open()

class FirstDirectScraper(Scraper):

    filledCredentials = {}
    
    version = '1.01'
    display = 'First Direct'
    
    questionlist = [
                   {'id': '03', 'display':'User Name', 'x':'0', 'l':'0', 't': 'a'},
                   {'id': '04', 'display':'Electronic Password', 'x':'0', 'l':'0', 't': 'a'},
                   {'id': '06', 'display':'Memorable Answer', 'x':'0', 'l':'0', 't': 'a'}
                   ]
    
    account_names = [{'id':'1', 'htmlkey': 'Joint 1st Account', 'display': 'Joint 1st Account', 'compound': '1st Joint Account', 'type': 'Cheque', 'parser': 'synchronised' },
                    {'id':'2', 'htmlkey': 'Joint Savings Account', 'display': 'Joint Savings Account', 'compound': '1st Joint Savings', 'type': 'Cheque', 'parser': 'synchronised'},
                    {'id':'3', 'htmlkey': '1st Account', 'display': 'Current Account', 'compound': '1st Account', 'type': 'Cheque', 'parser': 'synchronised' },
                    {'id':'4', 'htmlkey': 'Savings Account', 'display': 'Savings Account', 'compound': '1st Savings', 'type': 'Cheque', 'parser': 'synchronised'},
                    {'id':'5', 'htmlkey': 'Joint offset Mortgage', 'display': 'Joint offset Mortgage', 'compound': '1st Joint Mortgage', 'type': 'Credit', 'parser': 'synchronised'},
                    {'id':'6', 'htmlkey': 'offset Mortgage', 'display': 'offset Mortgage', 'compound': '1st Mortgage', 'type': 'Credit', 'parser': 'synchronised'},
                    {'id':'7', 'htmlkey': 'Credit Card', 'display': 'Credit Card', 'compound': '1st Credit Card', 'type': 'Credit', 'parser': 'synchronised'},
                    {'id':'8', 'htmlkey': 'e-Savings Account', 'display': 'e-Savings Account', 'compound': '1st e-Savings', 'type': 'Cheque', 'parser': 'synchronised'},
                    {'id':'9', 'htmlkey': 'Everyday e-Saver', 'display': 'Everyday e-Saver', 'compound': '1st Everyday e-Saver', 'type': 'Cheque', 'parser': 'synchronised'},
                    {'id':'10', 'htmlkey': 'cash e-ISA', 'display': 'cash e-ISA', 'compound': '1st Cash e-ISA', 'type': 'Cheque', 'parser': 'synchronised'},
                    {'id':'11', 'htmlkey': 'Joint Flexiloan', 'display': 'Joint Flexiloan', 'compound': '1st Joint Flexiloan', 'type': 'Credit', 'parser': 'synchronised'},
                    {'id':'12', 'htmlkey': 'Regular Saver', 'display': 'Regular Saver', 'compound': '1st Saver', 'type': 'Cheque', 'parser': 'synchronised'},
                    {'id':'13', 'htmlkey': 'gold card', 'display': 'Gold Card', 'compound': '1st Gold Card', 'type': 'Credit', 'parser': 'synchronised'},
                    {'id':'14', 'htmlkey': 'Flexiloan', 'display': 'Flexiloan', 'compound': '1st Flexiloan', 'type': 'Cheque', 'parser': 'synchronised'},
                    {'id':'15', 'htmlkey': 'Visa', 'display': 'Visa', 'compound': '1st Visa', 'type': 'Credit', 'parser': 'synchronised'},
                    {'id':'16', 'htmlkey': 'Joint Everyday e-Saver', 'display': 'Visa', 'compound': '1st Joint e-Saver', 'type': 'Cheque', 'parser': 'synchronised'},
                    {'id':'17', 'htmlkey': 'Joint Bonus Savings', 'display': 'Joint Bonus Savings', 'compound': '1st Joint Bonus', 'type': 'Cheque', 'parser': 'synchronised'},
                    {'id':'18', 'htmlkey': 'Everyday Savings', 'display': 'Everyday Savings', 'compound': '1st Everyday Savings', 'type': 'Cheque', 'parser': 'synchronised'},
                    {'id':'19', 'htmlkey': 'Joint Everyday Savings', 'display': 'Joint Everyday Savings', 'compound': '1st Joint Everyday', 'type': 'Cheque', 'parser': 'synchronised'}
                ]
        
        
    def __lookupAccount(self, htmlkey):
        for row in self.account_names:
            if row['htmlkey'] == htmlkey:
                return row['id']
        self.unFoundAccount(htmlkey)
        return '0'
    
    
    def __init__(self, passedCreds):
        self.credentials = {}
        
        for cred in self.questionlist:
            self.credentials[cred['display']] = '';            
        
        self.filledCreds = passedCreds
    
    def getQuestions(self):
        return self.questionlist
    
    def getDisplay(self):
        return 'First Direct'
    
    def getCreds(self):
        return self.credentials
    
    def lookupdigit(self, word):
        passcode = self.filledCreds['04']
        
        lupword = word.lower()
        
        if lupword == 'first':
            return passcode[0]
        if lupword == 'second':
            return passcode[1]
        if lupword == 'third':
            return passcode[2]
        if lupword == 'fourth':
            return passcode[3]
        
        if lupword == '1st':
            return passcode[0]
        if lupword == '2nd':
            return passcode[1]
        if lupword == '3rd':
            return passcode[2]
            
        if len(lupword) >= 3 and lupword[-1] == 'h':
            lupword = lupword[0:-2]
            return passcode[int(lupword)-1]
            
        if lupword == 'last':
            return passcode[-1]
        
        if lupword == 'penultimate':
            return passcode[-2]
    
    
    def processAccount(self, acCount, acName, account_path, allofit):
        
        page = self.HexToByte( allofit['body'])
        
        # save this page
        self.output_page("account" + str(acCount) + ".html", page) 
        
        soup = BeautifulSoup(page)
            
        logging.debug('ac path - ' + str(account_path) + ' - end' )
        
        if account_path != "":
            # delete existing current xactions
            
            logging.debug('Processing :) ' )
            
            self.statementbuilder = StatementBuilder(self.facade, account_path, self.token)
           
            # need to get last statement and make a new one every time
            self.statementbuilder.make_recent_dif_statement('Fd-recent', 'Scraper', None) #TODO change this 
                        
            isVisa = False
            loginform=soup.find('input', attrs={'name' : 'cmd_sort_referenceAscending'})
            if loginform != None:
                isVisa = True
                
                bal_tables=soup.findAll('table', attrs={'class' : 'fdTableBackgroundOne'})
                balance_table = bal_tables[2]

                if balance_table <> None:
                    vals = balance_table.findAll('td')

                    if vals:
                        bal = vals[1].text
                        data = bal.replace('&#163;', u'£');
                        data = data.strip(u'£')
                        if data[-1] == 'D':
                            data = data.replace('DB','')
                            data = data.replace('D','')
                            lastbal = int( float(data) * 100 )
                            firstbal = 0 - lastbal
                        else:
                            data = data.replace('CR','')
                            data = data.replace('C','')
                            firstbal = int( float(data) * 100 )
                        
                        self.statementbuilder.set_current_balance(firstbal)    
                   
            
            logging.debug("-----------------------------*******---------------------")
            if isVisa:
                logging.debug("found visa --")
            
            acTable=soup.find('table', attrs={'class' : 'fdStatTable'})
            
            # if no table then no new data afaik
            if acTable != None:
               datarows=acTable.findAll('tr')
               
               next = False
               
                
               # build the post values up
               atts = {}
               
               isFirst = True
               firstbal = 0
               firstdate = ""
               
               lastbal = 0
               lastdate = ""
               
               doBalance = False
               
               dp = DateParser()
                           
               for rows in datarows:
                   vals = rows.findAll('td')
                   
                   if vals:
                       for i, val in enumerate(vals):
                           
                           if val.text:
                               data = val.text.strip()
                               data = unescape(data)
                               data = unicode(data)
                               
                           else:
                               data = ""
                           
                           if data != "&nbsp;":
                               data = data.replace('&nbsp;','')
                               if i == 0:
                                   if data != "":
                                       try:
                                           lastdate = dp.ymd_from_date(dp.date_from_dmy(data,'/'))
                                       except:
                                           logging.warn("Invalid FD date format - probably no transactions")
                                           return
                                       
                                       if firstdate == "":
                                           firstdate = lastdate
                                       
                                   atts['date'] = lastdate
                                   
                               if (i == 1 and not isVisa) or (i == 2 and isVisa):
                                       atts['display'] = data[0:19]
                                       atts['extradisplay'] = data[19:]
                                   
                               if (i == 2 and not isVisa) or (i == 3 and isVisa):
                                   if data != "":
                                       data = data.strip(u'£')
                                       data = data.strip(u'D')
                                       data = data.strip(u'B')
                                       if data == '':
                                           atts['amount'] = 0
                                       else:
                                           atts['amount'] = int( float(data) * 100 )
                                       atts['type'] = 'Debit'
                                           
                               if (i == 3 and not isVisa) or (i == 4 and isVisa):
                                   if data != "":
                                       data = data.strip(u'£')
                                       data = data.strip(u'C')
                                       data = data.strip(u'R')
                                       if data == '':
                                           atts['amount'] = 0
                                       else:
                                           atts['amount'] = int( float(data) * 100 )
                                       atts['type'] = 'Credit'
                                       
                               if not isVisa:
                                   if i == 4:
                                       data = data.strip(u'£')
                                       if data != "":
                                           lastbal = int( float(data) * 100 )
                                           
                                           if isFirst:
                                               isFirst = False
                                               firstbal = lastbal
                                               doBalance = True
                                               
                                   if i == 5:
                                       if doBalance:
                                           doBalance = False
                                           if data == "D":
                                               firstbal = 0 - firstbal
                                           self.statementbuilder.set_current_balance(firstbal) 
                                       
                       self.statementbuilder.make_xact(atts)
           
               self.statementbuilder.put_statement()
               self.current_statement = self.current_statement + 1
        

    def ByteToHex(self,  byteStr ):
        """
        Convert a byte string to it's hex string representation e.g. for output.
        """
        
        # Uses list comprehension which is a fractionally faster implementation than
        # the alternative, more readable, implementation below
        #   
        #    hex = []
        #    for aChar in byteStr:
        #        hex.append( "%02X " % ord( aChar ) )
        #
        #    return ''.join( hex ).strip()        
    
        return ''.join( [ "%02X" % ord( x ) for x in byteStr ] )
        
    def HexToByte(self, hexStr ):
        """
        Convert a string hex byte values into a byte string. The Hex Byte values may
        or may not be space separated.
        """
        # The list comprehension implementation is fractionally slower in this case    
        #
        #    hexStr = ''.join( hexStr.split(" ") )
        #    return ''.join( ["%c" % chr( int ( hexStr[i:i+2],16 ) ) \
        #                                   for i in range(0, len( hexStr ), 2) ] )
     
        bytes = []
    
        for i in range(0, len(hexStr), 2):
            bytes.append( chr( int (hexStr[i:i+2], 16 ) ) )
    
        return ''.join( bytes ).decode("utf-8")

    def  firstPass(self, page):
        soup = BeautifulSoup(page)
        
        loginform=soup.find('form')
        
        action = loginform['action']
        
        urls = urlparse(action);
        self.urlBase = "https://" + urls.netloc
        logging.info("Base URL = " + self.urlBase)
        
        inputs = loginform.findAllNext('input')
        
        values = {}
        
        values['userid'] = self.filledCreds['03']  #username
        
        # build the body content
        data = urllib.urlencode(values)

        self.response = {}
        self.response['url'] = self.ByteToHex(action)
        self.response['data'] = self.ByteToHex(data)
        self.response['method'] = 'POST'
        self.response['step'] = 2
    
    def GetInitialUrl(self, allofit):
        
        body = self.HexToByte( allofit['body'])
        
        # the following is how you could retrieve the headers from the request
        # for head in allofit['headers']:
        #     name = self.HexToByte(head['name'])
        #     val = self.HexToByte(head['value'])
        
        self.firstPass(body)
        
        return 'good'
    
    def DoStep2(self, allofit):
       
        page = self.HexToByte( allofit['body'])
           
        #-------------------------------- Grab the form values -----------------------------------------------
        soup = BeautifulSoup(page)
        
        self.output_page("fd-username.html", page)
    
        loginform=soup.find('form')
    
        action = loginform['action']
        
        inputs = loginform.findAllNext('input')
        
        values = {}
        
        self.response = {}
        
        # build the post values up - there arent any others afaik
                
        ps = loginform.findAllNext('p')
                
        numbers = ps[1].findAllNext('strong')
        
        #not enough lookup digits
        try:
            password =  self.lookupdigit(numbers[0].text) + self.lookupdigit(numbers[1].text) + self.lookupdigit(numbers[2].text) 
        except:
            logging.debug("credentials incorrect")
            return 'credentials incorrect'
        
        answer = self.filledCreds['06']
        
        values['password'] = password
        values['memorableAnswer'] = answer
        
        # build the body content
        data = urllib.urlencode(values)
        
        self.response['url'] = self.ByteToHex(action)
        self.response['data'] = self.ByteToHex(data)
        self.response['method'] = 'POST'
        self.response['step'] = 3
        
        return 'good'
    
    def DoStep3(self, allofit):
        
        scrape_result = "good"
        
        page = self.HexToByte( allofit['body'])
           
        #-------------------------------- Grab the form values -----------------------------------------------
        soup = BeautifulSoup(page)
        
        self.output_page("fd-summary.html", page)
        
        accountTable=soup.find('table', attrs={'class' : 'fdBalancesTable'})
        
        if accountTable != None:
            self.accountLinks=accountTable.findAll('a', attrs={'class' : 'fdActionLink'})
            
            if len(self.accountLinks) == 0:
                #got some kind of message
                scrape_result = 'bank error'
                logging.info('Still got no accounts')
        else:
            logging.debug("No fd table");
            scrape_result = 'credentials incorrect'
            
        return scrape_result
    
    def getacclist(self, facade, accountList, token, step, allofit):    
        self.facade = facade
        self.token = token
    
        scrape_result = 'good'
        
        if step == 1:
            scrape_result = self.GetInitialUrl(allofit)
        elif step == 2:
            scrape_result = self.DoStep2(allofit)
        elif step == 3:
            scrape_result = self.DoStep3(allofit)
            
            self.response = {}
            
            if scrape_result == "good":
                
                self.myAccounts = []
                
                for ac in self.accountLinks:
                    acName = ac.string
                    
                    logging.info("FFF - " + ac['href'])
                    acpair = self.getAccountFromLink(acName, ac['href'])
                        
                    if acpair != None:
                         self.myAccounts.append(acpair)
                    else:
                         logging.error("Cant tell what kind of account this is - with number - " + acnum)
                        
                self.response['url'] = ""
                self.response['data'] = ""
                self.response['method'] = 'END'
                self.response['step'] = 3
                
                scrape_result = "got list"
                
        return scrape_result
    
    def getxactlist(self, facade, accountList, token, step, allofit):    
        self.facade = facade
        self.token = token
         
        scrape_result = 'good'
            
        if step == 1:
            scrape_result = self.GetInitialUrl(allofit)
        elif step == 2:
            scrape_result = self.DoStep2(allofit)
        elif step == 3:
            
            bankurl = self.HexToByte(allofit['bankurl'])
            urls = urlparse(bankurl);
            self.urlBase = "https://" + urls.netloc
            logging.info("Base URL = " + self.urlBase)
            
            scrape_result = self.DoStep3(allofit)
            self.myAccounts = []
            self.response = {}
            
            if scrape_result == "good":
                accounts = []
                
                for ac in self.accountLinks:
                        
                    acLink = ac['href']
                    acName = ac.string
                    
                    theAccountPath = ""
                    
                    logging.info('-------------->' + acName)
                    
                    # do we know about this account
                    acID = self.__lookupAccount(acName)
                    
                    if acID == '0':
                        logging.warn("N-B - unknown account " + acName)
                        
                    logging.info('-------------->' + str(acID))
                    
                    acpair = self.getAccountFromLink(acName, acLink)
                        
               # if we did detect an account number - then try lookimg it up in the list of acconts
                    if acpair != None:
                       acID = acpair['num']
                       logging.info('Checking if we have this acc num in our list----->' + str(acID))
                   
                       # found the newer style account is not in our account list look it up the old way
                       if not (acID in accountList):
                           acID = self.__lookupAccount(acName)
                    else:
                       acID = self.__lookupAccount(acName)
                    
                    # and is this one in our list
                    if acID in accountList:
                        theAccountPath = accountList[acID]
                
                        chunks = acLink.split("'")
                
                        acJsLink = chunks[1]
                
                        url = self.urlBase + acJsLink
                        
                        account = {}
                        account['accountid'] = acID
                        account['href'] = url
                        account['path'] = theAccountPath
                        account['synched'] = False
                        accounts.append(account)
                    else:
                        logging.warn("N-B - account not in users list " + acName + ' - ' + acID)
                    
                # get the next on the list
                # set the url 
        
                accounts[0]['synched'] = True
                self.response['accountlist'] = accounts
                
                # TODO - choose the right url
                self.response['url'] = self.ByteToHex(accounts[0]['href'])
                self.response['data'] = ""
                self.response['method'] = 'GET'
                self.response['step'] = 4
                self.response['accountid'] = accounts[0]['accountid']
                self.response['accountpath'] = accounts[0]['path']
                
                scrape_result = "account list"
        
        elif step == 4:

            accounts = allofit['accountlist']
            
            acCount = allofit['accountid']
            theAccountPath = allofit['accountpath']
            acName = ""
            
            bankurl = self.HexToByte(allofit['bankurl'])
            urls = urlparse(bankurl);
            self.urlBase = "https://" + urls.netloc
            logging.info("Base URL = " + self.urlBase)
            
            logging.debug("PROCESSING - -- -> ")
            logging.debug("acCount - " + acCount + "  acName - " + acName + " acPath - " + str(theAccountPath))

            # do the processing
            
            acLink = self.processAccount(acCount, acName, theAccountPath, allofit) #TODO - cant do this  - have to click back button redo this and click second one
            
            url = ""
            acind = 0
            acit = 0
            # now work out the next url
            for acc in accounts:
                if not acc['synched']:
                    acind = acit
                    url = acc['href']
                    break;
                acit = acit + 1
            
            self.response = {}
            
            # TODO - choose the right url
            
            self.response['data'] = ""
            
            self.response['curaccountid'] = acCount
            self.response['curaccountpath'] = theAccountPath;
            
            if url == "":
                self.response['url'] = ""
                self.response['method'] = 'END'
            else:
                self.response['url'] = self.ByteToHex(url)
                accounts[acind]['synched'] = True
                self.response['method'] = 'GET'
                self.response['accountid'] = accounts[acind]['accountid']
                self.response['accountpath'] = accounts[acind]['path']
            
            self.response['step'] = 4
            
            self.response['accountlist'] = accounts
            
            scrape_result = "got account"
                
        return scrape_result   

    def getAccountFromLink(self, acName, link):
       
        acpair = {}
        
        pos = link.find('SelectedAccount=')
        pos = pos + 16
        
        pos2 = len(link) - 2
        
        actype =  'Cheque'
        
        # might be a credit card
        if (pos2 < 0) or ((pos2 - pos) > 14):
            actype =  'Credit'
            
        acnum = link[pos:pos2]
        
        logging.info(str(acnum))
        
        if len(acnum) > 7 and len(acnum) < 20:
            acpair['name'] = acName;
            acpair['num'] = acnum;
            acpair['type'] = actype;
            
            return acpair
        else:
            return None
