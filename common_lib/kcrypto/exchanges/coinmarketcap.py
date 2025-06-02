'''
@name: 
@author:  kayma
@createdon: 06-May-2025
@description:



 
'''
__created__ = "06-May-2025" 
__updated__ = "06-May-2025"
__author__ = "kayma"

from requests import Session
from bs4 import BeautifulSoup
from functools import lru_cache
from operator import itemgetter
from urllib.parse import urljoin, urlencode
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

import requests
import json
import codecs
import time
import hmac
import hashlib
import unicodedata

from common_lib import kWebClient
from common_lib import kTools
            
class CoinMarketCap(object):

    def __init__(self, api_key=''):
        '''
        Constructor
        '''

        self.tls = kTools.KTools()
        self.tls.debug('Initializing {0}'.format(self.__class__.__name__))
        
        self.baseUrl = 'https://pro-api.coinmarketcap.com/v1'
        self.api_key = api_key if api_key else "d8e96fef-e457-4816-91ed-1c9301cf4dae"
        
        self._pnlData = None
        self._communitySentimentData = None
        
        self.nowSlugs = []
    
    def _urlCallSimple(self, url, params={}, payload={}):
        '''
        Simple Get Call with API response output
        '''
        #print(url)
        #url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        #print(url)
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
        session = Session()
        session.headers.update(headers)
        data = ''
        try:
            self.tls.debug('Calling ' + url)
            if payload:
                response = session.post(url, payload, params)
            else:
                response = session.get(url, params=params)
            data = json.loads(response.text)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            self.tls.error(e)        
        return data
    
    def _urlCall(self, uri='/cryptocurrency/listings/latest', params={}):
        url = self.baseUrl + uri    
        #print(url)
        #url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        #print(url)        
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
            'x-request-id': 'f7bc4c600b2f463d88882641791e1384'
        }
        session = Session()
        session.headers.update(headers)
        data = ''
        try:
            self.tls.debug('Calling ' + url)
            response = session.get(url, params=params)
            data = json.loads(response.text)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            self.tls.error(e)        
        return data
                
    def clearCache(self):
        self.getCoinInfo.cache_clear()
        self.getExchangeVolumeToper.cache_clear()
        self.getTopGainer.cache_clear()
        self.getTopLoser.cache_clear()
        self._fetchCachedSlug.cache_clear()
        self._fetchLiveSlugs.cache_clear()        
        
    def getCommunityTrendStatus(self, cryptoUCID=52):
        '''
            {"trend":"-1.9","total":"371"}    @TIME FRAME MIGHT BE 7 BUT ITS 24HRS
            tred = 7ds
            totals = 24h
            CHECK INSIDE BULLIST BEARISH COMMINUTY SECTION
        '''
        respJson = {}        
        url = 'https://api.coinmarketcap.com/gravity/v3/gravity/vote/overview-data' #works
        payloads = {}
        payloads['cryptoId'] = cryptoUCID
        payloads['timeFrame'] = 1
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        wc = kWebClient.WebClient(base_url=url)
        resp = wc.post('', payloads, headers)
        if resp.status_code == 200 :
            respJson = resp.json()
            respJson = respJson['data']
        else:
            tls.error("Unable to fetch: ")
            tls.error(resp)            
        return respJson        
        
    def getMostViewed(self):
        mostVisited = []
        murl = 'https://coinmarketcap.com/most-viewed-pages/'
        self.tls.debug(f'Calling {murl}')
        page = requests.get(murl)
        soup = BeautifulSoup(page.content, "html.parser")
        rows = soup.find('table').find('tbody').find_all('tr')
        for eachRow in rows:
            coin = eachRow.find('p', attrs = {'color': 'text3', 'data-sensors-click':'true'}).text
            mostVisited.append(coin)
        return mostVisited
    
    def getMostTrending(self):
        mostVisited = []
        murl = 'https://coinmarketcap.com/trending-cryptocurrencies/'
        self.tls.debug(f'Calling {murl}')
        page = requests.get(murl)
        soup = BeautifulSoup(page.content, "html.parser")
        rows = soup.find('table').find('tbody').find_all('tr')
        for eachRow in rows:
            coin = eachRow.find('p', attrs = {'color': 'text3', 'data-sensors-click':'true'}).text
            mostVisited.append(coin)
        return mostVisited    
        
    def getCommunitySentiment(self):
        '''
        https://api.coinmarketcap.com/gravity/v3/gravity/vote/get-sentiment-leaderboard
        post        
        '''
    
        payload = {}
        payload['coinsTopN'] = 100
        payload['timeframe'] = '24h'
                
        url = "https://api.coinmarketcap.com/gravity/v3/gravity/vote/get-sentiment-leaderboard"
       
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
            'x-request-id': 'f7bc4c600b2f463d88882641791e1384'
        }
        session = Session()
        session.headers.update(headers)
        data = ''
        try:
            self.tls.debug('Calling ' + url)
            response =  session.post(url, json=payload, headers=headers)
            data = json.loads(response.text)
            data = data['data']
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            self.tls.error(e)       

        sentiments = []
        addedCoins = []

        def addCoinToSentiments(coinRow, type):
            coin = coinRow['symbol']
            if not coin in addedCoins: 
                bullvotes = coinRow['bullishVotes']
                bearvotes = coinRow['bearishVotes']
                bullpercent = float(coinRow['bullishRate'])
                bearpercent = float(coinRow['bearishRate'])
                votes =  coinRow['votes']
                trendPercent =  coinRow['voteChange']
                addedCoins.append(coin)
                sentiments.append((
                        coin,
                        bullvotes,
                        bearvotes,
                        bullpercent,
                        bearpercent,
                        votes,
                        trendPercent,
                        type
                    ))

        for each in data['mostBullish']:
            addCoinToSentiments(each, "bullish")
            
        for each in data['mostBearish']:
            addCoinToSentiments(each, "bearish")       
            
        for each in data['topGainerInBullishVotes']:
            addCoinToSentiments(each, "bullish")                   

        for each in data['topGainerInBearishVotes']:
            addCoinToSentiments(each, "bearish")
            
        for each in data['mostVotes']:
            addCoinToSentiments(each, "active")        

        return (addedCoins, sentiments)        
    
    def safeFetch(self, fetchLogic, label="Unknown", currentCoinSlug=None, default=None):
        """
        Tries to execute fetch_func(*args, **kwargs). If it fails, prints an error and returns the default.
        
        Parameters:
            fetch_func: A callable/lambda that fetches/parses from BeautifulSoup.
            *args, **kwargs: Arguments passed to the fetch_func.
            default: Value to return on error.
            label: A label for logging which field failed.
    
        Returns:
            The result of fetch_func or the default value.
        """
        try:
            return fetchLogic()
        except Exception as e:
            if 0: self.tls.error(f"[ERROR] Failed to fetch {label} value for {currentCoinSlug}")
            return default

    @lru_cache(maxsize=100)        
    def getCoinInfo(self, coin, slug=None):
        info = {}
                
        coinSlug = slug if slug else self.getCoinSlug(coin)
        if coinSlug == None: return None
  
        murl = f'https://coinmarketcap.com/currencies/{coinSlug}/'
        self.tls.debug(f'Calling {murl}')
        page = requests.get(murl)
        soup = BeautifulSoup(page.content, "html.parser")
  
        try:     
                   
            name = self.safeFetch(
                lambda:soup.find('span', attrs = {'data-role': 'coin-name'}, title=True).contents[0].text,
                label = "name",
                currentCoinSlug = coinSlug
                )
            
            symbol = self.safeFetch(
                lambda:soup.find(lambda tag: (tag.name == 'span' and 'base-text' in tag.get('class', []) and tag.get('data-role') == 'coin-symbol')).contents[0].text,
                label = "symbol",
                currentCoinSlug = coinSlug
                )
            
            rank = self.safeFetch(
                lambda:soup.find('div', attrs = {'data-role': 'chip-content-item'}).contents[0].text,
                label = "rank",
                currentCoinSlug = coinSlug
                )
            
            slug = coinSlug
            
            cmcWatchers = self.safeFetch(
                lambda:soup.find(lambda tag:(tag.name=='div' and tag.get('data-role') == 'btn-content-item' and any('BaseButton_labelWrapper' in cls for cls in tag.get('class', [])) and len(tag.find_all('span', recursive=False)) == 1 and 'base-text' in tag.find('span', recursive=False).get('class', []))).contents[0].text,
                label = "cmcWatchers",
                currentCoinSlug = coinSlug
                )
            
            cmcStarRating = self.safeFetch(
                lambda:soup.find(lambda tag:(tag.name=='div' and any('RatingSection_wrapper' in cls for cls in tag.get('class', [])))).text.strip(),
                label = "cmcStarRating",
                currentCoinSlug = coinSlug,
                default = 0
                )

            price = self.safeFetch(
                lambda:soup.find('span', attrs = {'data-test': 'text-cdp-price-display'}).contents[0].text,
                label = "price",
                currentCoinSlug = coinSlug
                )
            
            priceChangeParentTag = self.safeFetch(
                lambda:soup.find(lambda tag:(tag.name=='div' and tag.get('data-role') == 'percentage-value' and tag.get('data-sensors-click', True) and len(tag.find_all('p', recursive=False)) == 1 and 'change-text' in tag.find('p', recursive=False).get('class', []))),
                label = "priceChangeParentTag",
                currentCoinSlug = coinSlug
                )
            
            priceChangeTag = self.safeFetch(
                lambda:priceChangeParentTag.find('p', recursive=False),
                label = "priceChangeTag",
                currentCoinSlug = coinSlug
                )
            
            priceChangePercent = self.safeFetch(
                lambda:priceChangeTag.text.split('%')[0],
                label = "priceChangePercent",
                currentCoinSlug = coinSlug
                )
            
            priceChangeIsUp = self.safeFetch(
                lambda:priceChangeTag.get('data-change') == 'up' and priceChangeTag.get('color') == 'green',
                label = "priceChangeIsUp",
                currentCoinSlug = coinSlug
                )
            
            marketCap = self.safeFetch(
                lambda:soup.find(string="Market cap").findPrevious('dt').findNext('dd').find('span').text,
                label = "marketCap",
                currentCoinSlug = coinSlug
                )
            
            marketCapPercent = self.safeFetch(
                lambda:soup.find(string="Market cap").findPrevious('dt').findNext('dd').find(lambda tag:(tag.name=='div' and tag.get('data-role') == 'percentage-value')).text,
                label = "marketCapPercent",
                currentCoinSlug = coinSlug
                )
            
            vol24 = self.safeFetch(
                lambda:soup.find(string="Volume (24h)").findPrevious('dt').findNext('dd').find('span').text,
                label = "vol24",
                currentCoinSlug = coinSlug
                )
            
            vol24Percent = self.safeFetch(
                lambda:soup.find(string="Volume (24h)").findPrevious('dt').findNext('dd').find(lambda tag:(tag.name=='div' and tag.get('data-role') == 'percentage-value')).text,
                label = "vol24Percent",
                currentCoinSlug = coinSlug
                )
            
            fdv = self.safeFetch(
                lambda:soup.find(string="FDV").findPrevious('dt').findNext('dd').find('span').text,
                label = "fdv",
                currentCoinSlug = coinSlug
                )
            
            volMarkPercent = self.safeFetch(
                lambda:soup.find(string="Vol/Mkt Cap (24h)").findPrevious('dt').findNext('dd').text,
                label = "volMarkPercent",
                currentCoinSlug = coinSlug
                )
            
            holders = self.safeFetch(
                lambda:soup.find(string="Holders").findPrevious('dt').findNext('dd').text,
                label = "holders",
                currentCoinSlug = coinSlug
                )
            
            supply = self.safeFetch(
                lambda:soup.find(string="Total supply").findPrevious('dt').findNext('dd').text,
                label = "supply",
                currentCoinSlug = coinSlug
                )
            
            cirsupply = self.safeFetch(
                lambda:soup.find(string="Circulating supply").findPrevious('dt').findNext('dd').find('span').text,
                label = "cirsupply",
                currentCoinSlug = coinSlug
                )
            
            cirsupplyPercent = self.safeFetch(
                lambda:soup.find(string="Circulating supply").findPrevious('dt').findNext('dd').find('progress').text,
                label = "cirsupplyPercent",
                currentCoinSlug = coinSlug
                )
            
            priceLowest = self.safeFetch(
                lambda:soup.find(string="Low").findNext("span").text,
                label = "priceLowest",
                currentCoinSlug = coinSlug
                )
            
            priceHighest = self.safeFetch(
                lambda:soup.find(string="High").findNext("span").text,
                label = "priceHighest",
                currentCoinSlug = coinSlug
                )
            
            
            allTimeHighWhen = self.safeFetch(
                lambda:soup.find(string="All-time high").findPrevious('div').findNext('div').text,
                label = "allTimeHighWhen",
                currentCoinSlug = coinSlug
                )
            
            allTimeHighPrice = self.safeFetch(
                lambda:soup.find(string="All-time high").findPrevious('div').findNextSibling('div').find("span").text,
                label = "allTimeHighPrice",
                currentCoinSlug = coinSlug
                )
            
            allTimeHighPercent = self.safeFetch(
                lambda:soup.find(string="All-time high").findPrevious('div').findNextSibling('div').find("div").text,
                label = "allTimeHighPercent",
                currentCoinSlug = coinSlug
                )
            
            allTimeLowWhen = self.safeFetch(
                lambda:soup.find(string="All-time low").findPrevious('div').findNext('div').text,
                label = "allTimeLowWhen",
                currentCoinSlug = coinSlug
                )
            
            allTimeLowPrice = self.safeFetch(
                lambda:soup.find(string="All-time low").findPrevious('div').findNextSibling('div').find("span").text,
                label = "allTimeLowPrice",
                currentCoinSlug = coinSlug
                )
            
            allTimeLowPercent = self.safeFetch(
                lambda:soup.find(string="All-time low").findPrevious('div').findNextSibling('div').find("div").text,
                label = "allTimeLowPercent",
                currentCoinSlug = coinSlug
                )
            
            ucid = self.safeFetch(
                lambda:soup.find(string="UCID").findPrevious(lambda tag:(tag.name=='div' and any('InfoBarItem' in cls for cls in tag.get('class', [])))).findPrevious('div').findNextSibling('div').findNext('div', attrs = {'data-role': 'chip-content-item'}).text,
                label = "ucid",
                currentCoinSlug = coinSlug
                )
            
            trends = self.getCommunityTrendStatus(ucid)
            trend7d = trends['trend']
            trendttl = trends['total']            
                       
            info['name'] = name
            info['slug'] = slug
            info['symbol'] = symbol
            info['rank'] = int(rank.replace('#',''))

            info['cmcWatchers'] = self.tls.shortHandNumberConverter(cmcWatchers)
            info['cmcStarRating'] = cmcStarRating
            info['ucid'] = ucid
            
            info['trend7d'] = trend7d
            info['trendttl'] = trendttl                        
            
            info['price'] = price
            info['priceChangePercent'] = priceChangePercent
            info['priceChangeIsUp'] = priceChangeIsUp
            info['priceLowest'] = priceLowest
            info['priceHighest'] = priceHighest
            
            info['marketCap'] = marketCap
            info['marketCapPercent'] = marketCapPercent
            
            info['vol24'] = vol24
            info['vol24Percent'] = vol24Percent
            
            info['fdv'] = fdv
            info['volMarkPercent'] = volMarkPercent
            
            info['holders'] = holders
            info['supply'] = supply
            
            info['cirsupply'] = cirsupply
            info['cirsupplyPercent'] = cirsupplyPercent
            
            info['allTimeHighWhen'] = allTimeHighWhen
            info['allTimeHighPrice'] = allTimeHighPrice
            info['allTimeHighPercent'] = allTimeHighPercent
            info['allTimeLowWhen'] = allTimeLowWhen
            info['allTimeLowPrice'] = allTimeLowPrice
            info['allTimeLowPercent'] = allTimeLowPercent
            
        except Exception as e:
            self.tls.error(f'Error Parsing: CMC URL: {murl}')        
            print(self.tls.getLastErrorInfo())

        return info

    @lru_cache
    def getExchangeVolumeToper(self, exchange='binance'):
        '''
        
        '''
        murl = f'https://coinmarketcap.com/exchanges/{exchange}/'
        
        page = requests.get(murl)
        soup = BeautifulSoup(page.content, "html.parser")
        #results = soup.find('tbody')
        tmp = soup.find_all("table", {"class": "cmc-table"})
        tmp2 = tmp[1].find('tbody')
        rows = tmp2.find_all("tr")
        datas = []
        for each in rows:
            r = each.find_all('td')
            if r:
                ##    Currency    Pair        Price        +2% Depth        -2% Depth            Volume        Volume %    Liquidity    Updated
                #1    Bitcoin    BTC/USDT    $21,178.45    $12,252,961.25    $18,986,372.75    $1,239,475,283    13.50%    1,008    Recently'
                #1 BTC/USDT 2.70%
                #2 GMT/USDT 1.39%
                #3 ETH/USDT 2.17%            
                rank = r[0].text
                pair = r[2].text
                pair = pair.replace('/USDT','')
                price = r[3].text
                price = price.replace('$','').replace(',','')
                price = float(price)
                tradedVol = r[6].text
                tradedVol = tradedVol.replace('$','').replace(',','')
                tradedVol = float(tradedVol)                        
                tradedVolPercent = r[7].text
                tradedVolPercent = tradedVolPercent.replace('$','').replace(',','').replace('%','')
                tradedVolPercent = float(tradedVolPercent)            
                # liquidity = r[8].text
                # liquidity = liquidity.replace('$','').replace(',','')
                # liquidity = float(liquidity)
                
                if 'USDT' in r[2].text:                
                    tmp = {}
                    tmp['rank'] = int(rank)
                    tmp['pair'] = pair
                    tmp['price'] = price
                    tmp['tradedVol'] = tradedVol
                    tmp['tradedVolPercent'] = tradedVolPercent
                    #tmp['liquidity'] = liquidity
                    
                    datas.append(tmp)
            
        return datas        

    @lru_cache                    
    def getTopGainer(self,howManyToFetch=30):
        '''
        Top Gainers
        list of 
         {'rank': 47, 'symbol': 'ARB', 'priceChangePercent': 24.76435623, 'price': 0.47292536362258264, 'vol': 718956460.1037422, 'slug': 'arbitrum'}
        '''
        murl = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/spotlight?dataType=2&limit=[TOFETCH]&rankRange=[RANKRANGE]&timeframe=24h'
        
        rankRange = str(100) #60 - 100        
        toFetch = howManyToFetch #100
        
        toFetch = str(toFetch)        
        murl = murl.replace('[TOFETCH]',toFetch)
        murl = murl.replace('[RANKRANGE]',rankRange)
        self._pnlData = self._pnlData if self._pnlData else self._urlCallSimple(murl) #data/gainerlist
        data = []
        if self._pnlData:
            lst = self._pnlData['data']['gainerList']
            data = self._getGainerLoserInfo(lst)
        return data

    @lru_cache
    def getTopLoser(self,howManyToFetch=30):
        '''
        Top Loser
        list of 
        {'rank': 22, 'symbol': 'LEO', 'priceChangePercent': -5.01474223, 'price': 8.257778476890165, 'vol': 8490845.99827765, 'slug': 'unus-sed-leo'}
        '''
        murl = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/spotlight?dataType=2&limit=[TOFETCH]&rankRange=[RANKRANGE]&timeframe=24h'
        toFetch = howManyToFetch
        toFetch = str(toFetch) #5 - 30
        rankRange = str(100) #60 - 100
        murl = murl.replace('[TOFETCH]',toFetch)
        murl = murl.replace('[RANKRANGE]',rankRange)
        self._pnlData = self._pnlData if self._pnlData else self._urlCallSimple(murl)        
        data = []
        if self._pnlData:  
            lst = self._pnlData['data']['loserList']
            data = self._getGainerLoserInfo(lst)
        return data
    
    def _getGainerLoserInfo(self, lst):
        '''
        {'id': 52, 'name': 'XRP', 'symbol': 'XRP', 'slug': 'xrp', 'rank': 4, 'status': 'active', 
        'marketCap': 146476358437.56, 'selfReportedMarketCap': 0.0, 
        'priceChange': {'price': 2.5002717528151344, 'priceChange1h': 0.80336265, 
        'priceChange24h': 4.23461835, 'priceChange7d': 18.86053874, 'priceChange30d': 16.55443812, 
        'volume24h': 11018243006.931831, 'lastUpdate': '2025-05-13T06:54:00.000Z'}, 'isActive': 1}
        '''
        
        data = []
        for eachItem in lst:
            id = eachItem['id']
            symbol = eachItem['symbol']
            rank = eachItem['rank']
            #{'price': 1.5062724062675072, 'priceChange1h': 0.40104849, 'priceChange24h': -8.71662593, 'priceChange7d': 11.3612143, 'priceChange30d': 225.52005718, 'volume24h': 498781775.06415576, 'lastUpdate': '2025-05-07T00:26:00.000Z'}            
            change = eachItem['priceChange']['priceChange24h']  
            price = eachItem['priceChange']['price']
            vol = eachItem['priceChange']['volume24h']  
            slug = eachItem['slug']
            _tmp = {}
            #[id,rank,symbol,change,price,vol,slug]
            _tmp['rank'] = int(rank)
            _tmp['symbol'] = symbol
            _tmp['priceChangePercent'] = float(change)
            _tmp['price'] = float(price)
            _tmp['vol'] = float(vol)
            _tmp['slug'] = slug            
            data.append(_tmp)
            
        return data         
    
    def getCoinSlug(self, coin):
        self._fetchCachedSlug()
        for each in self.nowSlugs:
            if each[0].strip().upper() == coin.strip().upper():
                return each[1]
        self.tls.error(f'CMC Slug not found for {coin}')
        return None        

    @lru_cache    
    def _fetchCachedSlug(self):
        if self.nowSlugs:
            lst = self.nowSlugs
        else:
            cacheName = 'cache_slug'
            if self.tls.isCacheAvailable(cacheName):
                lst = self.tls.getCache(cacheName)
            else:
                lst = self._fetchLiveSlugs()
                self.tls.setCache(cacheName, lst)
            self.nowSlugs = lst

    @lru_cache        
    def _fetchLiveSlugs(self):
        '''
        slug is special name in cmc 
        
        used in 
        url = 'https://coinmarketcap.com/currencies/bitcoin/'
        
        exception - ape alone
        url = 'https://coinmarketcap.com/currencies/apecoin-ape/
        '''        
        murl = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
        lst = []        
        session = Session()
        session.headers.update(headers)
        data = ''
        try:
            self.tls.debug('Calling ' + murl)
            response = session.get(murl)
            data = response.text
            dj = json.loads(data)
            if dj and 'data' in dj:
                for each in dj['data']:
                    symbol = str(unicodedata.normalize('NFKD', each['symbol']).encode('ascii', 'ignore')) 
                    symbol = symbol[2:len(symbol)-1]
                    slug = str(unicodedata.normalize('NFKD', each['slug']).encode('ascii', 'ignore'))
                    slug = slug[2:len(slug)-1]
                    #print(symbol, '---',slug)
                    lst.append((symbol, slug))            
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            self.tls.error(e)
        return lst     

if __name__ == '__main__':
    tls = kTools.GetKTools()    

    obj = CoinMarketCap()
    #
    # tls.info('-------')
    # tls.info("getTopLoser")
    # tls.info('-------')
    # datas = obj.getTopLoser()
    # tls.info(datas)
    # tls.info('-------') 
    #
    # tls.info(datas[0])
    # tls.info('-------')
    #
    # tls.info('-------')
    # tls.info("getTopGainer")
    # tls.info('-------')
    # datas = obj.getTopGainer()
    # tls.info(datas)
    # tls.info('-------') 
    #
    # tls.info(datas[0])
    # tls.info('-------')    

    # tls.info('-------') #
    # tls.info("getMostViewed")
    # tls.info('-------')
    # datas = obj.getMostViewed()
    # tls.info(datas)
    # tls.info('-------') 
    #
    # tls.info(datas[0])
    # tls.info('-------')    
    
    # tls.info('-------') #
    # tls.info("getMostTrending")
    # tls.info('-------')
    # datas = obj.getMostTrending()
    # tls.info(datas)
    # tls.info(len(datas))
    # tls.info('-------') 
    #
    # tls.info(datas[0])
    # tls.info('-------')      


    tls.info('-------') #
    tls.info("getCommunitySentiment")
    tls.info('-------')
    datas = obj.getCommunitySentiment()
    tls.info(datas)
    tls.info(len(datas))
    tls.info('-------') 
    
    tls.info(datas[0])
    tls.info('-------')      






    
    # tls.info('-------')
    # tls.info("getCoinInfo")
    # tls.info('-------')
    # datas = obj.getCoinInfo('LTC')
    # tls.info ( tls.getDictFormatted(datas) )
    # tls.info('-------') 



    # tls.info('-------')
    # tls.info("getTrendStatus")
    # tls.info('-------')
    # datas = obj.getCommunityTrendStatus(1,1)
    # #{'total': '1181', 'trend': '-7.9'}
    # #{'total': '679', 'trend': '-1.5'}
    # #{'total': '678', 'trend': '-1.5'}
    # #{'total': '676', 'trend': '-1.5'}
    # #{'total': '678', 'trend': '-0.1'}
    # tls.info ( tls.getDictFormatted(datas) )
    # tls.info('-------') 


    # tls.info('-------')
    # tls.info("getExchangeVolumeToper")
    # tls.info('-------')
    # datas = obj.getExchangeVolumeToper()
    # #{'total': '1181', 'trend': '-7.9'}
    # #{'total': '679', 'trend': '-1.5'}
    # #{'total': '678', 'trend': '-1.5'}
    # #{'total': '676', 'trend': '-1.5'}
    # #{'total': '678', 'trend': '-0.1'}
    # tls.info ( tls.getDictFormatted(datas) )
    # tls.info('-------') 

    print('done')        