import datetime
import logging

from utils.dateparser import DateParser


class MiniParams:
  def __init__(self):
    self.noDecorate = True
    self.month = 0
    self.year = 0
    self.day = 0

class TaskQueue:

  def add(self, url, payload, eta):
    pass


class Balance:
  pass


class Xact:
  pass

class Account:
  keyname = ''
  synchbal = 0
  synched = True
  synchbal = 0
  synchdate = None
  synched = True
  _scur_count = 1

  def put(self):
    pass

  def update_bal_direct(self, xact):
    pass

  def set_fixed_bal(self, old_synchbal, credit, debit):
    pass

class Statement:
  hash = "Dont-Match"
  mindate=None
  maxdate=None
  credits=0
  debits=0
  xactcount=0
  isnew=False
  xact_set = []

  def before_put_callback(self, dec):
    pass

  def put(self):
    pass

class StatementBuilder():
    __last_xact = None
    __last_balance = 0
    __canfix = False        #only statemetns and thing with explcit balances

    __type = ''
    __filename = ''
    __body = ''
    fixedStatement = False

    __account = None

    __xactList = []

    def __init__(self, facade, pathlist, token):
        self.token = token
        self.facade = facade
        self.__pathlist = pathlist[:]
        self.xactcount = 0
        self.__xactList = []
        self.__prety_xactList = []
        if len(pathlist) < 3:
          logging.error(">>>>>>>>>>>>>>>>>>>>>> TEST DATA TEST DATA pathlist not set probably not passes a good user in for the test!! <<<<<<<<<<<<<<<<<<<<<<")
          pathlist = ['Person','TEST','Account', 'TEST']
        self.__account_key = pathlist[-1]
        logging.info("path - " +  str(self.__pathlist))

    # does a partial update on the account - only called from scrapers
    def set_current_balance(self, curBalance):
        if self.fixedStatement:

            dp = DateParser()

            self.__old_synchbal = self.__account.synchbal
            self.__old_synched = self.__account.synched

            self.__account.synchbal = curBalance
            self.__account.synchdate = dp.todate()
            self.__account.synched = True


    # for normal statement create it
    # for a sync statement find or create one
    def __make_new_statement(self):
        self.__xactList = []

        logging.info("path - " +  str(self.__pathlist))

        statement_path = self.__pathlist[:]
        statement_path.append('Statement')

        if self.fixedStatement:
            sync_stat_key = 'scur' + str(self.__account._scur_count)

            logging.info('Key to find = ' + sync_stat_key)
            statement_path.append(sync_stat_key)

        satts = {}

        dp = DateParser()

        satts['date'] = dp.ymd_from_date(dp.todate())

        satts['display'] = self.__filename
        satts['ftype'] = self.__type

        satts['_fixedKey'] = self.fixedStatement    #true or false

        satts['rawdata'] = str(self.__body)

        self._current_statement = Statement()

        logging.info('Got a statement with hash - ' + self._current_statement.hash)

        self.facade._statkey =  self._current_statement

    def make_recent_dif_statement(self, type, filename, body):
        self.slidingDif = True
        self.make_recent_statement(type, filename, body)
    
    
    def make_statement(self, type, filename, body):
        self.make_statement_fixed(type, filename, body, False)

    def make_recent_statement(self, type, filename, body):
        self.make_statement_fixed(type, filename, body, True)

    def make_statement_fixed(self, type, filename, body, isFixedKey):

        self.__type = type
        self.__filename = filename
        self.__body = body
        self.fixedStatement = isFixedKey


        if self.fixedStatement:   # is a synchro statement
            atts = MiniParams();
            # get the accoun to get the current key

            logging.info('getting account to build fixed key')

            account_pathlist = self.__pathlist[:]

            logging.info('path  - ' + str( account_pathlist ) )


            #self.__account = self.facade.retrieve(account_pathlist, atts)

            self.__account = Account()

            if None == self.__account:
              logging.error("FUCKIT")


        self.__make_new_statement()

        self._current_statement.mindate=None
        self._current_statement.maxdate=None
        self._current_statement.credits=0
        self._current_statement.debits=0

    def set_balance(self, bal):     # calling this makes the balance explicit (i.e. not quif)
        self.__last_balance = bal
        self.__canfix = True

    def get_last_bal(self):
      return self.__last_balance

    def get_s_path(self):
      return self.__pathlist

    def make_xact(self, atts):

        xact_pathlist = self.__pathlist[:]
        xact_pathlist.append('Xact')

        atts_copy = atts.copy()

        currentXact = Xact();

        dp = DateParser()

        currentXact.date = dp.date_from_ymd(atts['date'])
        currentXact.m = currentXact.date.month
        currentXact.y = currentXact.date.year

        if (self._current_statement.maxdate == None) or (currentXact.date > self._current_statement.maxdate):
            self._current_statement.maxdate = currentXact.date

        if (self._current_statement.mindate == None) or ( currentXact.date < self._current_statement.mindate):
            self._current_statement.mindate = currentXact.date

        self._current_statement.xactcount = self._current_statement.xactcount + 1


        if atts['type'] == 'Debit':
            self._current_statement.debits +=  atts['amount']
        else:
            self._current_statement.credits -=  atts['amount']


        self.__last_xact = currentXact

        self.__xactList.append(atts_copy)
        #account.end_trans()

    def getxactlist(self):
      return self.__xactList

    def getSynchBalance(self):

      if self.__account == None:
        return 0
      else:
        return self.__account.synchbal;

    def getSynchAccountID(self):

      if self.__account == None:
        return self.__account_key;
      else:
        return self.__account.keyname;

    def put_statement(self):
        logging.info("-*-*-*-*-*-*-*----> Put Statement")
        existing = "dunno"

        logging.info("existing - "  + str(existing))

        self.__account.set_fixed_bal(self.__old_synchbal, 0, 0)

        return self._current_statement
