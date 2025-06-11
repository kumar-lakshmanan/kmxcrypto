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
from kcrypto.exchanges.coinmarketcap import CoinMarketCap
import kTools

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
            data = {}
            data['date'] = today = each[0]
            data['coin'] = coin = each[1]
            data['coinslug'] = slug = each[2]
            data['price'] = price = each[3]
            data['pricechangepercent'] = priceChangePercent = each[4]
            data['binanceTradeVolPercent'] = binTradVolPercent = each[5]
            data['trend7d'] = trend7d = each[6]
            data['trendttl'] = trendttl = each[7]
            data['rank'] = rank = each[8]
            data['cmcWatchers'] = cmcWatchers = int(each[9])
            data['cmcStarRating'] = cmcStarRating = float(each[10])
            data['status'] = status = each[11]
            data['winDate'] = windate = each[12]
            data['winDuration'] = windur = each[13]
            data['isMostVisited'] = isItMostVisited = each[14]
            data['isMostTrending'] = isItMostTrending = each[15]
            data['isSentimental'] = isItSentimental = each[16]
            data['bullvotes'] = bullvotes = each[17]
            data['bearvotes'] = bearvotes = each[18]
            data['bullpercent'] = bullpercent = each[19]
            data['bearpercent'] = bearpercent = each[20]
            data['ttlvotes'] = ttlvotes = each[21]
            data['trendPercent'] = trendPercent = each[22]
            data['sentimenttype'] = type = each[23]

            # Info should not be missed
            if (self.isMissing(bullvotes) or
                self.isMissing(bearvotes) or
                self.isMissing(bullpercent) or
                self.isMissing(bearpercent) or
                self.isMissing(ttlvotes) or
                self.isMissing(trendPercent)):
                self.tls.debug(f" {coin} - missed few infos: BLV: {bullvotes}, BRV: {bearvotes}, BLP: {bullpercent}, BRP: {bearpercent}, TTLV: {ttlvotes}, TRP: {trendPercent}")
                continue

            # Price Change Percent should be less then 0
            if not (priceChangePercent < 0):
                self.tls.debug(f" {coin} - Faild priceChangePercent {priceChangePercent} < 0")
                continue

            # Should be in binance and trade vol in it should be above zero
            if not (binTradVolPercent > 0):
                self.tls.debug(f" {coin} - Faild binTradVolPercent {binTradVolPercent} > 0")
                continue

            # rank should be below 50
            if not (rank < 50 and rank > 10):
                self.tls.debug(f" {coin} - Faild rank {rank} < 50 and > 10")
                continue

            # cmcWatchers should be above 100k
            if not (cmcWatchers > 100000):
                self.tls.debug(f" {coin} - Faild cmcWatchers {cmcWatchers} > 100000")
                continue

            # cmcStarRating should be above 1
            if not (cmcStarRating > 1):
                self.tls.debug(f" {coin} - Faild cmcStarRating {cmcStarRating} > 1")
                continue

            picked.append(data)
            
        return picked

# ['20250610214412', 'UNI', 'uniswap', 8.222292052231788, 26.13793341, 0.82, '3.4', '445', 28, 770000, 0, 'open', None, None, 1, 1, 1, 51, 6, 89.5, 10.5, 172, 16.9, 'bullish']

# {'date': 20250610023004, 'coin': 'AVAX', 'coinslug': 'avalanche', 'price': 21.31964523555377,
# 'pricechangepercent': -0.57316786, 'binanceTradeVolPercent': 0.32, 'trend7d': -3, 'trendttl': 235, 'rank': 14,
# 'cmcWatchers': 1000000, 'cmcStarRating': 4, 'status': 'pass', 'winDate': 20250610034002,
# 'winDuration': 0, 'isMostVisited': 1, 'isMostTrending': 1, 'isSentimental': 1,
# 'bullvotes': 86, 'bearvotes': 21, 'bullpercent': 80, 'bearpercent': 20, 'ttlvotes': 234, 'trendpercent': 3.3, 'sentimenttype': 'bullish'}