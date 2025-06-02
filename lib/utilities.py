'''
@name: 
@author:  kayma
@createdon: 11-May-2025
@description:



 
'''
__created__ = "11-May-2025" 
__updated__ = "11-May-2025"
__author__ = "kayma"

import os,sys
from common_lib import kTools
from common_lib import kDatabase

# -------- DB Calls ------------

class GeneralServices():
        
    def getPercentaged(self, mainValue, percentage):
        '''
        How much value it will increase or decrease for the given Percentage
        '''
        return mainValue * (percentage/100)
        
    def getPercentageIncrDecr(self, mainValue, percentage):
        '''
        How much value it will increase or decrease for the given Percentage
        '''
        return mainValue + self.getPercentaged(mainValue, percentage)
    
    def getPercentageDifference(self, startValue, endValue):
        '''
        How much percent its increased or decreased between these too
        '''
        return ((endValue - startValue) / abs(startValue)) * 100
    
    def isPercentageAchived(self, startValue, endValue, percentage):
        return self.getPercentageDifference(startValue, endValue) >= percentage
        

class DBServices():
    
    def __init__(self):
        self.tls = kTools.KTools()
        self.tblPNLTopGainersLosers = "kmxcryptos.topgainerslosers"
        self.db = None

    def genericInsertQryBuilder(self, values):
        # Column list (must match the order of `values`)
        columns = [
            "date", "coin", "coinslug", "price", "pricechangepercent", "binanceTradeVolPercent",
            "trend7d", "trendttl", "`rank`", "cmcWatchers", "cmcStarRating", "status",
            "winDate", "winDuration", "isMostVisited", "isMostTrending", "isSentimental",
            "bullvotes", "bearvotes", "bullpercent", "bearpercent", "ttlvotes",
            "trendpercent", "sentimenttype"
        ]
        
        if len(values) != len(columns):
            raise ValueError("Number of values does not match number of columns")
        
        def format_value(v):
            if v is None:
                return "NULL"
            elif isinstance(v, str):
                escaped = v.replace("'", "''")  # Escape single quotes safely
                return f"'{escaped}'"
            else:
                return str(v)
        
        formatted_values = [format_value(v) for v in values]
        
        column_part = ", ".join(columns)
        value_part = ", ".join(formatted_values)
        
        query = f"INSERT INTO {self.tblPNLTopGainersLosers} ({column_part}) VALUES ({value_part});"
        return query    
       
    def genericReadDB(self, query, fetchRawResult=0):
        '''
        Sample qry : "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        '''
        self.tls.debug(f"Fetching data from db")
        self.db = kDatabase.SimpleMySql()
        results = self.db.fetch_query(query)
        self.db.close()
        if fetchRawResult:
            return results
        else:
            return [row[0] for row in results]    
    
    def genericWriteDB(self, dataList):
        self.tls.debug(f"Writing to db")
        self.db = kDatabase.SimpleMySql()
        for eachRow in dataList:
            qry = self.genericInsertQryBuilder(eachRow)
            self.db.execute_query(qry)
        self.db.commit_all()
        self.db.close()    

    def simpleDBUpdate(self, qry, auto_commit_close=1):
        self.tls.debug(f"Updating db")
        self.db = kDatabase.SimpleMySql()
        self.db.execute_query(qry)
        if auto_commit_close:
            self.db.commit_all()
            self.db.close()    
    
    def manual_commit_close(self):
        if self.db:
            self.db.commit_all()
            self.db.close()            
    
    def genericSelectAll(self, tableName):
        self.tls.debug(f"Fetching all data from db")
        query = f"SELECT * FROM {tableName};"    
        return self.genericReadDB(query)    
        
    def genericSelectForDate(self, date, tableName):
        '''
            Should have date field
        '''
        self.tls.debug(f"Fetching data for date {date}")
        query = f"SELECT * FROM {tableName} WHERE date LIKE '{date}%';"    
        return self.genericReadDB(query)    

    #------------------------------------------------
    
    def getPNLAll(self):
        self.tls.debug(f"Fetching PNL all")
        return self.genericSelectAll(self.tblPNLTopGainersLosers)

    def getPNLForDate(self, date):
        self.tls.debug(f"Fetching PNL for {date}")
        return self.genericSelectForDate(date, self.tblPNLTopGainersLosers)

    def getPNLForStatus(self, status):
        self.tls.debug(f"Fetching PNL {status}")
        query = f"SELECT * FROM {self.tblPNLTopGainersLosers} WHERE status = '{status}'"  
        return self.genericReadDB(query, 1)   
    
    def updatePNL(self, entry_date, coin, status, winDate, winDuration):
        self.tls.debug(f"Updating coin {coin} status to {status}")
        qry = f"update {self.tblPNLTopGainersLosers} SET status='{status}', winDate='{winDate}', winDuration='{winDuration}' where date LIKE '{entry_date}%' AND coin = '{coin}';"
        self.simpleDBUpdate(qry, auto_commit_close=0);
        
if __name__ == '__main__':
    db = DBServices()
    opn = db.getPNLForStatus('open')
    print(opn)