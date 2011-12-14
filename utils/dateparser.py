import datetime

class DateParser:
    
    def get_divider(self, datestr):
        div = '-'
        pathlist = datestr.split(div)
        if len(pathlist) == 3:
            return div 
        div = '/'
        pathlist = datestr.split(div)
        if len(pathlist) == 3:
            return div
        div = '\\'
        pathlist = datestr.split(div)
        if len(pathlist) == 3:
            return div
        div = ' '
        pathlist = datestr.split(div)
        if len(pathlist) == 3:
            return div
        return ''
    
    def date_from_dmy(self, datestr, div = '-'):
        medate = None
        pathlist = datestr.split(div)
        if len(pathlist) == 3:
            if len(pathlist[2]) == 2:
                pathlist[2] = '20'+ pathlist[2]
            medate = datetime.date(int(pathlist[2]), int(pathlist[1]), int(pathlist[0]))
        return medate
    
    def date_from_small(self, datestr, div = ' '):
        pathlist = datestr.split(div)
        if len(pathlist) == 3:
            if len(pathlist[2]) == 2:
                pathlist[2] = '20'+ pathlist[2]
            if len(pathlist[1]) == 3:
                mon = pathlist[1].upper()
                imon = 0;
                if 'JAN' == mon:
                    imon = 1
                if 'FEB' == mon:
                    imon = 2
                if 'MAR' == mon:
                    imon = 3
                if 'APR' == mon:
                    imon = 4
                if 'MAY' == mon:
                    imon = 5
                if 'JUN' == mon:
                    imon = 6
                if 'JUL' == mon:
                    imon = 7
                if 'AUG' == mon:
                    imon = 8
                if 'SEP' == mon:
                    imon = 9
                if 'OCT' == mon:
                    imon = 10
                if 'NOV' == mon:
                    imon = 11
                if 'DEC' == mon:
                    imon = 12
                
            medate = datetime.date(int(pathlist[2]), imon, int(pathlist[0]))
        return medate
    
    def date_from_ymd(self, datestr, div = '-'):
        medate = None
        pathlist = datestr.split(div)
        if len(pathlist) == 3:
            if len(pathlist[0]) == 2:
                pathlist[0] = '20'+ pathlist[0]
            medate = datetime.date(int(pathlist[0]), int(pathlist[1]), int(pathlist[2]))
        return medate
    
    def date_from_ymd_fixed(self, datestr):
        medate = None
        medate = datetime.date(int(datestr[0:3]), int(datestr[4:5]), int(datestr[6:8]))
        return medate
    
    def todate(self):
        return datetime.datetime.today().date()
    
    def todatetime(self):
        return datetime.datetime.today()
    
    def ymd_from_date(self, medate):
        return str(medate.year) + '-' + str(medate.month) + '-' + str(medate.day)

    def ym_from_date(self, medate):
        return str(medate.year) + str(medate.month)

    def date_from_ymdhms(self, indatetime):
        #"2010-11-27T14:34:58.012124"
        medate = None
        
        partlist = indatetime.split('T')
        if len(partlist) != 2:                  #try splitting on spaces
            partlist = indatetime.split(' ')
    
        if len(partlist) == 2:
            good_date = False
            good_time = False
            
            timelist = partlist[1].split(':')
            if len(timelist) == 3:
                good_time = True
                # strip off miliseconds
                seclist = timelist[2].split('.')
                if len(seclist) == 2:
                    timelist[2] = seclist[0]
            
            pathlist = partlist[0].split('-')
            if len(pathlist) == 3:
                if len(pathlist[0]) == 2:
                    pathlist[0] = '20'+ pathlist[0]
                good_date = True
                
            if good_time and good_date:
                medate = datetime.datetime(int(pathlist[0]), int(pathlist[1]), int(pathlist[2]),
                                           int(timelist[0]), int(timelist[1]), int(timelist[2]))
        return medate
    
    def ymdhms_from_date(self, medate):
        #2010-08-02T18:08:54.264207
        return str(medate.year) + '-' + str(medate.month) + '-' + str(medate.day) + "T" + str(medate.hour) + ":" + str(medate.minute) + ":" +str(medate.second)

    def add_month(self, medate):
        m = medate.month
        if m == 12:
            m = 1
            y = medate.year + 1
            medate = medate.replace(year=y)
        else:
            m = m + 1;
            
        try:
            medate = medate.replace(month=m)
        except ValueError:
            if m == 2:
               d = 29
            else:
                d = d -1
            try:
                medate = medate.replace(month=m, day=d)
            except ValueError:
                d = 28
                medate = medate.replace(month=m, day=d)
        
        return medate

    def dec_month(self, medate):
        m = medate.month
        d = medate.day
        if m == 1:
            m = 12
            y = medate.year - 1
            medate = medate.replace(year=y)
        else:
            m = m - 1;
            
            
        try:
            medate = medate.replace(month=m)
        except ValueError:
            if m == 2:
               d = 29
            else:
                d = d -1
            try:
                medate = medate.replace(month=m, day=d)
            except ValueError:
                d = 28
                medate = medate.replace(month=m, day=d)
            
        return medate

    def add_week(self, medate):
        delta = datetime.timedelta(days=7)
        return medate + delta