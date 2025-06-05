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

def doWinnerCheck():

    gens = utilities.GeneralServices()
    dbs = utilities.DBServices()

    profitPercentToClose = 2.5

    tls.info("Start...")
    today = tls.getDateTimeStamp("%Y%m%d%H%M%S")
    winCnt = 0
    openEntries = dbs.getPNLForStatus('open')
    tls.info(f"Total open coins {len(openEntries)}")
    if len(openEntries) > 0:
        core = fetcher.ConsolidatedDataFetch(skipFetchingPreData=1)
        core.getCoinPrice.cache_clear()
        for cnt, eachEntry in enumerate(openEntries):
            entryDate = eachEntry[1]
            coin = eachEntry[2]
            coinSlug = eachEntry[3]
            buyPrice = eachEntry[4]
            nowPrice = core.getCoinPrice(coin)
            nowPrice = float(nowPrice.replace('$','').replace(',','') if nowPrice else 0.0)
            noOfDays = tls.getDateDiff(entryDate, today, "%Y%m%d%H%M%S")
            if gens.isPercentageAchived(buyPrice, nowPrice, profitPercentToClose):
                tls.info(f"{cnt+1}. Win by {coin} after {noOfDays} days, came on {entryDate}!")
                dbs.updatePNL(entryDate, coin, 'pass', today, noOfDays)
                winCnt += 1
            else:
                tls.info(f"{cnt+1}. Waiting for {coin} to win for past {noOfDays} days, came on {entryDate}")    # Buy/Current Price: {buyPrice}/{nowPrice}")
        dbs.manual_commit_close()

    tls.info(f"Total coins won now: {winCnt}/{len(openEntries)}")
    tls.info("End")
    return (winCnt,len(openEntries))

if __name__ == "__main__":
    doWinnerCheck()
    

