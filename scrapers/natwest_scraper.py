#!/usr/bin/env python
# coding: utf-8


import cookielib, urllib, urllib2

from utils.dateparser import DateParser
from urlparse import urlparse

from utils.utilfuncs import unescape
  
import logging                             
import re

from BeautifulSoup.BeautifulSoup import BeautifulSoup

from models.statementbuilder import StatementBuilder

from scraper import Scraper

#class ReportOpener:
#    def open()

class NatWestScraper(Scraper):

    filledCredentials = {}
    
    version = '1.02'
    display = 'NatWest'

    questionlist = [{'id': '01', 'display':'Customer number', 'x':'0', 'l': '10','t': 'n'},
                   {'id': '02', 'display':'Your PIN', 'x':'0', 'l':'4', 't': 'n'},
                   {'id': '03', 'display':'Your Password', 'x':'0', 'l':'30', 't': 'a'}
                ]

    # need this dummy thing whilst the old lookup code is still in place
    account_names = [{'id':'1', 'htmlkey': 'Platinum Plus', 'display': 'Lloyds Platinum Plus', 'compound': 'Lloyds Platinum', 'type': 'Cheque', 'parser': 'simple' }
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
        return 'NatWest'
    
    def getCreds(self):
        return self.credentials
    

    def getSid(self):
        return "NatWest";

    def doStep1(self, allofit, page):
        
        body = page
        
        scrape_result = 'good'
        logging.info("NatWest page1")


        # the following is how you could retrieve the headers from the request
        # for head in allofit['headers']:
        #     name = self.HexToByte(head['name'])
        #     val = self.HexToByte(head['value'])
        
        
        # write out the start page
        self.output_page("1_first_page.html", body)


        soup = BeautifulSoup(body);

        frame = soup.find('frame', id='ctl00_secframe');

        if frame != None:

            action = self.urlBase + '/' + frame['src'];

            #<frame id="ctl00_secframe" title="Security Frame" frameborder="0" src="login.aspx?refererident=774C53DCE4C17556595C91973A6DF1A0A1F6242E&amp;cookieid=100714"></frame>
        
            self.response = {}
            self.response['url'] = self.ByteToHex(action)
            self.response['data'] = ""
            self.response['method'] = 'GET'
            self.response['step'] = 2
        else:
            logging.debug('NatWest frame link error - ')
            scrape_result = 'bank error'

        
        return scrape_result



    def doStep2(self, allofit, page):
       
        #-------------------------------- Grab the form values -----------------------------------------------
        soup = BeautifulSoup(page)
        
        self.output_page("natwest-username.html", page)
    
        loginform=soup.find('form', attrs={'name': 'aspnetForm'})

        if loginform == None:
            logging.debug('NatWest no login form')
            return 'bank error'


        action = self.urlBase + '/' + loginform['action']
        
        values = self.parseForm(loginform)
        
        # fill in our credentials
        values["ctl00$mainContent$LI5TABA$DBID_edit"] = self.filledCreds['01']   #customer number

        # build the body content
        data = urllib.urlencode(values)
        self.response = {}
        self.response['url'] = self.ByteToHex(action)
        self.response['data'] = self.ByteToHex(data)
        self.response['method'] = 'POST'
        self.response['step'] = 3
        
        return 'good'



    def doStep3(self, allofit, page):
        
        scrape_result = "good"
        
        #-------------------------------- Grab the form values -----------------------------------------------
        soup = BeautifulSoup(page)

        # write out the start page
        self.output_page("natwest-security.html", page)
        
        scrape_result = 'good'
        logging.info("NatWest security page2")

        # check if we got returned
        # check for the password input ctl00$mainContent$LI5TABA$DBID_edit then we didnt move on
        errorDiv=soup.findAll('input', attrs={'name' : 'ctl00$mainContent$LI5TABA$DBID_edit'})

        if len(errorDiv) != 0:
            logging.info("NatWest security page1 still - customer number bad")
            return  'credentials incorrect'   # if we get here then the form was found hence creds must be wrong
        
        
        # find our form
        loginform=soup.find('form', attrs={'name': 'aspnetForm'})

        if loginform == None:
            logging.debug('NatWest no security form')
            return 'bank error'

        values = self.parseForm(loginform)

        # define some variables that would only otherwise exist in a try catch block scope
        # the label text split on spaces
        which1arr = ""
        which2arr = ""
        which3arr = ""

        # the chalenges
        firstDigit  = ""
        secondDigit = ""
        thirdDigit  = ""

        #>>>>>>> The first set of Pin fields
        #-------------------- get the questions --------------#

        #<label for="ctl00_mainContent_Tab1_LI6PPEA_edit" id="ctl00_mainContent_Tab1_LI6DDALALabel" class="wizCrl wizardLabelRememberMeWide">Enter the 2nd number</label>
        useNewTab = False
        try:
            which1=soup.find('label', attrs={'for' : 'ctl00_mainContent_LI6PPEA_edit'}).text
        except Exception, e:
            useNewTab = True

        

        try:
            if useNewTab:
                which1=soup.find('label', attrs={'for' : 'ctl00_mainContent_Tab1_LI6PPEA_edit'}).text
                which2=soup.find('label', attrs={'for' : 'ctl00_mainContent_Tab1_LI6PPEB_edit'}).text
                which3=soup.find('label', attrs={'for' : 'ctl00_mainContent_Tab1_LI6PPEC_edit'}).text
            else:
                which1=soup.find('label', attrs={'for' : 'ctl00_mainContent_LI6PPEA_edit'}).text
                which2=soup.find('label', attrs={'for' : 'ctl00_mainContent_LI6PPEB_edit'}).text
                which3=soup.find('label', attrs={'for' : 'ctl00_mainContent_LI6PPEC_edit'}).text
        except Exception, e:
            logging.warn("Pin page error -> " + str(e) )
            return 'bank error'

        # split them on spaces
        try:
            which1arr = which1.split()
            which2arr = which2.split()
            which3arr = which3.split()
        except Exception, e:
            logging.error("Pin parse error -> " + str(e) )
            return 'bank error'

        #--------------look up my pass code from the dynamic questions - if there is a lookup exception it is almost certain that the creds are wrong
        try:
            firstDigit  = self.__lookupdigitPin(which1arr[2])
            secondDigit = self.__lookupdigitPin(which2arr[2])
            thirdDigit  = self.__lookupdigitPin(which3arr[2])
        except Exception, e:
            logging.warn("Passcode lookup error -> " + str(e) )
            return 'credentials incorrect'

        #-------------------- inject my credentials ----------------------
        try:
            if useNewTab:
                values['ctl00$mainContent$Tab1$LI6PPEA_edit'] = firstDigit
                values['ctl00$mainContent$Tab1$LI6PPEB_edit'] = secondDigit
                values['ctl00$mainContent$Tab1$LI6PPEC_edit'] = thirdDigit
            else:
                values['ctl00$mainContent$LI6PPEA_edit'] = firstDigit
                values['ctl00$mainContent$LI6PPEB_edit'] = secondDigit
                values['ctl00$mainContent$LI6PPEC_edit'] = thirdDigit

        except Exception, e:
            logging.error("Form parse error -> " + str(e) )
            return 'bank error'

        #>>>>>>> The second set of Password fields
        #-------------------- get the questions --------------#
        if useNewTab:
            which1=soup.find('label', attrs={'for' : 'ctl00_mainContent_Tab1_LI6PPED_edit'}).text
            which2=soup.find('label', attrs={'for' : 'ctl00_mainContent_Tab1_LI6PPEE_edit'}).text
            which3=soup.find('label', attrs={'for' : 'ctl00_mainContent_Tab1_LI6PPEF_edit'}).text
        else:
            which1=soup.find('label', attrs={'for' : 'ctl00_mainContent_LI6PPED_edit'}).text
            which2=soup.find('label', attrs={'for' : 'ctl00_mainContent_LI6PPEE_edit'}).text
            which3=soup.find('label', attrs={'for' : 'ctl00_mainContent_LI6PPEF_edit'}).text

        # split them on spaces
        try:
            which1arr = which1.split()
            which2arr = which2.split()
            which3arr = which3.split()
        except Exception, e:
            logging.error("Pin parse error -> " + str(e) )
            return 'bank error'

        #--------------look up my pass code from the dynamic questions - if there is a lookup exception it is almost certain that the creds are wrong
        try:
            firstDigit  = self.__lookupdigitPass(which1arr[2])
            secondDigit = self.__lookupdigitPass(which2arr[2])
            thirdDigit  = self.__lookupdigitPass(which3arr[2])
        except Exception, e:
            logging.warn("Passcode lookup error -> " + str(e) )
            return 'credentials incorrect'

        #-------------------- inject my credentials ----------------------
        try:
            if useNewTab:
                values['ctl00$mainContent$Tab1$LI6PPED_edit'] = firstDigit
                values['ctl00$mainContent$Tab1$LI6PPEE_edit'] = secondDigit
                values['ctl00$mainContent$Tab1$LI6PPEF_edit'] = thirdDigit
            else:
                values['ctl00$mainContent$LI6PPED_edit'] = firstDigit
                values['ctl00$mainContent$LI6PPEE_edit'] = secondDigit
                values['ctl00$mainContent$LI6PPEF_edit'] = thirdDigit
        except Exception, e:
            logging.error("Form parse error -> " + str(e) )
            return 'bank error'

        # Here goes - post the form
        action = self.urlBase + '/' + loginform['action']
        
        # build the body content
        data = urllib.urlencode(values)
        self.response = {}
        self.response['url'] = self.ByteToHex(action)
        self.response['data'] = self.ByteToHex(data)
        self.response['method'] = 'POST'
        self.response['step'] = 4

        return scrape_result


    def doStep4(self, allofit, page):
        
        scrape_result = "good"
        
        #-------------------------------- Grab the form values -----------------------------------------------
        soup = BeautifulSoup(page)
        
        # write out the start page
        self.output_page("natwest-pos-accounts.html", page)
        
        scrape_result = 'good'
        logging.info("NatWest message or bad cred check ")

        # if we still have the input then def bad credentials 
        errorDiv=soup.findAll('input', attrs={'name' : 'ctl00$mainContent$LI6PPEA_edit'})

        if len(errorDiv) != 0:
            logging.info("NatWest defiantely bad credentials")
            return 'credentials incorrect' 


        accountBLock=soup.findAll('table', attrs={'class' : 'AccountTable'})
        # got some acount details so all good
        if len(accountBLock) > 0:
            logging.debug("NatWest defiantely got some good accounts")
            return 'good';

        # find any link

        # if we find a link return it 

        # check for the normal continue button and fail all else - with credentials failure
        continueButton = soup.find('input', attrs={'id' : 'ctl00_mainContent_FinishButton_button'})

        if(continueButton == None):
            logging.warning("NatWest cant find finish button credentials incorrect")

            nextButton = soup.find('input', attrs={'id' : 'ctl00_mainContent_NextButton_button'})

            if(nextButton == None):
                logging.warning("NatWest cant find next button either")
                return  'credentials incorrect'


        # now find the form that these buttons belong to
        loginform=soup.find('form', attrs={'name': 'aspnetForm'})

        if loginform == None:
            logging.debug('NatWest no continue form')
            return 'bank error'
        else:
            logging.debug('found a continue form - so clicking it')
        action = self.urlBase + '/' + loginform['action']
    
        # any hidden values etc        
        values = self.parseForm(loginform)
        

        # build the body content
        data = urllib.urlencode(values)
        self.response = {}
        self.response['url'] = self.ByteToHex(action)
        self.response['data'] = self.ByteToHex(data)
        self.response['method'] = 'POST'
        self.response['step'] = 4

        return 'messages'


    def __scrape_accountlist(self, allofit, page):
        scrape_result = 'good'

        logging.info("Good log in - grabbing account list")

        self.accountLinks = []

        # write out the start page
        self.output_page("4_accountlist_page.html", page)

        # get the find the account detail stuff
        return self._parseNatWestLinks(page)



    def _parseNatWestLinks(self, raw):
        soup = BeautifulSoup(raw)
        accountBLock=soup.findAll('a', attrs={'class' : 'accountNameExpand'})

        # got some acount details now so all good
        if len(accountBLock) == 0:
            logging.warning('NatWest no accounts after continue form')
            return 'account problem'

        for ac_link in accountBLock:
            ac_link.string = ac_link.text
            self.accountLinks.append(ac_link)


            # now the accnum list - to get the pair data, cos cant get it from link
            row = ac_link.parent.parent
            try:
                # find the account number span
                acnumSpan = row.find('span', attrs={'class': 'AccountNumber'})
                acnum = acnumSpan.text
                acnum = acnum.replace(' ', '')

                # find the sort code span
                sortSpan = row.find('span', attrs={'class': 'SortCode'})
                sortc = sortSpan.text
                sortc = sortc.replace(' ', '')
                sortc = sortc.replace('-', '')
            except Exception, e:
                logging.exception('NatWest form error - ' + str(e))
                return 'bank error'

            #combine the two - to be our matching number
            num = sortc + "-" + acnum

            actype =  'Cheque'
            # might be a credit card
            if len(acnum) > 14:
                actype =  'Credit'

            # now get balances...
            balance = 0
            baltr = ac_link.parent.parent
            baltds = baltr.findAll('td')
            if len(baltds) > 2:
                baltext = self.tidy_text(baltds[3].text)
                balance = self.normalise_ammount(baltext)

            # and add it to our account list
            acpair = {'name': ac_link.text, 'num': num, 'type': actype, 'bal': balance}

            self.myAccounts.append(acpair)

        # now find the buttons wiht the actual links
        rightButtons=soup.findAll('a', attrs={'class' : 'link-button-right'})

        # any buttons?
        if len(rightButtons) == 0:
            logging.error('NatWest no accountbuttons - odd - html changed??')
            return 'bank error'

        # natWest is not dynamic -so this static list is fine (unlike Smile)
        ac = 0
        for a in rightButtons:
            # filter out the account detail buttons matching just the statement buttons
            # Bloody hope this regex finds shit in the right order
            if re.search(".iew..ull..tatement", a.text):
                link = self.composeLink(a['href'][:])

                self.accountLinks[ac]['href'] = link
                ac = ac + 1

        # because potential for mismatch - just check we have them all added up correctly
        if ac != len(accountBLock):
            logging.error("Account and account link mismatch")

        return 'good'


    def doStep7(self, page):
        
        #-------------------------------- Grab the form values -----------------------------------------------
        soup = BeautifulSoup(page)
        
        self.output_page("natwest-acclink.html", page)
    
        loginform=soup.find('form', attrs={'name': 'aspnetForm'})

        if loginform == None:
            logging.debug('NatWest no view account form')
            return 'bank error'


        action = self.urlBase + '/' + loginform['action']
        
        values = self.parseForm(loginform)
        
        # fill in our selection - 1 month
        values['ctl00$mainContent$SS2SPDDA'] = 'M1'

        # default button - needed
        values['ctl00$mainContent$NextButton_button'] = 'View Transactions'

        # build the body content
        data = urllib.urlencode(values)
        self.response = {}
        self.response['url'] = self.ByteToHex(action)
        self.response['data'] = self.ByteToHex(data)
        self.response['method'] = 'POST'
        self.response['step'] = 20
        

        return 'good'

    def composeLink(self, acLink):
        action = acLink
        try:
            logging.debug("checking link - " + acLink)
            urls = urlparse(acLink);

            if urls.netloc == '':
                logging.debug('ading base to link')
                if acLink[0] == '/':
                    action = self.urlBase + acLink
                else:
                    action = self.urlBase + '/' + acLink

                logging.debug(action)
            # if it parses properly good else    
        
        except Exception, e:
            logging.debug('composing link cause of  - ' + str(e))
            if acLink[0] == '/':
                action = self.urlBase + acLink
            else:
                action = self.urlBase + '/' + acLink

        return action
        
    
    
    # <a id="ctl11cc9ddb_mainContent_Actionlink1Anchor" class="link-button-right" href="https://www.nwolb.com/CardStatementDetail.aspx?id=5B3195B4D0BD4EC2C43A20A238349E36FE0071AE">View Statements</a>

    def doStep12(self, page):
       
        #-------------------------------- Grab the form values -----------------------------------------------
        soup = BeautifulSoup(page)
        
        self.output_page("natwest-xactlist-cc-poss.html", page)
    
        rightButtons=soup.findAll('a', attrs={'class' : 'link-button-right'})

        # any buttons?
        if len(rightButtons) == 0:
            logging.error('NatWest no cc accountbuttons')
            return 'bank error'

        # natWest is not dynamic -so this static list is fine (unlike Smile)
        acLink = None
        for a in rightButtons:
            # filter out the account detail buttons matching just the statement buttons
            # Bloody hope this regex finds shit in the right order
            if re.search(".ard.tatement.etail", a['href']):
                acLink = a['href'][:]
                



        if acLink == None:
            logging.debug('NatWest no cc detail link')
            return 'bank error'

        

        # action = self.urlBase + '/' + loginform['action']

        action = acLink
        try:
            logging.debug("checking link - " + acLink)
            urls = urlparse(acLink);

            # if it parses properly good else    
            
        
        except Exception, e:
            logging.error('NatWest cc link error - ' + str(e))
            action = self.urlBase + '/' + acLink
            

        
        logging.debug("using this bank url - " + action)
        
        self.response = {}
        self.response['url'] = self.ByteToHex(action)
        self.response['data'] = ""
        self.response['method'] = 'GET'
        self.response['step'] = 20
        

        return 'good'

    # look for an all link
    def doAllLink(self, page):
       
        soup = BeautifulSoup(page)
        
        self.output_page("natwest-xactlist-all-look.html", page)

        #<a href="/StatementsFixedPeriod.aspx?id=B7879D8CABBF283B38AE447E07A4EA5D8DA9A859&amp;persist=%2fwEPBQ1BY2NvdW50TnVtYmVyBQg4ODU3MjIxOA%3d%3d%7c%2fwEPBQhGcm9tRGF0ZQUTMTgvMDUvMjAxMSAwMDowMDowMA%3d%3d%7c%2fwEPBQhTb3J0Q29kZQUGNjAxNzIx%7c%2fwEPBQZUb0RhdGUFEzE4LzA3LzIwMTEgMDA6MDA6MDA%3d%7c%2fwEWBh4JU1MyQUNDRERBDwUUU0lOSEEgTS9TVFUgODg1NzIyMTgFKEI3ODc5RDhDQUJCRjI4M0IzOEFFNDQ3RTA3QTRFQTVEOERBOUE4NTkeCFNTMlNQRERBDxBkZBYBAgNnHgZTUzJXTEEPAgFo&amp;showall=1" title="Show all items on a single page">All</a>

        logging.debug('NatWest checking for all links')

        # find any all link
        links=soup.findAll('a')

        link = None
        for a in links:
            # detect our link
            try:
                if re.search(".tatements.ixed.eriod", a['href']):
                    logging.debug("natwest - got a statement  link")
                    if re.search(".ll", a.text):                        # the one that says all
                        link = self.composeLink(a['href'][:])
                        logging.debug("natwest - got an All statement link")
                        break                                                   # only need the first one so break the for loop
            except Exception, e:
                logging.debug('NatWest a link error missing href - ' + str(e))


        # any 'all' link
        if link == None:
            logging.debug('NatWest no All link')
            return 'allxacts'                           # special resonse for the normal case that there is no 'All' link


        
        logging.debug("using this All link  url - " + link)
        
        self.response = {}
        self.response['url'] = self.ByteToHex(link)
        self.response['data'] = ""
        self.response['method'] = 'GET'
        self.response['step'] = 30
        

        return 'good'


    def prepParse(self, allofit, facade, token):
        self.facade = facade
        self.token = token
    
        scrape_result = 'good'

        bankurl = self.HexToByte(allofit['bankurl'])
        urls = urlparse(bankurl);
        self.urlBase = "https://" + urls.netloc
        logging.info("Base URL = " + self.urlBase)


        # lower case them incase any auto casing in the app - NatWest is case insensitive.
        for creds in self.filledCreds:
            self.filledCreds[creds] = self.filledCreds[creds].lower();

        # now try utf8 encoding ready for urlencoding
        for creds in self.filledCreds:
            try: 
                self.filledCreds[creds] = self.filledCreds[creds].encode('utf8');
            except Exception, e:
                logging.warning('NatWest utf8 encoding error - ' + str(e))



    def gettheAccounts(self, facade, accountList, token, step, allofit, page):    
        
        self.response = {}
        
        if step == 1:
            scrape_result = self.doStep1(allofit, page)
    
        elif step == 2:
            scrape_result = self.doStep2(allofit, page)
        
        elif step == 3:
            scrape_result = self.doStep3(allofit, page)
        
        elif step == 4 or step == 5 or step == 6:
            scrape_result = self.doStep4(allofit, page)
            
            # make sure we move on one - if step 6 then later we set END
            newstep = step + 1
            if newstep > 6:
                newstep = 6
            self.response['step'] = newstep

        # after step 4 any good response means we have a list of accounts
            if  scrape_result == "good":

                # something 
                    
                self.myAccounts = []

                self.__scrape_accountlist(allofit, page)
                
                # if it is a sync then the other steps will update the url
                self.response['url'] = ""
                self.response['data'] = ""
                self.response['method'] = 'END'
                
                scrape_result = "got list"
        
        # messages is a flag so the good result above does not get fired - which wuld remove our urls
        # we got some messages if this is the second time round - i.e. step 5 then END with errors 
        if scrape_result == "messages":
            # if on step 5 and not got a list then were fucked
            if step == 6:
                self.response['method'] = 'END'
                scrape_result = "bank error"
            else:
                scrape_result = "good"

                
        return scrape_result
    
    

    def getacclist(self, facade, accountList, token, step, allofit):                # accountList not used in getacclist
        logging.info(" --> STEP-" + str(step))
        Scraper.getacclist(self, facade, accountList, token)
        self.wipe_pages()

        self.prepParse(allofit, facade, token)

        page = self.HexToByte( allofit['body'])

        scrape_result = self.gettheAccounts(facade, accountList, token, step, allofit, page)

        if scrape_result != 'good' and scrape_result != "got list":
            logging.warning("Got result - " + scrape_result)
            self.flush_pages()

        return scrape_result


    
    def getxactlist(self, facade, accountList, token, step, allofit):    
        logging.info(" --> STEP-" + str(step))
        Scraper.doscrape(self, facade, accountList, token)
        self.wipe_pages()

        scrape_result = "good"

        self.response = {}


        self.prepParse(allofit, facade, token)

        page = self.HexToByte( allofit['body'])

        # if its early steps login and get the accounts 
        if step < 7:
            scrape_result = self.gettheAccounts(facade, accountList, token, step, allofit, page)

        if step == 4 or step ==5 or step == 6:
            # if that went well and we now have a list 
            if scrape_result == "got list":
                # test that we have some account links
                acCount = 0
                accounts = []
                for ac in self.accountLinks:
                    acName = self.accountLinks[acCount].string
                    acLink = self.accountLinks[acCount]['href']
                    # simple lookup here as login sets up mayAccounts in NatWest
                    acpair = self.myAccounts[acCount]

                    # tha unique name defining this account to link on (eg accont number)
                    acID = None

                    # if we did detect an account number
                    if acpair != None:
                        logging.debug('got a pair')
                        acID = acpair['num']   # then use this

                    # now see if we hav this id in our list of accounts to get the correct path to add the xactions to
                    theAccountPath = []
                    if acID in accountList:
                        theAccountPath = accountList[acID]

                        account = {}
                        account['accountid'] = acID
                        account['href'] = acLink
                        account['path'] = theAccountPath
                        account['synched'] = False
                        account['type'] = acpair['type']
                        account['balance'] = acpair['bal']

                        accounts.append(account)
                    
                    else:
                        logging.warn("N-B - account not in users list " + acName + ' - ' + acID)

                    logging.info('-------------->' + str(acID))
                    logging.info('-------------->' + str(theAccountPath))
                    logging.info('-------------->' + str(acLink))
                    logging.info('-------------->' + str(acName))

                    acCount = acCount + 1

                accounts[0]['synched'] = True
                self.response['accountlist'] = accounts
                
                # TODO - choose the right url - the first on the list
                self.response['url'] = self.ByteToHex(accounts[0]['href'])
                self.response['data'] = ""
                self.response['method'] = 'GET'

                #  7 or twelve cc or normal
                if accounts[0]['type'] == 'Credit':
                    self.response['step'] = 12
                else:
                    self.response['step'] = 7

                self.response['accountid'] = accounts[0]['accountid']
                self.response['accountpath'] = accounts[0]['path']
                
                scrape_result = "account list"

            elif scrape_result != "good":
                self.flush_pages()
                

            return scrape_result
        
        if step > 6:
            accounts = allofit['accountlist']
            
            # detals of the currently synching account
            # account number - id etc
            acName = allofit['accountid']
            theAccountPath = allofit['accountpath'][:]
            
            bankurl = self.HexToByte(allofit['bankurl'])

            logging.debug("PROCESSING - -- -> " + bankurl)
            logging.debug(" acName - " + acName + " acPath - " + str(theAccountPath))

            actype = None
            acbal = 0

            

        # first recieved next link towards accountlist for normal accounts
        if step == 7:

            logging.info('STEP 7')
            
            scrape_result = self.doStep7(page)

        

        # first recieved next link towards accountlist for cc accounts
        if step == 12:
            logging.info('STEP 12')
            
            scrape_result =self.doStep12(page)


        # actually got a transaction list page - so check for an all link
        if step == 20:
            # now find this account to get the extra bits of info
            
            result = self.doAllLink(page)
            
            # if we allready have all xacts as per ususal then trigger step 30 with this page
            if result == "allxacts":
                step = 30
            else:
                logging.debug("need to get the page of all accounts")


        # copy all the response stuff
        if step > 5 and step < 30:
            self.response['accountid'] = acName
            self.response['accountpath'] = theAccountPath
            self.response['accountlist'] = accounts


            scrape_result = "account list"

        
        # actually got a transaction list page
        if step == 30:

            # now find this account to get the extra bits of info
            for ac in accounts:
                if ac['accountid'] == acName:
                    acType = ac['type']
                    balance = ac['balance']

            if acType == 'Credit':
                result = self._processCCAccount(page, theAccountPath, balance)
            else:
                result = self._processNormAccount(page, theAccountPath, balance)
            


        # good or bad move onto next account - good plan??
        # if trying to grab the account detail pages and they return bad - move on as well
        # remember all the pre acc list return scrape_result = "account list" on success
        if step == 30 or (step > 5 and scrape_result != 'account list'):
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
            
            
            self.response['data'] = ""
            
            self.response['accountid'] = ""
            self.response['accountpath'] = ""
            
            if url == "":
                self.response['url'] = ""
                self.response['method'] = 'END'
            else:
                self.response['url'] = self.ByteToHex(url)
                accounts[acind]['synched'] = True
                self.response['method'] = 'GET'
                self.response['accountid'] = accounts[acind]['accountid']
                self.response['accountpath'] = accounts[acind]['path']
            

            #  6 or twelve cc or normal
            if accounts[acind]['type'] == 'Credit':
                self.response['step'] = 12
            else:
                self.response['step'] = 7
            
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



    def __lookupdigitPin(self, word):
        passcode = self.filledCreds['02']   #Four Digit PIN

        # strip off nd, st, rd, th
        lupword = word[:-2]

        logging.debug("Looking pin for - " + lupword)

        return passcode[int(lupword) - 1 ]


    def __lookupdigitPass(self, word):
        passcode = self.filledCreds['03']   #Password

        lupword = word[:-2]

        logging.debug("Looking Pass for - " + lupword)

        return passcode[int(lupword) - 1 ]


    def _processCCAccount(self, raw, account_path, balance):
        soup = BeautifulSoup(raw)

        logging.debug('CC ac path - ' + str(account_path) + ' - end' )

        try:
            if account_path != "":
                # delete existing current xactions
                logging.debug('Processing :) ' )

                builder = StatementBuilder(self.facade, account_path, self.token)
                self.statementlist.append(builder)
                self.statementbuilder = self.statementlist[self.current_statement]

                # we know this is not a credit card
                isCCard = True

                # get a fixed balance somewhere??
                # passed in for natwest

                # set up our statement
                self.statementbuilder.make_recent_dif_statement('NatWest-recent', 'Scraper', None)

                # now set the final balance
                logging.debug("Balance - - - - - - - > " + str(balance))
                self.statementbuilder.set_current_balance(balance)

                # now find all the recent transactions
                x_table = soup.find('table', attrs={'class' : 'ItemTable'})

                if x_table != None:
                    x_body = x_table.find('tbody')
                    inputs = x_body.findAll('tr')

                    # build the post values up
                    for rows in inputs:
                        atts = {}

                        vals = rows.findAll('td')
                        if vals:
                            datebit = ''
                            for i, val in enumerate(vals):
                                data = self.tidy_text(val.text)
                                if i == 0:
                                    dp = DateParser()
                                    try:
                                        atts['date'] = dp.ymd_from_date(dp.date_from_small(data))
                                    except:
                                        atts['date'] == ''

                                if i == 1:
                                    datebit = data[:-5]

                                if i == 2:
                                    if data != 'SALE':           # only keep extra xact date for Sales
                                        datebit = ''

                                if i == 3:
                                    if data != "":
                                        atts['display'] =  " ".join(data.split()).encode('utf8')
                                        atts['extradisplay'] = datebit.encode('utf8')

                                if i > 3:   # the numbers

                                    if data != "" and data != '-':
                                        amount = self.normalise_ammount(data)

                                        if i == 4:
                                            atts['amount'] = amount
                                            atts['type'] = 'Credit'

                                        if i == 5:
                                            atts['amount'] = amount
                                            atts['type'] = 'Debit'

                                    if i == 5:
                                        self.statementbuilder.make_xact(atts)


            self.statementbuilder.put_statement()
            self.current_statement = self.current_statement + 1

        except Exception, e:
            logging.exception('NatWest parsing error - ' + str(e))

        return None


    def _processNormAccount(self, raw, account_path, balance):

        soup = BeautifulSoup(raw)

        logging.debug('Norm ac path - ' + str(account_path) + ' - end' )

        try:
            if account_path != "":
                # delete existing current xactions
                logging.debug('Processing :) norm ' )

                builder = StatementBuilder(self.facade, account_path, self.token)
                self.statementlist.append(builder)
                self.statementbuilder = self.statementlist[self.current_statement]

                # we know this is not a credit card
                isCCard = False

                # get a fixed balance somewhere??
                # balance passed in for natwest

                # set up our statement
                self.statementbuilder.make_recent_dif_statement('NatWest-recent', 'Scraper', None)

                

                # now set the final balance
                logging.debug("Balance - - - - - - - > " + str(balance))
                self.statementbuilder.set_current_balance(balance)


                # now find all the recent transactions
                x_table = soup.find('table', attrs={'class' : 'ItemTable'})

                if x_table == None:
                    # could easily be no transactions
                    logging.debug(" No xtable ======>")


                if x_table != None:
                    x_body = x_table.find('tbody')
                    inputs = x_body.findAll('tr')

                    # build the post values up
                    for rows in inputs:
                        atts = {}

                        vals = rows.findAll('td')
                        if vals:
                            cash = ''
                            for i, val in enumerate(vals):
                                data = self.tidy_text(val.text)
                                if i == 0:
                                    
                                    dp = DateParser()
                                    try:
                                        atts['date'] = dp.ymd_from_date(dp.date_from_small(data))
                                    except:
                                        atts['date'] == ''
                                if i == 1:
                                    if data == 'ATM':
                                        cash = 'CASH - '

                                if i == 2:
                                    if data != "":
                                        extra = ""
                                        datebit = ""
                                        parts = data.split(',')
                                        if len(parts) > 1:
                                            # match natwest dates - a.la. 8062 14APR11
                                            if re.match('\d{4}\s\d\d[A-Z]{3}\d\d', parts[0]) != None:
                                                datebit = parts[0][0:4] + ' ' + parts[0][5:7] + ' ' + parts[0][7:10]
                                                # remember pretty_display strips out any words containing a sequence of 3 or more numbers

                                                parts = parts[1:]

                                        if len(parts) > 1:
                                            extra = parts[-1]
                                            parts = parts[0:-1]

                                        data = ' '.join(parts)

                                        disp =  (cash + data).strip()

                                        atts['display'] = " ".join(disp.split())

                                        atts['extradisplay'] = " ".join( (extra + " " + datebit).split())

                                if i > 2:   # the numbers

                                    if data != "" and data != '-':
                                        
                                        amount = self.normalise_ammount(data)

                                        if i == 3:
                                            atts['amount'] = amount
                                            atts['type'] = 'Credit'

                                        if i == 4:
                                            atts['amount'] = amount
                                            atts['type'] = 'Debit'

                                    if i == 5:
                                        self.statementbuilder.make_xact(atts)

            self.statementbuilder.put_statement()
            self.current_statement = self.current_statement + 1

        except Exception, e:
            logging.exception('NatWest parsing error - ' + str(e))

        return None


