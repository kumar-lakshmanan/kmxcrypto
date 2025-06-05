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

tls = kTools.KTools()

def fetchTodaysCoin(forceUpdate = 0):
    tls.info("Start fetching new coin...")
    todaysTopGainerLoserList = []
    filteredCoins = []

    dbs = utilities.DBServices()

    todaysTopGainerLoserList = dbs.getPNLForDate(tls.getDateTimeStamp("%Y%m%d"))

    if len(todaysTopGainerLoserList) <= 0 or forceUpdate:
        core = fetcher.ConsolidatedDataFetch()

        tls.info("Fetching top gainers and losers...")
        todaysTopGainerLoserList = core.fetchTodayTopGainersLosers(1)
        filteredCoins = core.myGuessFilter(todaysTopGainerLoserList)
        if (len(filteredCoins)):
            dbs.genericWriteDB(filteredCoins)

    ret = f"Status: TotalTopGainersLosers: {len(todaysTopGainerLoserList)}/Filtered : {len(filteredCoins)}"
    tls.info(ret)
    return ret

if __name__ == "__main__":
    fetchTodaysCoin()



