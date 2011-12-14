#!/usr/bin/env python
# coding: utf-8

import logging                             
import codecs
from utils.utilfuncs import unescape


# important instance variables:

#    myAccounts - the list of accounts

class Scraper():
    current_statement = 0
    statementlist = []
    pagelist = {}

    filledCredentials = {}
    statementbuilder = None

    realUrlChunk = ""
    urlBase = ""

    questionlist = [{'id': '01', 'display':'User ID', 'x':'0', 'l': '12'}]



    def __init__(self, passedCreds):
        self.credentials = {}
        self.startUrl = None
        
        for cred in self.questionlist:
            self.credentials[cred['display']] = '';            
        
        self.filledCreds = passedCreds
    

    def ByteToHex(self,  byteStr ):
        """
        Convert a byte string to it's hex string representation e.g. for output.
        """
        
        return ''.join( [ "%02X" % ord( x ) for x in byteStr ] )

        
    def HexToByte(self, hexStr ):
        """
        Convert a string hex byte values into a byte string. The Hex Byte values may
        or may not be space separated.
        """
        bytes = []
    
        for i in range(0, len(hexStr), 2):
            bytes.append( chr( int (hexStr[i:i+2], 16 ) ) )
    
        return ''.join( bytes ).decode("utf-8")



    def getBuilder(self):
        return 'fixed'


    def unFoundAccount(self, htmlkey):
        msg = "Couldnt find account ----> " + htmlkey
        logging.warn(msg)



    def getSid(self):
        return "default";


    def doscrape(self, facade, accountList, token):
        scrape_result = 'good'
        self.facade = facade
        self.token = token
        self.myAccounts = []
        self.statementlist = []


    def getacclist(self, facade, accountList, token):
        scrape_result = 'good'
        self.facade = facade
        self.token = token
        self.myAccounts = []



    def output_page(self, name, page):
        self.pagelist[name] = page
        # now call the _pretty_printer
        self._pp(name, page)
    
        
        
    def write_page(self, person, name, page):

        logging.debug('>'*50)
        logging.debug(name)
        
        root_path = './pagedump/' + name;
        file = codecs.open(root_path,"wb", "utf-8-sig");
        file.write(page)
        file.close()


    def flush_pages(self):
        for page in self.pagelist:
            self.write_page(self.facade.user, self.facade.user + "_" + self.getSid() + "_" + page, self.pagelist[page])
            
    def wipe_pages(self):
        self.pagelist = {}


    def getQuestions(self):
        return self.questionlist
    
    def getAccounts(self):
        return self.account_names
    
    def getDisplay(self):
        return self.display
    

    def getCreds(self):
        return self.credentials

    
    def normalise_ammount(self, bal, cc = False):
        data = self.tidy_text(bal)
        # remove pound signs
        data = data.replace(u'£','');
        data = data.replace(u'?','');

        # remove commas
        data = data.replace(',','')

        negative = False

        # for credit cards invert things when a CR is found
        if cc and data.find('C') >= 0:
            negative = True

        # check for a 'D'
        if data.find('D') >= 0:
            negative = True

        # check for a '-'
        if data.find('-') >= 0:
            negative = True

        # check for a '(xx.xx)'
        if (data.find('(') >= 0) and (data.find(')') >= 0):
            negative = True

        # strip them all
        data = data.replace('-','')
        data = data.replace('(','')
        data = data.replace(')','')
        data = data.replace('D','')
        data = data.replace('B','')
        data = data.replace('C','')
        data = data.replace('R','')

        # other representatins of zero
        if data == 'NIL':
            data = '0'

        # now finally get the ammount
        lastbal = int( float(data) * 100 )

        if negative:
            lastbal = 0 - lastbal

        return lastbal


    def tidy_text(self, text):
        data = unescape(text)
        data = unicode(data)

        # remove html pound signs
        data = data.replace('&#163;', u'£')
        data = data.replace('&pound', u'£');

        # remove html spaces
        data = data.replace('&#160;', ' ')
        data = data.replace('&nbsp;', ' ')

        # remove puntuation
        data = data.replace('"','')

        # remove duplicate spaces
        data = data.replace('       ', ' ')
        data = data.replace('     ', ' ')
        data = data.replace('   ', ' ')
        data = data.replace('  ', ' ')
        data = data.replace('  ', ' ')

        # remove other html
        data = data.replace('<br>','')
        data = data.replace('<br/>','')
        data = data.replace('</br>','')

        # then drop leading and trailing whitespace
        data = data.strip()

        return data


    def parseForm(self, loginform):
        inputs = loginform.findAll('input')
            
        # build the post values up
        values = {}
        for tag in inputs:
            if tag['type'] <> 'image' and tag['type'] <> 'submit':
                value = ''
                
                try:

                    value = tag['value']
                except:
                    pass
                
                
                #logging.debug("V ==> " + tag['name'] + " : " + value)
                values[tag['name']] = value

        # any select values
        inputs = loginform.findAll('select')
            
        for tag in inputs:
            value = ''

            options = tag.findAll('option')

            for option in options:                
                if  option.get('selected'):
                    if option['selected'].lower() == 'selected':
                        value = option['value'][:]
                
            
        
            
            # logging.debug("V ==> " + tag['name'] + " : " + value)
        
            values[tag['name']] = value

        return values
        
    
    # pretty printer to be overriden in test class - called whenever a page is output
    def _pp(self, name, page):
        pass