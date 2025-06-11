'''
@name: 
@author:  kayma
@createdon: 11-May-2025
@description:

'''
__created__ = "11-May-2025" 
__updated__ = "11-May-2025"
__author__ = "kayma"

import kTools
from lib import fetcher
from lib import organizer

tls = kTools.KTools()

def doFetchCoin(forceUpdate = 0):
    fc = organizer.FetchCoin()
    filteredCoins = []
    todaysTopGainerLoserList = fc.getTodaysCollection()
    tls.info("Verify is today already collected... " + str(len(todaysTopGainerLoserList)))
    if len(todaysTopGainerLoserList) <= 0 or forceUpdate:
        tls.info("Start analysing new coin...")
        core = fetcher.ConsolidatedDataFetch()
        tls.info("Fetching top gainers and losers...")
        todaysTopGainerLoserList = core.fetchTodayTopGainersLosers(1)
        tls.info(f"Found {len(todaysTopGainerLoserList)}")
        filteredCoins = core.myGuessFilter(todaysTopGainerLoserList)
        tls.info(f"Filtering with my logic, Found: {len(filteredCoins)}")
        for eachCoin in filteredCoins:
            res = fc.addToCollection(eachCoin)
            tls.info(f"Added {eachCoin['coin']}") if res else tls.error(f"Unable to add date {eachCoin['coin']}")
    ret = f"Status: TotalTopGainersLosers: {len(todaysTopGainerLoserList)}/Filtered : {len(filteredCoins)}"
    tls.info(ret)
    return ret

if __name__ == "__main__":
    doFetchCoin()