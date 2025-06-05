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
from functools import lru_cache
from common_lib import kTools
from common_lib.kcrypto.exchanges.coinmarketcap import CoinMarketCap

class ConsolidatedDataFetch():
    
    def __init__(self, skipFetchingPreData = 0):
        self.tls = kTools.KTools()        
        self.cmc = CoinMarketCap()
        self.todaysSentimentalCoins, self.sentimentDetails = [],[]
        self.todayBinanceToppers = []
        self.todaysMostVisited = []
        self.todaysMostTrending = []
        if not skipFetchingPreData: self.gatherTodaysData()

    def gatherTodaysData(self):
        self.todaysSentimentalCoins, self.sentimentDetails = self.cmc.getCommunitySentiment()
        self.todaysMostVisited = self.cmc.getMostViewed()        
        self.todaysMostTrending = self.cmc.getMostTrending()
        self.todayBinanceToppers = self.cmc.getExchangeVolumeToper()
    
    def _getSentimentDetails(self, coin):
        for each in self.sentimentDetails:
            if coin == each[0]:
                return each
        return ('',None,None,None,None,None,None,None)
    
    def isItMostVisited(self, coin):
        return int(coin in self.todaysMostVisited)

    def isItMostTrending(self, coin):
        return int(coin in self.todaysMostTrending)

    def isItSentimental(self, coin):
        return int(coin in self.todaysSentimentalCoins)
    
    def getCoinSentiment(self, coin):
        '''
        coin,
        bullvotes,
        bearvotes,
        bullpercent,
        bearpercent,
        votes,
        trendPercent,
        type        
        '''
        return self._getSentimentDetails(coin)
        
    @lru_cache  
    def getCoinPrice(self, coin):        
        coinInfo = self.cmc.getCoinInfo(coin)
        return self.tls.getSafeDictValue(coinInfo, 'price', 0.0)
                
    def binanceTradeVolPercent(self, coin):
        for eachEntry in self.todayBinanceToppers:
            if coin == eachEntry['pair']:
                return eachEntry['tradedVolPercent']
        return 0
    
    def fetchTodayTopGainersLosers(self, cleanFetch=0):
        self.tls.debug("Fetching top gainers and losers..")
        today = self.tls.getDateTimeStamp()

        if cleanFetch: self.cmc.clearCache()
        topGainers = self.cmc.getTopGainer()
        topLosers = self.cmc.getTopLoser()
        
        def entryFormat(entry):
            coin = entry['symbol']
            coinInfo = self.cmc.getCoinInfo(coin)
            if not coinInfo: self.tls.debug(f"Coin info missing for {coin}")
            if not coinInfo: return None
            nw = []
            nw.append(today)
            nw.append(coin)
            nw.append(entry['slug'])
            nw.append(entry['price'])
            nw.append(entry['priceChangePercent'])
            nw.append(self.binanceTradeVolPercent(coin))
            nw.append(coinInfo['trend7d'])
            nw.append(coinInfo['trendttl'])
            nw.append(coinInfo['rank'])
            nw.append(coinInfo['cmcWatchers'])
            nw.append(coinInfo['cmcStarRating'])
            nw.append('open')
            nw.append(None)
            nw.append(None)
            nw.append(self.isItMostVisited(coin))
            nw.append(self.isItMostTrending(coin))
            nw.append(self.isItSentimental(coin))
            sentiData = self.getCoinSentiment(coin)
            nw.append(sentiData[1]) #bullvotes
            nw.append(sentiData[2]) #bearvotes
            nw.append(sentiData[3]) #bullpercent
            nw.append(sentiData[4]) #bearpercent
            nw.append(sentiData[5]) #votes
            nw.append(sentiData[6]) #trendPercent
            nw.append(sentiData[7]) #type
            return nw    
            
        combined = []
        for entry in topGainers:
            nw = entryFormat(entry)
            if nw: combined.append(nw)
    
        for entry in topLosers:
            nw = entryFormat(entry)
            if nw: combined.append(nw)
         
        return combined   
    
    def isMissing(self, item):
        return item == None or str(item).strip() == ""

    def myGuessFilter(self, allTopGainerLoser):
        self.tls.debug("Picking my-guess coins...")        
        picked = []
        for each in allTopGainerLoser:
            today = each[0]
            coin = each[1]
            slug = each[2]
            price = each[3]
            priceChangePercent = each[4]
            binTradVolPercent = each[5]
            trend7d = each[6]
            trendttl = each[7]
            rank = each[8]
            cmcWatchers = int(each[9])
            cmcStarRating = float(each[10])
            status = each[11]
            windate = each[12]
            windur = each[13]
            isItMostVisited = each[14]
            isItMostTrending = each[15]
            isItSentimental = each[16]
            bullvotes = each[17]
            bearvotes = each[18]
            bullpercent = each[19]
            bearpercent = each[20]
            ttlvotes = each[21]
            trendPercent = each[22]
            type = each[23]
            
            # Info should not be missed
            if (self.isMissing(bullvotes) or
                self.isMissing(bearvotes) or
                self.isMissing(bullpercent) or
                self.isMissing(bearpercent) or
                self.isMissing(ttlvotes) or
                self.isMissing(trendPercent)):
                continue
            
            # Price Change Percent should be less then 0 
            if not (priceChangePercent < 0):  continue
            
            # Should be in binance and trade vol in it should be above zero
            if not (binTradVolPercent > 0):  continue
            
            # rank should be below 50
            if not (rank < 50 and rank > 10):  continue
                
            # cmcWatchers should be above 100k
            if not (cmcWatchers > 100000):  continue
            
            # cmcStarRating should be above 1
            if not (cmcStarRating > 1):  continue
            
            picked.append(each)
            
        return picked
