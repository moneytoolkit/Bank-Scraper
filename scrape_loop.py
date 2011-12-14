#!/usr/bin/env python
# 

import logging
import codecs
import sys
import os
import re

from scraper_controller import ScraperController
from scrapers.all_crapers import AllScrapers


import mechanize


# a loop to seperate the connection from the scrping logic
# although this loop is in python you could use any http client code
class ScrapeHTTPLoop:

    def ByteToHex(self,  byteStr ):
        return ''.join( [ "%02X" % ord( x ) for x in byteStr ] )

    def HexToByte(self, hexStr ):
     
        bytes = []
    
        for i in range(0, len(hexStr), 2):
            bytes.append( chr( int (hexStr[i:i+2], 16 ) ) )
    
        return ''.join( bytes ).decode("utf-8")


    def output_page(self, name, page):

        root_path = './pagedump/' + name;                   # add any path in here
        file = codecs.open(root_path,"wb", "utf-8-sig");
        
        file.write(page)
        file.close()


    def loop(self, message):

        # get the bank id for this sesh
        bankId = message[0]['bankId']
        # and find its start URL
        all_scrapers = AllScrapers()
        self.startUrl = all_scrapers.getStartUrl(bankId)

        self.b = mechanize.Browser(factory=mechanize.RobustFactory())
        self.b.set_handle_robots(None)

        self.b.set_debug_redirects(True)
        # Log HTTP response bodies (ie. the HTML, most of the time).
        self.b.set_debug_responses(True)
        # Print HTTP headers.
        self.b.set_debug_http(True)

        # Don't handle Refresh redirections
        self.b.set_handle_refresh(False)
        
        logging.info("Start URL = " + self.startUrl)


        controller = ScraperController()

        bank_url = self.startUrl
        next_step = 1
        method = 'GET'
        post = ''

        post_data = None

        do_loop = True

        while do_loop:

            
            # open the first page
            self.b.open(bank_url, post_data)

            raw = self.b.response().get_data()

                    # write out the start page
            self.output_page(str(next_step) + "_page.html", raw.decode('utf-8'))


            request = {}

            request['body'] = 'tbd'        
            request['status'] = 200
            request['bankurl'] = self.ByteToHex(self.startUrl)
            request['headers'] = []
            request['step'] = next_step
            request['credentials'] = message

            logging.debug(str(request));

            request['body'] = self.ByteToHex(raw) 

            # call the controller with this page
            response = controller.get_accounts(request)

            logging.debug('>>> -------------------------')
            logging.debug('>>> -------------------------------------------->')
            logging.debug('>>> -------------------------')

            # decypher what went on in the parsing
            status = response['message']

              
            if status == 'good':
              next_request = response['request']

              method = next_request['method']
              bank_url = self.HexToByte(next_request['url'])
              next_step = next_request['step']
              post = self.HexToByte(next_request['data'])


              logging.debug("METHOD: " + method)
              logging.debug("URL: " + bank_url)
              logging.debug("STEP:" + str(next_step))
              logging.debug("DATA: " + post)

              post_data = None
              if method == 'POST':
                post_data = post



            if method == 'END':
              do_loop = False
            if status != 'good':
              do_loop = False


        return response


# loop makes the first bank call

# our loop sends this to the scraper...

# {
#   "body": "0a0a0a0a........6c3e0a", 
#   "status": 200, 
#   "bankurl": "", 
#   "headers": [
#     {
#       "name": "5365742d436f6f6b6965", 
#       "value": "6664613d72323139383132313139313b20706174683d2f3b20657870697265733d"
#     }, 
#     {
#       "name": "44617465", 
#       "value": "5361742c203233204f637420323031302031313a33303a323720474d54"
#     } 
#   ], 
#   "step": 1, 
#   "credentials": [
#     {
#       "credentials": {
#         "03": "danmux", 
#         "06": "rdsdsdson", 
#         "04": "blblblbl"
#       }, 
#       "name": "not needed", 
#       "bankId": "www.firstdirect.com"
#     }
#   ]
# }

# # scraper sends back 


# fc.response.out.write('{"message": "' + scrape_result + '", "bankid": "' + bank['bankId'] + '", "request": ' + respJson + ' }')


# {
#   "message": "good", 
#   "bankid": "www.natwest.com", 
#   "request": {
    
#     "url": "68747470733A2F2F7777772E6E776F6C622E636F6D2F4361726453746174656D656E74732E617370783F69643D32463146463943334443354231374432423043463739363334394535443830364138323831433442", 
#     "step": 5, 
#     "data": "", 
#     "method": "GET", 
    
#   } 
# }






# {
#   "message": "good", 
#   "bankid": "www.natwest.com", 
#   "request": {
    
#     "accountpath": [
#       "Person", 
#       "danm", 
#       "Account", 
#       "a3"
#     ],
#     "url": "68747470733A2F2F7777772E6E776F6C622E636F6D2F4361726453746174656D656E74732E617370783F69643D32463146463943334443354231374432423043463739363334394535443830364138323831433442", 
#     "step": 5, 
#     "data": "", 
#     "method": "GET", 
#     "accountid": "-5454605883266740",


#     "accountlist": [
#       {
#         "path": [
#           "Person", 
#           "danm", 
#           "Account", 
#           "a3"
#         ], 
#         "accountid": "-5454605883266740", 
#         "href": "https://www.nwolb.com/CardStatements.aspx?id=2F1FF9C3DC5B17D2B0CF796349E5D806A8281C4B", 
#         "synched": true
#       }, 
#       {
#         "path": [
#           "Person", 
#           "danm", 
#           "Account", 
#           "a3"
#         ], 
#         "accountid": "-5454605883266740", 
#         "href": "https://www.nwolb.com/CardStatements.aspx?id=2F1FF9C3DC5B17D2B0CF796349E5D806A8281C4B", 
#         "synched": false
#       }, 
#       {
#         "path": [
#           "Person", 
#           "danm", 
#           "Account", 
#           "a3"
#         ], 
#         "accountid": "-5454605883266740", 
#         "href": "https://www.nwolb.com/CardStatements.aspx?id=2F1FF9C3DC5B17D2B0CF796349E5D806A8281C4B", 
#         "synched": false
#       }, 
#       {
#         "path": [
#           "Person", 
#           "danm", 
#           "Account", 
#           "a3"
#         ], 
#         "accountid": "-5454605883266740", 
#         "href": "https://www.nwolb.com/CardStatements.aspx?id=2F1FF9C3DC5B17D2B0CF796349E5D806A8281C4B", 
#         "synched": false
#       }
#     ] 
    
#   } 
# }

