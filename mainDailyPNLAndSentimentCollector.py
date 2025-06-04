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

from lib import utilities
from lib import fetcher

if __name__ == "__main__":

    tls = kTools.KTools()
    tls.logSys.setLevel("DEBUG")
    
    core = fetcher.ConsolidatedDataFetch()
    gens = utilities.GeneralServices()
    dbs = utilities.DBServices()
        
    tls.info("Start...")
    forceUpdate = 1
    
    tls.info("Is todays data captured?")
    todaysTopGainerLoserList = dbs.getPNLForDate(tls.getDateTimeStamp("%Y%m%d"))
    
    if len(todaysTopGainerLoserList) <= 0 or forceUpdate:
        
        tls.info("Fetching top gainers and losers...")
        todaysTopGainerLoserList = core.fetchTodayTopGainersLosers(1)
        tls.info(f"Total top gainers and losers : {len(todaysTopGainerLoserList)}")
        
        filteredCoins = core.myGuessFilter(todaysTopGainerLoserList)
                
        if (len(filteredCoins)):
            dbs.genericWriteDB(filteredCoins)
    
    tls.info(f"Today Picked: {len(filteredCoins)}")
    
    tls.info("End")
    


