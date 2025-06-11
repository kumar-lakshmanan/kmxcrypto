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

from lib import organizer
from lib import utilities
from lib import fetcher

tls = kTools.KTools()
tls.kdata['uselivedata'] = tls.getSafeConfig(['general','uselivedata'],0)

def doWinnerCheck():
    profitPercentToClose = 2.5
    wc = organizer.WinnerChecker()
    gens = utilities.GeneralServices()

    tls.info("Starting winner check...")
    today = tls.getDateTimeStamp("%Y%m%d%H%M%S")
    winCnt = 0
    openEntries = wc.getCurrentOpenItems()

    tls.info(f"Total open coins {len(openEntries)}")
    if len(openEntries) > 0:
        core = fetcher.ConsolidatedDataFetch(skipFetchingPreData=1)
        core.getCoinPrice.cache_clear()
        for cnt, eachEntry in enumerate(openEntries):
            entryDate = eachEntry["date"]
            coin = eachEntry["coin"]
            buyPrice = eachEntry["price"]
            nowPrice = core.getCoinPrice(coin)
            nowPrice = float(nowPrice.replace('$','').replace(',','') if nowPrice else 0.0)
            noOfDays = tls.getDateDiff(entryDate, today, "%Y%m%d%H%M%S")
            if gens.isPercentageAchived(buyPrice, nowPrice, profitPercentToClose):
                wc.updateWinner(entryDate, coin)
                tls.info(f"{cnt+1}. Win by {coin} after {noOfDays} days, came on {entryDate}!")
                winCnt += 1
            else:
                tls.info(f"{cnt+1}. Waiting for {coin} to win for past {noOfDays} days, came on {entryDate}")    # Buy/Current Price: {buyPrice}/{nowPrice}")

    tls.info(f"Total coins won now: {winCnt}/{len(openEntries)}")
    tls.info("End")
    return (winCnt,len(openEntries))

if __name__ == "__main__":
    doWinnerCheck()
    

