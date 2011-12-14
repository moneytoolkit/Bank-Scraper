#!/usr/bin/env python

import sys
import os
import re
import logging
import simplejson

# our list of suppoted scrapers
from scrapers.all_scrapers import AllScrapers


# little facade object to pass a usr round the place - if we have multiple users
class Facade:

    def __init__(self, user):
        self.user = user


class ScraperController:
'''recieves scraper body requests calls the appropriate scraper
   takes the scraper response and wraps it in json and passes it back
'''

    self.persister = None

    def addPersistance(self, persister):
        self.persister = persister

   
    def getScraper(self, bankId, credentials):   #TODO - check do we need to know about proxy_grab

        scraperFactory = AllScrapers()
        return scraperFactory.getScraper(bankId, credentials)


   
    def get_accounts(self, allofit):
        '''here is the structure of an example an allofit  object pased in to get_accounts
        {
          "body": "0a0a0a0a........6c3e0a", 
          "status": 200, 
          "bankurl": "", 
          "headers": [
            {
              "name": "5365742d436f6f6b6965", 
              "value": "6664613d72323139383132313139313b20706174683d2f3b20657870697265733d"
            }, 
            {
              "name": "44617465", 
              "value": "5361742c203233204f637420323031302031313a33303a323720474d54"
            } 
          ], 
          "step": 1, 
          "credentials": [
            {
              "credentials": {
                "03": "danmux", 
                "06": "rdsdsdson", 
                "04": "blblblbl"
              }, 
              "name": "not needed", 
              "bankId": "www.firstdirect.com"
            }
          ]
        }'''

        facade = Facade('user');
        
        # get important bits from the message
        step = allofit['step']
        bank = allofit['credentials'][0]              # SEE - only one ever!
        bankId = bank['bankId']
        
        logging.info("found:    - " + bankId)
        
        #look up our scraper
        scc = self.getScraper(bankId, bank['credentials'])
        
        matching_accounts = {}                                                      # TODO refactor getacclist as not used in getacclist anymore
            
        if scc:
            
            scrape_result = scc.getacclist(facade, matching_accounts, 'unusedtoken', step, allofit)
            
            respJson = simplejson.dumps(scc.response, indent = 2)
            
            # if we have not got got a list of accounts yet then just return our wrappers and the scraper response
            if "got list" != scrape_result:
                response = {}
                response['message'] = scrape_result
                response['bankid'] = bank['bankId']
                response['request'] = respJson
            else:
                
                accounts = scc.myAccounts
                
                bank_display = scc.getDisplay()
                
                found_accs = []
                
                got_some_acc = False
                
                for accpair in accounts:
                    
                    got_some_acc = True
                    
                    acc = accpair['name']
                    ac_num = accpair['num']
                    ac_type = accpair['type']
                    
                    logging.debug("found bank ==========> " + acc + "    - num - " + ac_num)
                    
                    # a status flag - if all local file or API handling goes well
                    new = True

                    # if we have a permanent list of accounts then check our new found list to see if we can find an existing account in the users account list
                    if self.persister != None:


                    
                    
                    #    logging.debug("checking existing accounts")
                    #    for account in user.accounts:
                    #     if we dont find  this account then ad it to our list by setting good = True
                    
                    
                    # got a new account so set up default attributes for this account to store in our file of accounts or spreadsheet
                    if new == True:

                        attributes= {}
                        attributes['display'] = acc
                        attributes['accountname'] = ac_num
                        attributes['bankname'] = bankId
                        attributes['type'] = ac_type
                        attributes['synchbal'] = 0
                        attributes['synched'] = False
                        attributes['balance'] = 0

                        
                        
                        #TODO - if new accounts update our accounts with a unique key
                        attributes['id'] = 'a1'
                        attributes['keyname'] = 'a1'
                        
                        
                        # TODO review ths usage
                        attributes['parser'] = accdesc['parser']
                        attributes['synchbalwhich'] = "Positive"
                        attributes['which'] = "Positive"
                        

                        
                        
                        logging.debug("adding account to the list")
                        found_accs.append(attributes)
                    
                if len(found_accs) == 0 and got_some_acc:
                    logging.debug("all accounts already added")
                
                response = {}
                response['message'] = "good"
                response['bankid'] = bank['bankId']
                response['request'] = respJson
                response['accounts'] = found_accs
            
        else:    
            response = {}
            response['message'] = "bank not supported"
            response['bankid'] = bank['bankId']
            

        return response





# # loop makes the first bank call

# # our loop sends this to the scraper...

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

