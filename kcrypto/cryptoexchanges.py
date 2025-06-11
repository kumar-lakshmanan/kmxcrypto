'''
Created on 09-Sep-2021

@author: kayma
'''
#-----------------------
import requests
import json

import time
import hmac
import hashlib

from requests import Session
from bs4 import BeautifulSoup
from operator import itemgetter

from urllib.parse import urljoin, urlencode
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

import kTools
##tls = xtools.getGlobalTools()
#codecs.register_error("strict", codecs.ignore_errors)

  
#https://api.coingecko.com/api/v3/exchanges/binance/tickers?depth=cost_to_move_up_usd&order=volume_desc
class Wazrix(object):
    
    
    def __init__(self):
        
        self.tls = xtools.getGlobalTools()
        self.tls.debug('Initializing {0}'.format(self.__class__.__name__))
        
        #'https://api.wazirx.com/api/v2/market-status'
        self.baseurl = 'https://api.wazirx.com/api/v2/'
        self.diffFor = ['inr','usdt','wrx']
        self.marketPriceCache=None
        

    def _urlCall(self, url, headers={}, params={}):
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

    def _composeUrl(self,uri='market-status'):
        return self.baseurl + uri

    def getMarketPrice(self):
        if self.marketPriceCache:
            return self.marketPriceCache
        else:
            url = self._composeUrl('market-status')
            data = self._urlCall(url)   
            self.marketPriceCache = data      
            return self.marketPriceCache
    
    def _coinInfo(self,coinItem):
        sellRate  = coinItem['sell'] #currently selling rate
        buyRate = coinItem['buy'] #currently buying rate
        fee = coinItem['fee']['bid']['maker']
        sellRate = self.tls.precision(sellRate,6) if not '0.00000' in sellRate else float(sellRate)
        buyRate = self.tls.precision(buyRate,6) if not '0.00000' in buyRate else float(buyRate)
        fee = self.tls.precision(fee)
                
        return {'sell':sellRate,'buy':buyRate, 'fee':fee } 
    
    def getCoinInfo(self, forcoin=''):
        data = self.getCoinsInfo(forcoin, multiPair=0, inrMust=0)
        return data[forcoin] if forcoin in data else {}
    
    def getCoinsInfo(self, forcoin='', multiPair=1, inrMust=1):
        coins = {}
        data = self.getMarketPrice()
        markets = data['markets']        
        for eachItem in markets:
            currcoin = eachItem['baseMarket']
            if eachItem['status'] == 'active' and eachItem['type'] == 'SPOT':
                if not currcoin in coins: coins[currcoin] = {}
                pair = eachItem['quoteMarket']
                coins[currcoin][pair] = self._coinInfo(eachItem)

        filterd = {}
        def _filterApply(coin, data):
            filterd[coin] = {}
            filterd[coin] = data
        
        def chkINRMust(coin,data):
            if inrMust:
                if 'inr' in data.keys():
                    _filterApply(coin, data)
            else:
                _filterApply(coin, data)

        def chkFilters(coin, data):
            if multiPair:
                if len(data)>1:
                    chkINRMust(coin,data)
            else:
                chkINRMust(coin,data)
        
        if forcoin:
            data=coins[forcoin]
            chkFilters(forcoin,data)
        else:            
            for coin in coins:
                data=coins[coin]
                chkFilters(coin,data)
                
        return filterd
        
    def getPrice(self, coin, output='inr'):
        rate = 0.0
        data = self.getMarketPrice()
        markets = data['markets']        
        for eachItem in markets:
            if eachItem['baseMarket'] == coin.lower().strip() and eachItem['quoteMarket'] == output and eachItem['status'] == 'active':
                rate = self._coinInfo(eachItem)
                break;
        return rate

class Binance(object):
    '''
    classdocs
    '''

    def __init__(self, api_key='', api_secret=''):
        '''
        Constructor
        '''
        self.tls = xtools.getGlobalTools()
        self.tls.debug('Initializing {0}'.format(self.__class__.__name__))

        self.api_key = api_key if api_key else "lBJRtzGjI5RmogelTcCli1HbR4CplofcHvv6EpHMg6HYSxlwbkrnaQestMF23Uz7"
        self.api_secret = api_secret if api_secret else "IUyCSVwPSvkMJcftpHOXkvO0NRSi3Muj4Ubi7nktbL2nkHMKVAwLbs3ewQkz4co3"
        self.bclient = Client(self.api_key, self.api_secret)
        self.baseurl = 'https://api.binance.com'
        
        self.pairCoin = 'USDT'
        
    def _urlCall(self, url, headers={}, params={}):
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

    def _urlCallPost(self, url, body={}, headers={}, params={}):
        session = Session()
        session.headers.update(headers)
        data = ''
        try:
            self.tls.debug('Calling ' + url)
            response = session.post(url,json=body, params=params)
            data = json.loads(response.text.encode('UTF-8'))
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            self.tls.error(e)
        return data
    
    def getP2PRate(self):
        url = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Content-Length": "500",
            "content-Type": "application/json",
            "Host": "p2p.binance.com",
            "Origin": "https://p2p.binance.com"
        }
        inp = {
          "asset": "USDT",
          "fiat": "INR",
          "merchantCheck": False,
          "page": 1,
          "payTypes": [],
          "publisherType": None,
          "rows": 10,
          "tradeType": "BUY"
        }
        response = requests.post(url, headers=headers, json=inp)
        #print(response.text.encode('UTF-8'))
        resp = json.loads(response.text.encode('UTF-8'))
        data = []
        if resp:
            for each in resp['data']:
                n = each['adv']['price']
                #print(n)                
                n = float(n)
                n = round(n,2)
                data.append(n)
        else:
            data.append(0.0)
        
        ret = 0.0
        takeItem = 5
        if len(data)>=takeItem:
            ret = data[takeItem-1]
        else:
            ret = data[0]
        return ret
    
    def getCoinPrice(self, coin):
        '''
        in usdt
        coin must be in binance (confirm by getting price detail from binance)
        '''
        coin = coin.upper().strip() + self.pairCoin.upper().strip()
        prices = self.bclient.get_all_tickers()
        finprice = ''
        for each in prices:
            name = each['symbol']
            price = each['price']
            if coin == name:
                finprice = price
        if finprice == '':
            self.tls.debug('Requested coin price not found : ' + coin)
            finprice = 0.0
        return float(finprice)
    
    
    
    def _getCustomAPICall(self, input={}):
        '''
        input
            - params
            - needTimestamp
            - needRecvWindow
            - path
        '''
        headers = {'X-MBX-APIKEY': self.api_key}
        timestamp = int(time.time() * 1000)
        params = {}
        if 'params' in input and input['params']:
            for eachKey in input['params']:
                params[eachKey] = input['params'][eachKey]
        if 'needTimestamp' in input and input['needTimestamp']:
            params['timestamp'] = timestamp
        if 'needRecvWindow' in input and input['needRecvWindow']:
            params['recvWindow'] = 5000
        if 'path' in input and input['path']:
            urlPath = input['path']            
        query_string = urlencode(params)
        params['signature'] = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        url = urljoin(self.baseurl, urlPath)
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 200:
            data = r.json()
            return data
            #findata = json.dumps(data, indent=2)
        else:
            tls.error('Error')
            tls.error(r.status_code)
            tls.error(r.json())
            return None
        
        
    def getMyAssets(self):
        
        myassets = {}
        
        alldata = []
        alldata.append(('lockedsaving', self.getMyLockedSavingAccountDetail()))
        alldata.append(('liquidswap',self.getMyLiquiditySwapAccountDetail()))
        alldata.append(('flexidefi',self.getMyFlexibleDefiAccountDetail()))
        alldata.append(('flexisav',self.getMyFlexibleSavingAccountDetail()))
        alldata.append(('spot',self.getMySpotAccountDetail()))
        
        for eachData in alldata:
            srcname = eachData[0]
            srcdata = eachData[1]
            for each in srcdata:
                amt = srcdata[each]                
                if each in myassets:
                    myassets[each] = myassets[each] + amt
                else:
                    myassets[each] = amt
        
        ttl = 0.0
        for asset in myassets:            
            amount = myassets[asset]            
            percoinrate = self.getCoinPrice(asset)
            val = (amount * percoinrate)
            ttl += val 
            #print(asset, amount, val, ttl )                    

        return {'ttl_usd_value': ttl, 'assets': myassets}
        
    
    def getMyLockedSavingAccountDetail(self):
        input = {}
        input['path'] = '/sapi/v1/staking/position'
        input['params'] = {'product': 'STAKING'}
        input['needTimestamp'] = 1
        input['needRecvWindow'] = 1
        
        self.tls.info('Fetching my locked savings...')
        
        rawdata = self._getCustomAPICall(input)
        
        mydata = {}
        for each in rawdata:
            asset = each['asset']
            amount = float(each['amount'])
            if amount > 0.0:            
                if asset in mydata:
                    mydata[asset] = mydata[asset] + amount
                else: 
                    mydata[asset] = amount     
        
        return mydata

    def getMyLiquiditySwapAccountDetail(self):
        input = {}
        input['path'] = '/sapi/v1/bswap/liquidity'
        input['needTimestamp'] = 1
        input['needRecvWindow'] = 0
        
        self.tls.info('Fetching my liquidity swap detail...')
          
        rawdata = self._getCustomAPICall(input)

        mydata = {}
        for each in rawdata:
            assetPair = each['share']['asset']
            for asset in assetPair:
                amount = float(assetPair[asset])
                if amount > 0.0:
                    if asset in mydata:
                        mydata[asset] = mydata[asset] + amount
                    else: 
                        mydata[asset] = amount     
        
        return mydata      
    
    def getMyFlexibleDefiAccountDetail(self):
        input = {}
        input['path'] = '/sapi/v1/staking/position'
        input['params'] = {'product': 'F_DEFI'}
        input['needTimestamp'] = 1
        input['needRecvWindow'] = 1
        
        self.tls.info('Fetching my flexible defi detail...')
        
        rawdata = self._getCustomAPICall(input)

        mydata = {}
        for each in rawdata:
            asset = each['asset']
            amount = float(each['amount'])
            if amount > 0.0:            
                if asset in mydata:
                    mydata[asset] = mydata[asset] + amount
                else: 
                    mydata[asset] = amount     
        
        return mydata         

    def getMyFlexibleSavingAccountDetail(self):
        input = {}
        input['path'] = '/sapi/v1/lending/daily/token/position'
        input['needTimestamp'] = 1
        input['needRecvWindow'] = 0
        
        self.tls.info('Fetching my flexible saving detail...')
        
        rawdata = self._getCustomAPICall(input)
        
        mydata = {}
        for each in rawdata:
            asset = each['asset']
            amount = float(each['totalAmount'])
            if amount > 0.0:            
                if asset in mydata:
                    mydata[asset] = mydata[asset] + amount
                else: 
                    mydata[asset] = amount     
        
        return mydata       
    
    def getMySpotAccountDetail(self):
        
        # info = self.bclient.get_account_snapshot(type='SPOT')
        # data= info['snapshotVos']
        # print(data)
        
        rawdata = self.bclient.get_account()['balances']
        
        self.tls.info('Fetching my spot balance...')
        
        mydata = {}
        for each in rawdata:
            asset = each['asset']
            amount = float(each['free'])
            if amount > 0.0:
                if asset in mydata:
                    mydata[asset] = mydata[asset] + amount
                else: 
                    mydata[asset] = amount
                      
        return mydata                                      
                
        
        #[{'type': 'spot', 'updateTime': 1679788799000, 'data': {'totalAssetOfBtc': '0.000064', 'balances': [{'asset': 'ADA', 'free': '0.09340039', 'locked': '0'}, {'asset': 'ALGO', 'free': '0', 'locked': '0'}, {'asset': 'ANKR', 'free': '0', 'locked': '0'}, {'asset': 'AR', 'free': '0', 'locked': '0'}, {'asset': 'ARPA', 'free': '0', 'locked': '0'}, {'asset': 'ATOM', 'free': '0.02109688', 'locked': '0'}, {'asset': 'AUDIO', 'free': '0', 'locked': '0'}, {'asset': 'AVAX', 'free': '0', 'locked': '0'}, {'asset': 'AXS', 'free': '0', 'locked': '0'}, {'asset': 'BAL', 'free': '0', 'locked': '0'}, {'asset': 'BAND', 'free': '0', 'locked': '0'}, {'asset': 'BAT', 'free': '0', 'locked': '0'}, {'asset': 'BEL', 'free': '0', 'locked': '0'}, {'asset': 'BETH', 'free': '0', 'locked': '0'}, {'asset': 'BLZ', 'free': '0', 'locked': '0'}, {'asset': 'BNB', 'free': '0.0003346', 'locked': '0'}, {'asset': 'BTC', 'free': '0', 'locked': '0'}, {'asset': 'BTT', 'free': '0', 'locked': '0'}, {'asset': 'BZRX', 'free': '0', 'locked': '0'}, {'asset': 'CELO', 'free': '0', 'locked': '0'}, {'asset': 'CELR', 'free': '0', 'locked': '0'}, {'asset': 'CFX', 'free': '0', 'locked': '0'}, {'asset': 'CHR', 'free': '0', 'locked': '0'}, {'asset': 'CHZ', 'free': '0', 'locked': '0'}, {'asset': 'COMP', 'free': '0', 'locked': '0'}, {'asset': 'DASH', 'free': '0', 'locked': '0'}, {'asset': 'DATA', 'free': '0', 'locked': '0'}, {'asset': 'DNT', 'free': '0', 'locked': '0'}, {'asset': 'DOGE', 'free': '0', 'locked': '0'}, {'asset': 'EGLD', 'free': '0.00578466', 'locked': '0'}, {'asset': 'EOS', 'free': '0.0117246', 'locked': '0'}, {'asset': 'ETH', 'free': '0', 'locked': '0'}, {'asset': 'ETHW', 'free': '0.10354775', 'locked': '0'}, {'asset': 'FOR', 'free': '0', 'locked': '0'}, {'asset': 'FTT', 'free': '0', 'locked': '0'}, {'asset': 'GALA', 'free': '0', 'locked': '0'}, {'asset': 'GRT', 'free': '0', 'locked': '0'}, {'asset': 'ICP', 'free': '0.02157411', 'locked': '0'}, {'asset': 'IOTX', 'free': '0', 'locked': '0'}, {'asset': 'JST', 'free': '0', 'locked': '0'}, {'asset': 'KEEP', 'free': '0', 'locked': '0'}, {'asset': 'LAZIO', 'free': '0', 'locked': '0'}, {'asset': 'LDADA', 'free': '0', 'locked': '0'}, {'asset': 'LDATOM', 'free': '0', 'locked': '0'}, {'asset': 'LDBTC', 'free': '0.01136555', 'locked': '0'}, {'asset': 'LDCHZ', 'free': '0.01841119', 'locked': '0'}, {'asset': 'LDEOS', 'free': '0', 'locked': '0'}, {'asset': 'LDERD', 'free': '0', 'locked': '0'}, {'asset': 'LDETH', 'free': '0.05072369', 'locked': '0'}, {'asset': 'LDGALA', 'free': '373.64184596', 'locked': '0'}, {'asset': 'LDICP', 'free': '0', 'locked': '0'}, {'asset': 'LDLAZIO', 'free': '0.08379923', 'locked': '0'}, {'asset': 'LDLINK', 'free': '0.01187067', 'locked': '0'}, {'asset': 'LDMATIC', 'free': '0', 'locked': '0'}, {'asset': 'LDSAND', 'free': '29.30011035', 'locked': '0'}, {'asset': 'LDSHIB2', 'free': '0', 'locked': '0'}, {'asset': 'LDSOL', 'free': '0', 'locked': '0'}, {'asset': 'LDTHETA', 'free': '0', 'locked': '0'}, {'asset': 'LDUSDT', 'free': '171.53685235', 'locked': '0'}, {'asset': 'LDVET', 'free': '111.13932981', 'locked': '0'}, {'asset': 'LDVTHO', 'free': '129.26260356', 'locked': '0'}, {'asset': 'LDWRX', 'free': '9.07671439', 'locked': '0'}, {'asset': 'LDXEC', 'free': '139405.18', 'locked': '0'}, {'asset': 'LDXMR', 'free': '0.10254661', 'locked': '0'}, {'asset': 'LDXRP', 'free': '326.68010271', 'locked': '0'}, {'asset': 'LDXTZ', 'free': '0', 'locked': '0'}, {'asset': 'LDZIL', 'free': '0', 'locked': '0'}, {'asset': 'LINK', 'free': '0', 'locked': '0'}, {'asset': 'LPT', 'free': '0', 'locked': '0'}, {'asset': 'LRC', 'free': '0', 'locked': '0'}, {'asset': 'LUNA', 'free': '0', 'locked': '0'}, {'asset': 'MANA', 'free': '0', 'locked': '0'}, {'asset': 'MATIC', 'free': '0.21055773', 'locked': '0'}, {'asset': 'NEAR', 'free': '0', 'locked': '0'}, {'asset': 'OMG', 'free': '0', 'locked': '0'}, {'asset': 'ONE', 'free': '0', 'locked': '0'}, {'asset': 'ORN', 'free': '0', 'locked': '0'}, {'asset': 'QNT', 'free': '0', 'locked': '0'}, {'asset': 'RSR', 'free': '0', 'locked': '0'}, {'asset': 'SAND', 'free': '0', 'locked': '0'}, {'asset': 'SHIB', 'free': '5683112', 'locked': '0'}, {'asset': 'SOL', 'free': '0.00119279', 'locked': '0'}, {'asset': 'SOLO', 'free': '1.71553587', 'locked': '0'}, {'asset': 'STMX', 'free': '0', 'locked': '0'}, {'asset': 'STX', 'free': '0', 'locked': '0'}, {'asset': 'THETA', 'free': '0.06294829', 'locked': '0'}, {'asset': 'TRX', 'free': '0', 'locked': '0'}, {'asset': 'UNFI', 'free': '0', 'locked': '0'}, {'asset': 'USDT', 'free': '0', 'locked': '0'}, {'asset': 'VET', 'free': '0', 'locked': '0'}, {'asset': 'VTHO', 'free': '0', 'locked': '0'}, {'asset': 'WRX', 'free': '0', 'locked': '0'}, {'asset': 'XEC', 'free': '0', 'locked': '0'}, {'asset': 'XMR', 'free': '0', 'locked': '0'}, {'asset': 'XRP', 'free': '0', 'locked': '0'}, {'asset': 'XTZ', 'free': '0.02392243', 'locked': '0'}, {'asset': 'ZEC', 'free': '0', 'locked': '0'}, {'asset': 'ZIL', 'free': '1.07491072', 'locked': '0'}]}}, {'type': 'spot', 'updateTime': 1679875199000, 'data': {'totalAssetOfBtc': '0.00006462', 'balances': [{'asset': 'ADA', 'free': '0.09747556', 'locked': '0'}, {'asset': 'ALGO', 'free': '0', 'locked': '0'}, {'asset': 'ANKR', 'free': '0', 'locked': '0'}, {'asset': 'AR', 'free': '0', 'locked': '0'}, {'asset': 'ARPA', 'free': '0', 'locked': '0'}, {'asset': 'ATOM', 'free': '0.02201473', 'locked': '0'}, {'asset': 'AUDIO', 'free': '0', 'locked': '0'}, {'asset': 'AVAX', 'free': '0', 'locked': '0'}, {'asset': 'AXS', 'free': '0', 'locked': '0'}, {'asset': 'BAL', 'free': '0', 'locked': '0'}, {'asset': 'BAND', 'free': '0', 'locked': '0'}, {'asset': 'BAT', 'free': '0', 'locked': '0'}, {'asset': 'BEL', 'free': '0', 'locked': '0'}, {'asset': 'BETH', 'free': '0', 'locked': '0'}, {'asset': 'BLZ', 'free': '0', 'locked': '0'}, {'asset': 'BNB', 'free': '0.00033877', 'locked': '0'}, {'asset': 'BTC', 'free': '0', 'locked': '0'}, {'asset': 'BTT', 'free': '0', 'locked': '0'}, {'asset': 'BZRX', 'free': '0', 'locked': '0'}, {'asset': 'CELO', 'free': '0', 'locked': '0'}, {'asset': 'CELR', 'free': '0', 'locked': '0'}, {'asset': 'CFX', 'free': '0', 'locked': '0'}, {'asset': 'CHR', 'free': '0', 'locked': '0'}, {'asset': 'CHZ', 'free': '0', 'locked': '0'}, {'asset': 'COMP', 'free': '0', 'locked': '0'}, {'asset': 'DASH', 'free': '0', 'locked': '0'}, {'asset': 'DATA', 'free': '0', 'locked': '0'}, {'asset': 'DNT', 'free': '0', 'locked': '0'}, {'asset': 'DOGE', 'free': '0', 'locked': '0'}, {'asset': 'EGLD', 'free': '0.005818', 'locked': '0'}, {'asset': 'EOS', 'free': '0.0122345', 'locked': '0'}, {'asset': 'ETH', 'free': '0', 'locked': '0'}, {'asset': 'ETHW', 'free': '0.10354775', 'locked': '0'}, {'asset': 'FOR', 'free': '0', 'locked': '0'}, {'asset': 'FTT', 'free': '0', 'locked': '0'}, {'asset': 'GALA', 'free': '0', 'locked': '0'}, {'asset': 'GRT', 'free': '0', 'locked': '0'}, {'asset': 'ICP', 'free': '0.02160884', 'locked': '0'}, {'asset': 'IOTX', 'free': '0', 'locked': '0'}, {'asset': 'JST', 'free': '0', 'locked': '0'}, {'asset': 'KEEP', 'free': '0', 'locked': '0'}, {'asset': 'LAZIO', 'free': '0', 'locked': '0'}, {'asset': 'LDADA', 'free': '0', 'locked': '0'}, {'asset': 'LDATOM', 'free': '0', 'locked': '0'}, {'asset': 'LDBTC', 'free': '0.01136561', 'locked': '0'}, {'asset': 'LDCHZ', 'free': '0.01841119', 'locked': '0'}, {'asset': 'LDEOS', 'free': '0', 'locked': '0'}, {'asset': 'LDERD', 'free': '0', 'locked': '0'}, {'asset': 'LDETH', 'free': '0.05072403', 'locked': '0'}, {'asset': 'LDGALA', 'free': '373.64184596', 'locked': '0'}, {'asset': 'LDICP', 'free': '0', 'locked': '0'}, {'asset': 'LDLAZIO', 'free': '0.08379923', 'locked': '0'}, {'asset': 'LDLINK', 'free': '0.01187538', 'locked': '0'}, {'asset': 'LDMATIC', 'free': '0', 'locked': '0'}, {'asset': 'LDSAND', 'free': '29.30044163', 'locked': '0'}, {'asset': 'LDSHIB2', 'free': '0', 'locked': '0'}, {'asset': 'LDSOL', 'free': '0', 'locked': '0'}, {'asset': 'LDTHETA', 'free': '0', 'locked': '0'}, {'asset': 'LDUSDT', 'free': '171.54447655', 'locked': '0'}, {'asset': 'LDVET', 'free': '111.13932981', 'locked': '0'}, {'asset': 'LDVTHO', 'free': '129.29548445', 'locked': '0'}, {'asset': 'LDWRX', 'free': '9.07671439', 'locked': '0'}, {'asset': 'LDXEC', 'free': '139405.18', 'locked': '0'}, {'asset': 'LDXMR', 'free': '0.10254661', 'locked': '0'}, {'asset': 'LDXRP', 'free': '326.6803891', 'locked': '0'}, {'asset': 'LDXTZ', 'free': '0', 'locked': '0'}, {'asset': 'LDZIL', 'free': '0', 'locked': '0'}, {'asset': 'LINK', 'free': '0', 'locked': '0'}, {'asset': 'LPT', 'free': '0', 'locked': '0'}, {'asset': 'LRC', 'free': '0', 'locked': '0'}, {'asset': 'LUNA', 'free': '0', 'locked': '0'}, {'asset': 'MANA', 'free': '0', 'locked': '0'}, {'asset': 'MATIC', 'free': '0.22041779', 'locked': '0'}, {'asset': 'NEAR', 'free': '0', 'locked': '0'}, {'asset': 'OMG', 'free': '0', 'locked': '0'}, {'asset': 'ONE', 'free': '0', 'locked': '0'}, {'asset': 'ORN', 'free': '0', 'locked': '0'}, {'asset': 'QNT', 'free': '0', 'locked': '0'}, {'asset': 'RSR', 'free': '0', 'locked': '0'}, {'asset': 'SAND', 'free': '0', 'locked': '0'}, {'asset': 'SHIB', 'free': '5683119.23', 'locked': '0'}, {'asset': 'SOL', 'free': '0.00121823', 'locked': '0'}, {'asset': 'SOLO', 'free': '1.71553587', 'locked': '0'}, {'asset': 'STMX', 'free': '0', 'locked': '0'}, {'asset': 'STX', 'free': '0', 'locked': '0'}, {'asset': 'THETA', 'free': '0.06320812', 'locked': '0'}, {'asset': 'TRX', 'free': '0', 'locked': '0'}, {'asset': 'UNFI', 'free': '0', 'locked': '0'}, {'asset': 'USDT', 'free': '0', 'locked': '0'}, {'asset': 'VET', 'free': '0', 'locked': '0'}, {'asset': 'VTHO', 'free': '0', 'locked': '0'}, {'asset': 'WRX', 'free': '0', 'locked': '0'}, {'asset': 'XEC', 'free': '0', 'locked': '0'}, {'asset': 'XMR', 'free': '0', 'locked': '0'}, {'asset': 'XRP', 'free': '0', 'locked': '0'}, {'asset': 'XTZ', 'free': '0.02488566', 'locked': '0'}, {'asset': 'ZEC', 'free': '0', 'locked': '0'}, {'asset': 'ZIL', 'free': '1.12167068', 'locked': '0'}]}}, {'type': 'spot', 'updateTime': 1679961599000, 'data': {'totalAssetOfBtc': '0.00006526', 'balances': [{'asset': 'ADA', 'free': '0.10155073', 'locked': '0'}, {'asset': 'ALGO', 'free': '0', 'locked': '0'}, {'asset': 'ANKR', 'free': '0', 'locked': '0'}, {'asset': 'AR', 'free': '0', 'locked': '0'}, {'asset': 'ARPA', 'free': '0', 'locked': '0'}, {'asset': 'ATOM', 'free': '0.02293258', 'locked': '0'}, {'asset': 'AUDIO', 'free': '0', 'locked': '0'}, {'asset': 'AVAX', 'free': '0', 'locked': '0'}, {'asset': 'AXS', 'free': '0', 'locked': '0'}, {'asset': 'BAL', 'free': '0', 'locked': '0'}, {'asset': 'BAND', 'free': '0', 'locked': '0'}, {'asset': 'BAT', 'free': '0', 'locked': '0'}, {'asset': 'BEL', 'free': '0', 'locked': '0'}, {'asset': 'BETH', 'free': '0', 'locked': '0'}, {'asset': 'BLZ', 'free': '0', 'locked': '0'}, {'asset': 'BNB', 'free': '0.00034294', 'locked': '0'}, {'asset': 'BTC', 'free': '0', 'locked': '0'}, {'asset': 'BTT', 'free': '0', 'locked': '0'}, {'asset': 'BZRX', 'free': '0', 'locked': '0'}, {'asset': 'CELO', 'free': '0', 'locked': '0'}, {'asset': 'CELR', 'free': '0', 'locked': '0'}, {'asset': 'CFX', 'free': '0', 'locked': '0'}, {'asset': 'CHR', 'free': '0', 'locked': '0'}, {'asset': 'CHZ', 'free': '0', 'locked': '0'}, {'asset': 'COMP', 'free': '0', 'locked': '0'}, {'asset': 'DASH', 'free': '0', 'locked': '0'}, {'asset': 'DATA', 'free': '0', 'locked': '0'}, {'asset': 'DNT', 'free': '0', 'locked': '0'}, {'asset': 'DOGE', 'free': '0', 'locked': '0'}, {'asset': 'EGLD', 'free': '0.00585134', 'locked': '0'}, {'asset': 'EOS', 'free': '0.0127444', 'locked': '0'}, {'asset': 'ETH', 'free': '0', 'locked': '0'}, {'asset': 'ETHW', 'free': '0.10354775', 'locked': '0'}, {'asset': 'FOR', 'free': '0', 'locked': '0'}, {'asset': 'FTT', 'free': '0', 'locked': '0'}, {'asset': 'GALA', 'free': '0', 'locked': '0'}, {'asset': 'GRT', 'free': '0', 'locked': '0'}, {'asset': 'ICP', 'free': '0.02164357', 'locked': '0'}, {'asset': 'IOTX', 'free': '0', 'locked': '0'}, {'asset': 'JST', 'free': '0', 'locked': '0'}, {'asset': 'KEEP', 'free': '0', 'locked': '0'}, {'asset': 'LAZIO', 'free': '0', 'locked': '0'}, {'asset': 'LDADA', 'free': '0', 'locked': '0'}, {'asset': 'LDATOM', 'free': '0', 'locked': '0'}, {'asset': 'LDBTC', 'free': '0.01136567', 'locked': '0'}, {'asset': 'LDCHZ', 'free': '0.01841119', 'locked': '0'}, {'asset': 'LDEOS', 'free': '0', 'locked': '0'}, {'asset': 'LDERD', 'free': '0', 'locked': '0'}, {'asset': 'LDETH', 'free': '0.05072437', 'locked': '0'}, {'asset': 'LDGALA', 'free': '373.64184596', 'locked': '0'}, {'asset': 'LDICP', 'free': '0', 'locked': '0'}, {'asset': 'LDLAZIO', 'free': '0.08379923', 'locked': '0'}, {'asset': 'LDLINK', 'free': '0.01188009', 'locked': '0'}, {'asset': 'LDMATIC', 'free': '0', 'locked': '0'}, {'asset': 'LDSAND', 'free': '29.3007729', 'locked': '0'}, {'asset': 'LDSHIB2', 'free': '0', 'locked': '0'}, {'asset': 'LDSOL', 'free': '0', 'locked': '0'}, {'asset': 'LDTHETA', 'free': '0', 'locked': '0'}, {'asset': 'LDUSDT', 'free': '171.55210079', 'locked': '0'}, {'asset': 'LDVET', 'free': '111.13932981', 'locked': '0'}, {'asset': 'LDVTHO', 'free': '129.32816134', 'locked': '0'}, {'asset': 'LDWRX', 'free': '9.07671439', 'locked': '0'}, {'asset': 'LDXEC', 'free': '139405.18', 'locked': '0'}, {'asset': 'LDXMR', 'free': '0.10254661', 'locked': '0'}, {'asset': 'LDXRP', 'free': '326.68067546', 'locked': '0'}, {'asset': 'LDXTZ', 'free': '0', 'locked': '0'}, {'asset': 'LDZIL', 'free': '0', 'locked': '0'}, {'asset': 'LINK', 'free': '0', 'locked': '0'}, {'asset': 'LPT', 'free': '0', 'locked': '0'}, {'asset': 'LRC', 'free': '0', 'locked': '0'}, {'asset': 'LUNA', 'free': '0', 'locked': '0'}, {'asset': 'MANA', 'free': '0', 'locked': '0'}, {'asset': 'MATIC', 'free': '0.23027785', 'locked': '0'}, {'asset': 'NEAR', 'free': '0', 'locked': '0'}, {'asset': 'OMG', 'free': '0', 'locked': '0'}, {'asset': 'ONE', 'free': '0', 'locked': '0'}, {'asset': 'ORN', 'free': '0', 'locked': '0'}, {'asset': 'QNT', 'free': '0', 'locked': '0'}, {'asset': 'RSR', 'free': '0', 'locked': '0'}, {'asset': 'SAND', 'free': '0', 'locked': '0'}, {'asset': 'SHIB', 'free': '5683126.46', 'locked': '0'}, {'asset': 'SOL', 'free': '0.00124367', 'locked': '0'}, {'asset': 'SOLO', 'free': '1.71553587', 'locked': '0'}, {'asset': 'STMX', 'free': '0', 'locked': '0'}, {'asset': 'STX', 'free': '0', 'locked': '0'}, {'asset': 'THETA', 'free': '0.06346795', 'locked': '0'}, {'asset': 'TRX', 'free': '0', 'locked': '0'}, {'asset': 'UNFI', 'free': '0', 'locked': '0'}, {'asset': 'USDT', 'free': '0', 'locked': '0'}, {'asset': 'VET', 'free': '0', 'locked': '0'}, {'asset': 'VTHO', 'free': '0', 'locked': '0'}, {'asset': 'WRX', 'free': '0', 'locked': '0'}, {'asset': 'XEC', 'free': '0', 'locked': '0'}, {'asset': 'XMR', 'free': '0', 'locked': '0'}, {'asset': 'XRP', 'free': '0', 'locked': '0'}, {'asset': 'XTZ', 'free': '0.02584889', 'locked': '0'}, {'asset': 'ZEC', 'free': '0', 'locked': '0'}, {'asset': 'ZIL', 'free': '1.16843064', 'locked': '0'}]}}, {'type': 'spot', 'updateTime': 1680047999000, 'data': {'totalAssetOfBtc': '0.0000672', 'balances': [{'asset': 'ADA', 'free': '0.1056259', 'locked': '0'}, {'asset': 'ALGO', 'free': '0', 'locked': '0'}, {'asset': 'ANKR', 'free': '0', 'locked': '0'}, {'asset': 'AR', 'free': '0', 'locked': '0'}, {'asset': 'ARPA', 'free': '0', 'locked': '0'}, {'asset': 'ATOM', 'free': '0.02385043', 'locked': '0'}, {'asset': 'AUDIO', 'free': '0', 'locked': '0'}, {'asset': 'AVAX', 'free': '0', 'locked': '0'}, {'asset': 'AXS', 'free': '0', 'locked': '0'}, {'asset': 'BAL', 'free': '0', 'locked': '0'}, {'asset': 'BAND', 'free': '0', 'locked': '0'}, {'asset': 'BAT', 'free': '0', 'locked': '0'}, {'asset': 'BEL', 'free': '0', 'locked': '0'}, {'asset': 'BETH', 'free': '0', 'locked': '0'}, {'asset': 'BLZ', 'free': '0', 'locked': '0'}, {'asset': 'BNB', 'free': '0.00034711', 'locked': '0'}, {'asset': 'BTC', 'free': '0', 'locked': '0'}, {'asset': 'BTT', 'free': '0', 'locked': '0'}, {'asset': 'BZRX', 'free': '0', 'locked': '0'}, {'asset': 'CELO', 'free': '0', 'locked': '0'}, {'asset': 'CELR', 'free': '0', 'locked': '0'}, {'asset': 'CFX', 'free': '0', 'locked': '0'}, {'asset': 'CHR', 'free': '0', 'locked': '0'}, {'asset': 'CHZ', 'free': '0', 'locked': '0'}, {'asset': 'COMP', 'free': '0', 'locked': '0'}, {'asset': 'DASH', 'free': '0', 'locked': '0'}, {'asset': 'DATA', 'free': '0', 'locked': '0'}, {'asset': 'DNT', 'free': '0', 'locked': '0'}, {'asset': 'DOGE', 'free': '0', 'locked': '0'}, {'asset': 'EGLD', 'free': '0.00588468', 'locked': '0'}, {'asset': 'EOS', 'free': '0.0132543', 'locked': '0'}, {'asset': 'ETH', 'free': '0', 'locked': '0'}, {'asset': 'ETHW', 'free': '0.10354775', 'locked': '0'}, {'asset': 'FOR', 'free': '0', 'locked': '0'}, {'asset': 'FTT', 'free': '0', 'locked': '0'}, {'asset': 'GALA', 'free': '0', 'locked': '0'}, {'asset': 'GRT', 'free': '0', 'locked': '0'}, {'asset': 'ICP', 'free': '0.0216783', 'locked': '0'}, {'asset': 'IOTX', 'free': '0', 'locked': '0'}, {'asset': 'JST', 'free': '0', 'locked': '0'}, {'asset': 'KEEP', 'free': '0', 'locked': '0'}, {'asset': 'LAZIO', 'free': '0', 'locked': '0'}, {'asset': 'LDADA', 'free': '0', 'locked': '0'}, {'asset': 'LDATOM', 'free': '0', 'locked': '0'}, {'asset': 'LDBTC', 'free': '0.01136573', 'locked': '0'}, {'asset': 'LDCHZ', 'free': '0.01841119', 'locked': '0'}, {'asset': 'LDEOS', 'free': '0', 'locked': '0'}, {'asset': 'LDERD', 'free': '0', 'locked': '0'}, {'asset': 'LDETH', 'free': '0.05072471', 'locked': '0'}, {'asset': 'LDGALA', 'free': '373.64184596', 'locked': '0'}, {'asset': 'LDICP', 'free': '0', 'locked': '0'}, {'asset': 'LDLAZIO', 'free': '0.08379923', 'locked': '0'}, {'asset': 'LDLINK', 'free': '0.0118848', 'locked': '0'}, {'asset': 'LDMATIC', 'free': '0', 'locked': '0'}, {'asset': 'LDSAND', 'free': '29.30110416', 'locked': '0'}, {'asset': 'LDSHIB2', 'free': '0', 'locked': '0'}, {'asset': 'LDSOL', 'free': '0', 'locked': '0'}, {'asset': 'LDTHETA', 'free': '0', 'locked': '0'}, {'asset': 'LDUSDT', 'free': '171.55972557', 'locked': '0'}, {'asset': 'LDVET', 'free': '111.13932981', 'locked': '0'}, {'asset': 'LDVTHO', 'free': '129.36065627', 'locked': '0'}, {'asset': 'LDWRX', 'free': '9.07671439', 'locked': '0'}, {'asset': 'LDXEC', 'free': '139405.18', 'locked': '0'}, {'asset': 'LDXMR', 'free': '0.10254661', 'locked': '0'}, {'asset': 'LDXRP', 'free': '326.68096177', 'locked': '0'}, {'asset': 'LDXTZ', 'free': '0', 'locked': '0'}, {'asset': 'LDZIL', 'free': '0', 'locked': '0'}, {'asset': 'LINK', 'free': '0', 'locked': '0'}, {'asset': 'LPT', 'free': '0', 'locked': '0'}, {'asset': 'LRC', 'free': '0', 'locked': '0'}, {'asset': 'LUNA', 'free': '0', 'locked': '0'}, {'asset': 'MANA', 'free': '0', 'locked': '0'}, {'asset': 'MATIC', 'free': '0.24013791', 'locked': '0'}, {'asset': 'NEAR', 'free': '0', 'locked': '0'}, {'asset': 'OMG', 'free': '0', 'locked': '0'}, {'asset': 'ONE', 'free': '0', 'locked': '0'}, {'asset': 'ORN', 'free': '0', 'locked': '0'}, {'asset': 'QNT', 'free': '0', 'locked': '0'}, {'asset': 'RSR', 'free': '0', 'locked': '0'}, {'asset': 'SAND', 'free': '0', 'locked': '0'}, {'asset': 'SHIB', 'free': '5683133.69', 'locked': '0'}, {'asset': 'SOL', 'free': '0.00126911', 'locked': '0'}, {'asset': 'SOLO', 'free': '1.71553587', 'locked': '0'}, {'asset': 'STMX', 'free': '0', 'locked': '0'}, {'asset': 'STX', 'free': '0', 'locked': '0'}, {'asset': 'THETA', 'free': '0.06372778', 'locked': '0'}, {'asset': 'TRX', 'free': '0', 'locked': '0'}, {'asset': 'UNFI', 'free': '0', 'locked': '0'}, {'asset': 'USDT', 'free': '0', 'locked': '0'}, {'asset': 'VET', 'free': '0', 'locked': '0'}, {'asset': 'VTHO', 'free': '0', 'locked': '0'}, {'asset': 'WRX', 'free': '0', 'locked': '0'}, {'asset': 'XEC', 'free': '0', 'locked': '0'}, {'asset': 'XMR', 'free': '0', 'locked': '0'}, {'asset': 'XRP', 'free': '0', 'locked': '0'}, {'asset': 'XTZ', 'free': '0.02681212', 'locked': '0'}, {'asset': 'ZEC', 'free': '0', 'locked': '0'}, {'asset': 'ZIL', 'free': '1.2151906', 'locked': '0'}]}}, {'type': 'spot', 'updateTime': 1680134399000, 'data': {'totalAssetOfBtc': '0.00006751', 'balances': [{'asset': 'ADA', 'free': '0.10970107', 'locked': '0'}, {'asset': 'ALGO', 'free': '0', 'locked': '0'}, {'asset': 'ANKR', 'free': '0', 'locked': '0'}, {'asset': 'AR', 'free': '0', 'locked': '0'}, {'asset': 'ARPA', 'free': '0', 'locked': '0'}, {'asset': 'ATOM', 'free': '0.02476828', 'locked': '0'}, {'asset': 'AUDIO', 'free': '0', 'locked': '0'}, {'asset': 'AVAX', 'free': '0', 'locked': '0'}, {'asset': 'AXS', 'free': '0', 'locked': '0'}, {'asset': 'BAL', 'free': '0', 'locked': '0'}, {'asset': 'BAND', 'free': '0', 'locked': '0'}, {'asset': 'BAT', 'free': '0', 'locked': '0'}, {'asset': 'BEL', 'free': '0', 'locked': '0'}, {'asset': 'BETH', 'free': '0', 'locked': '0'}, {'asset': 'BLZ', 'free': '0', 'locked': '0'}, {'asset': 'BNB', 'free': '0.00035128', 'locked': '0'}, {'asset': 'BTC', 'free': '0', 'locked': '0'}, {'asset': 'BTT', 'free': '0', 'locked': '0'}, {'asset': 'BZRX', 'free': '0', 'locked': '0'}, {'asset': 'CELO', 'free': '0', 'locked': '0'}, {'asset': 'CELR', 'free': '0', 'locked': '0'}, {'asset': 'CFX', 'free': '0', 'locked': '0'}, {'asset': 'CHR', 'free': '0', 'locked': '0'}, {'asset': 'CHZ', 'free': '0', 'locked': '0'}, {'asset': 'COMP', 'free': '0', 'locked': '0'}, {'asset': 'DASH', 'free': '0', 'locked': '0'}, {'asset': 'DATA', 'free': '0', 'locked': '0'}, {'asset': 'DNT', 'free': '0', 'locked': '0'}, {'asset': 'DOGE', 'free': '0', 'locked': '0'}, {'asset': 'EGLD', 'free': '0.00591802', 'locked': '0'}, {'asset': 'EOS', 'free': '0.0137642', 'locked': '0'}, {'asset': 'ETH', 'free': '0', 'locked': '0'}, {'asset': 'ETHW', 'free': '0.10354775', 'locked': '0'}, {'asset': 'FOR', 'free': '0', 'locked': '0'}, {'asset': 'FTT', 'free': '0', 'locked': '0'}, {'asset': 'GALA', 'free': '0', 'locked': '0'}, {'asset': 'GRT', 'free': '0', 'locked': '0'}, {'asset': 'ICP', 'free': '0.02171303', 'locked': '0'}, {'asset': 'IOTX', 'free': '0', 'locked': '0'}, {'asset': 'JST', 'free': '0', 'locked': '0'}, {'asset': 'KEEP', 'free': '0', 'locked': '0'}, {'asset': 'LAZIO', 'free': '0', 'locked': '0'}, {'asset': 'LDADA', 'free': '0', 'locked': '0'}, {'asset': 'LDATOM', 'free': '0', 'locked': '0'}, {'asset': 'LDBTC', 'free': '0.01136579', 'locked': '0'}, {'asset': 'LDCHZ', 'free': '0.01841119', 'locked': '0'}, {'asset': 'LDEOS', 'free': '0', 'locked': '0'}, {'asset': 'LDERD', 'free': '0', 'locked': '0'}, {'asset': 'LDETH', 'free': '0.05072505', 'locked': '0'}, {'asset': 'LDGALA', 'free': '373.64184596', 'locked': '0'}, {'asset': 'LDICP', 'free': '0', 'locked': '0'}, {'asset': 'LDLAZIO', 'free': '0.08379923', 'locked': '0'}, {'asset': 'LDLINK', 'free': '0.01188951', 'locked': '0'}, {'asset': 'LDMATIC', 'free': '0', 'locked': '0'}, {'asset': 'LDSAND', 'free': '29.30143541', 'locked': '0'}, {'asset': 'LDSHIB2', 'free': '0', 'locked': '0'}, {'asset': 'LDSOL', 'free': '0', 'locked': '0'}, {'asset': 'LDTHETA', 'free': '0', 'locked': '0'}, {'asset': 'LDUSDT', 'free': '171.56735061', 'locked': '0'}, {'asset': 'LDVET', 'free': '111.13932981', 'locked': '0'}, {'asset': 'LDVTHO', 'free': '129.39308861', 'locked': '0'}, {'asset': 'LDWRX', 'free': '9.07671439', 'locked': '0'}, {'asset': 'LDXEC', 'free': '139405.18', 'locked': '0'}, {'asset': 'LDXMR', 'free': '0.10254661', 'locked': '0'}, {'asset': 'LDXRP', 'free': '326.68124807', 'locked': '0'}, {'asset': 'LDXTZ', 'free': '0', 'locked': '0'}, {'asset': 'LDZIL', 'free': '0', 'locked': '0'}, {'asset': 'LINK', 'free': '0', 'locked': '0'}, {'asset': 'LPT', 'free': '0', 'locked': '0'}, {'asset': 'LRC', 'free': '0', 'locked': '0'}, {'asset': 'LUNA', 'free': '0', 'locked': '0'}, {'asset': 'MANA', 'free': '0', 'locked': '0'}, {'asset': 'MATIC', 'free': '0.24999797', 'locked': '0'}, {'asset': 'NEAR', 'free': '0', 'locked': '0'}, {'asset': 'OMG', 'free': '0', 'locked': '0'}, {'asset': 'ONE', 'free': '0', 'locked': '0'}, {'asset': 'ORN', 'free': '0', 'locked': '0'}, {'asset': 'QNT', 'free': '0', 'locked': '0'}, {'asset': 'RSR', 'free': '0', 'locked': '0'}, {'asset': 'SAND', 'free': '0', 'locked': '0'}, {'asset': 'SHIB', 'free': '5683140.92', 'locked': '0'}, {'asset': 'SOL', 'free': '0.00129455', 'locked': '0'}, {'asset': 'SOLO', 'free': '1.71553587', 'locked': '0'}, {'asset': 'STMX', 'free': '0', 'locked': '0'}, {'asset': 'STX', 'free': '0', 'locked': '0'}, {'asset': 'THETA', 'free': '0.06398761', 'locked': '0'}, {'asset': 'TRX', 'free': '0', 'locked': '0'}, {'asset': 'UNFI', 'free': '0', 'locked': '0'}, {'asset': 'USDT', 'free': '0', 'locked': '0'}, {'asset': 'VET', 'free': '0', 'locked': '0'}, {'asset': 'VTHO', 'free': '0', 'locked': '0'}, {'asset': 'WRX', 'free': '0', 'locked': '0'}, {'asset': 'XEC', 'free': '0', 'locked': '0'}, {'asset': 'XMR', 'free': '0', 'locked': '0'}, {'asset': 'XRP', 'free': '0', 'locked': '0'}, {'asset': 'XTZ', 'free': '0.02777535', 'locked': '0'}, {'asset': 'ZEC', 'free': '0', 'locked': '0'}, {'asset': 'ZIL', 'free': '1.26195056', 'locked': '0'}]}}, {'type': 'spot', 'updateTime': 1680220799000, 'data': {'totalAssetOfBtc': '0.00006784', 'balances': [{'asset': 'ADA', 'free': '0.11377624', 'locked': '0'}, {'asset': 'ALGO', 'free': '0', 'locked': '0'}, {'asset': 'ANKR', 'free': '0', 'locked': '0'}, {'asset': 'AR', 'free': '0', 'locked': '0'}, {'asset': 'ARPA', 'free': '0', 'locked': '0'}, {'asset': 'ATOM', 'free': '0.02568613', 'locked': '0'}, {'asset': 'AUDIO', 'free': '0', 'locked': '0'}, {'asset': 'AVAX', 'free': '0', 'locked': '0'}, {'asset': 'AXS', 'free': '0', 'locked': '0'}, {'asset': 'BAL', 'free': '0', 'locked': '0'}, {'asset': 'BAND', 'free': '0', 'locked': '0'}, {'asset': 'BAT', 'free': '0', 'locked': '0'}, {'asset': 'BEL', 'free': '0', 'locked': '0'}, {'asset': 'BETH', 'free': '0', 'locked': '0'}, {'asset': 'BLZ', 'free': '0', 'locked': '0'}, {'asset': 'BNB', 'free': '0.00035545', 'locked': '0'}, {'asset': 'BTC', 'free': '0', 'locked': '0'}, {'asset': 'BTT', 'free': '0', 'locked': '0'}, {'asset': 'BZRX', 'free': '0', 'locked': '0'}, {'asset': 'CELO', 'free': '0', 'locked': '0'}, {'asset': 'CELR', 'free': '0', 'locked': '0'}, {'asset': 'CFX', 'free': '0', 'locked': '0'}, {'asset': 'CHR', 'free': '0', 'locked': '0'}, {'asset': 'CHZ', 'free': '0', 'locked': '0'}, {'asset': 'COMP', 'free': '0', 'locked': '0'}, {'asset': 'DASH', 'free': '0', 'locked': '0'}, {'asset': 'DATA', 'free': '0', 'locked': '0'}, {'asset': 'DNT', 'free': '0', 'locked': '0'}, {'asset': 'DOGE', 'free': '0', 'locked': '0'}, {'asset': 'EGLD', 'free': '0.00595136', 'locked': '0'}, {'asset': 'EOS', 'free': '0.0142741', 'locked': '0'}, {'asset': 'ETH', 'free': '0', 'locked': '0'}, {'asset': 'ETHW', 'free': '0.10354775', 'locked': '0'}, {'asset': 'FOR', 'free': '0', 'locked': '0'}, {'asset': 'FTT', 'free': '0', 'locked': '0'}, {'asset': 'GALA', 'free': '0', 'locked': '0'}, {'asset': 'GRT', 'free': '0', 'locked': '0'}, {'asset': 'ICP', 'free': '0.02174776', 'locked': '0'}, {'asset': 'IOTX', 'free': '0', 'locked': '0'}, {'asset': 'JST', 'free': '0', 'locked': '0'}, {'asset': 'KEEP', 'free': '0', 'locked': '0'}, {'asset': 'LAZIO', 'free': '0', 'locked': '0'}, {'asset': 'LDADA', 'free': '0', 'locked': '0'}, {'asset': 'LDATOM', 'free': '0', 'locked': '0'}, {'asset': 'LDBTC', 'free': '0.01136585', 'locked': '0'}, {'asset': 'LDCHZ', 'free': '0.01841119', 'locked': '0'}, {'asset': 'LDEOS', 'free': '0', 'locked': '0'}, {'asset': 'LDERD', 'free': '0', 'locked': '0'}, {'asset': 'LDETH', 'free': '0.05072539', 'locked': '0'}, {'asset': 'LDGALA', 'free': '373.64184596', 'locked': '0'}, {'asset': 'LDICP', 'free': '0', 'locked': '0'}, {'asset': 'LDLAZIO', 'free': '0.08379923', 'locked': '0'}, {'asset': 'LDLINK', 'free': '0.01189422', 'locked': '0'}, {'asset': 'LDMATIC', 'free': '0', 'locked': '0'}, {'asset': 'LDSAND', 'free': '29.30176665', 'locked': '0'}, {'asset': 'LDSHIB2', 'free': '0', 'locked': '0'}, {'asset': 'LDSOL', 'free': '0', 'locked': '0'}, {'asset': 'LDTHETA', 'free': '0', 'locked': '0'}, {'asset': 'LDUSDT', 'free': '171.57497593', 'locked': '0'}, {'asset': 'LDVET', 'free': '111.13932981', 'locked': '0'}, {'asset': 'LDVTHO', 'free': '129.42554013', 'locked': '0'}, {'asset': 'LDWRX', 'free': '9.07671439', 'locked': '0'}, {'asset': 'LDXEC', 'free': '139405.18', 'locked': '0'}, {'asset': 'LDXMR', 'free': '0.10254661', 'locked': '0'}, {'asset': 'LDXRP', 'free': '326.68153433', 'locked': '0'}, {'asset': 'LDXTZ', 'free': '0', 'locked': '0'}, {'asset': 'LDZIL', 'free': '0', 'locked': '0'}, {'asset': 'LINK', 'free': '0', 'locked': '0'}, {'asset': 'LPT', 'free': '0', 'locked': '0'}, {'asset': 'LRC', 'free': '0', 'locked': '0'}, {'asset': 'LUNA', 'free': '0', 'locked': '0'}, {'asset': 'MANA', 'free': '0', 'locked': '0'}, {'asset': 'MATIC', 'free': '0.25985803', 'locked': '0'}, {'asset': 'NEAR', 'free': '0', 'locked': '0'}, {'asset': 'OMG', 'free': '0', 'locked': '0'}, {'asset': 'ONE', 'free': '0', 'locked': '0'}, {'asset': 'ORN', 'free': '0', 'locked': '0'}, {'asset': 'QNT', 'free': '0', 'locked': '0'}, {'asset': 'RSR', 'free': '0', 'locked': '0'}, {'asset': 'SAND', 'free': '0', 'locked': '0'}, {'asset': 'SHIB', 'free': '5683148.15', 'locked': '0'}, {'asset': 'SOL', 'free': '0.00131999', 'locked': '0'}, {'asset': 'SOLO', 'free': '1.71553587', 'locked': '0'}, {'asset': 'STMX', 'free': '0', 'locked': '0'}, {'asset': 'STX', 'free': '0', 'locked': '0'}, {'asset': 'THETA', 'free': '0.06424744', 'locked': '0'}, {'asset': 'TRX', 'free': '0', 'locked': '0'}, {'asset': 'UNFI', 'free': '0', 'locked': '0'}, {'asset': 'USDT', 'free': '0', 'locked': '0'}, {'asset': 'VET', 'free': '0', 'locked': '0'}, {'asset': 'VTHO', 'free': '0', 'locked': '0'}, {'asset': 'WRX', 'free': '0', 'locked': '0'}, {'asset': 'XEC', 'free': '0', 'locked': '0'}, {'asset': 'XMR', 'free': '0', 'locked': '0'}, {'asset': 'XRP', 'free': '0', 'locked': '0'}, {'asset': 'XTZ', 'free': '0.02873858', 'locked': '0'}, {'asset': 'ZEC', 'free': '0', 'locked': '0'}, {'asset': 'ZIL', 'free': '1.30871052', 'locked': '0'}]}}, {'type': 'spot', 'updateTime': 1680307199000, 'data': {'totalAssetOfBtc': '0.00006807', 'balances': [{'asset': 'ADA', 'free': '0.11785141', 'locked': '0'}, {'asset': 'ALGO', 'free': '0', 'locked': '0'}, {'asset': 'ANKR', 'free': '0', 'locked': '0'}, {'asset': 'AR', 'free': '0', 'locked': '0'}, {'asset': 'ARPA', 'free': '0', 'locked': '0'}, {'asset': 'ATOM', 'free': '0.02660398', 'locked': '0'}, {'asset': 'AUDIO', 'free': '0', 'locked': '0'}, {'asset': 'AVAX', 'free': '0', 'locked': '0'}, {'asset': 'AXS', 'free': '0', 'locked': '0'}, {'asset': 'BAL', 'free': '0', 'locked': '0'}, {'asset': 'BAND', 'free': '0', 'locked': '0'}, {'asset': 'BAT', 'free': '0', 'locked': '0'}, {'asset': 'BEL', 'free': '0', 'locked': '0'}, {'asset': 'BETH', 'free': '0', 'locked': '0'}, {'asset': 'BLZ', 'free': '0', 'locked': '0'}, {'asset': 'BNB', 'free': '0.00035962', 'locked': '0'}, {'asset': 'BTC', 'free': '0', 'locked': '0'}, {'asset': 'BTT', 'free': '0', 'locked': '0'}, {'asset': 'BZRX', 'free': '0', 'locked': '0'}, {'asset': 'CELO', 'free': '0', 'locked': '0'}, {'asset': 'CELR', 'free': '0', 'locked': '0'}, {'asset': 'CFX', 'free': '0', 'locked': '0'}, {'asset': 'CHR', 'free': '0', 'locked': '0'}, {'asset': 'CHZ', 'free': '0', 'locked': '0'}, {'asset': 'COMP', 'free': '0', 'locked': '0'}, {'asset': 'DASH', 'free': '0', 'locked': '0'}, {'asset': 'DATA', 'free': '0', 'locked': '0'}, {'asset': 'DNT', 'free': '0', 'locked': '0'}, {'asset': 'DOGE', 'free': '0', 'locked': '0'}, {'asset': 'EGLD', 'free': '0.0059847', 'locked': '0'}, {'asset': 'EOS', 'free': '0.014784', 'locked': '0'}, {'asset': 'ETH', 'free': '0', 'locked': '0'}, {'asset': 'ETHW', 'free': '0.10354775', 'locked': '0'}, {'asset': 'FOR', 'free': '0', 'locked': '0'}, {'asset': 'FTT', 'free': '0', 'locked': '0'}, {'asset': 'GALA', 'free': '0', 'locked': '0'}, {'asset': 'GRT', 'free': '0', 'locked': '0'}, {'asset': 'ICP', 'free': '0.02178249', 'locked': '0'}, {'asset': 'IOTX', 'free': '0', 'locked': '0'}, {'asset': 'JST', 'free': '0', 'locked': '0'}, {'asset': 'KEEP', 'free': '0', 'locked': '0'}, {'asset': 'LAZIO', 'free': '0', 'locked': '0'}, {'asset': 'LDADA', 'free': '0', 'locked': '0'}, {'asset': 'LDATOM', 'free': '0', 'locked': '0'}, {'asset': 'LDBTC', 'free': '0.01136591', 'locked': '0'}, {'asset': 'LDCHZ', 'free': '0.01841119', 'locked': '0'}, {'asset': 'LDEOS', 'free': '0', 'locked': '0'}, {'asset': 'LDERD', 'free': '0', 'locked': '0'}, {'asset': 'LDETH', 'free': '0.05072573', 'locked': '0'}, {'asset': 'LDGALA', 'free': '373.64184596', 'locked': '0'}, {'asset': 'LDICP', 'free': '0', 'locked': '0'}, {'asset': 'LDLAZIO', 'free': '0.08379923', 'locked': '0'}, {'asset': 'LDLINK', 'free': '0.01189893', 'locked': '0'}, {'asset': 'LDMATIC', 'free': '0', 'locked': '0'}, {'asset': 'LDSAND', 'free': '29.30209788', 'locked': '0'}, {'asset': 'LDSHIB2', 'free': '0', 'locked': '0'}, {'asset': 'LDSOL', 'free': '0', 'locked': '0'}, {'asset': 'LDTHETA', 'free': '0', 'locked': '0'}, {'asset': 'LDUSDT', 'free': '171.58260145', 'locked': '0'}, {'asset': 'LDVET', 'free': '111.13932981', 'locked': '0'}, {'asset': 'LDVTHO', 'free': '129.45783727', 'locked': '0'}, {'asset': 'LDWRX', 'free': '9.07671439', 'locked': '0'}, {'asset': 'LDXEC', 'free': '139405.18', 'locked': '0'}, {'asset': 'LDXMR', 'free': '0.10254661', 'locked': '0'}, {'asset': 'LDXRP', 'free': '326.68182056', 'locked': '0'}, {'asset': 'LDXTZ', 'free': '0', 'locked': '0'}, {'asset': 'LDZIL', 'free': '0', 'locked': '0'}, {'asset': 'LINK', 'free': '0', 'locked': '0'}, {'asset': 'LPT', 'free': '0', 'locked': '0'}, {'asset': 'LRC', 'free': '0', 'locked': '0'}, {'asset': 'LUNA', 'free': '0', 'locked': '0'}, {'asset': 'MANA', 'free': '0', 'locked': '0'}, {'asset': 'MATIC', 'free': '0.26971809', 'locked': '0'}, {'asset': 'NEAR', 'free': '0', 'locked': '0'}, {'asset': 'OMG', 'free': '0', 'locked': '0'}, {'asset': 'ONE', 'free': '0', 'locked': '0'}, {'asset': 'ORN', 'free': '0', 'locked': '0'}, {'asset': 'QNT', 'free': '0', 'locked': '0'}, {'asset': 'RSR', 'free': '0', 'locked': '0'}, {'asset': 'SAND', 'free': '0', 'locked': '0'}, {'asset': 'SHIB', 'free': '5683155.38', 'locked': '0'}, {'asset': 'SOL', 'free': '0.00134543', 'locked': '0'}, {'asset': 'SOLO', 'free': '1.71553587', 'locked': '0'}, {'asset': 'STMX', 'free': '0', 'locked': '0'}, {'asset': 'STX', 'free': '0', 'locked': '0'}, {'asset': 'THETA', 'free': '0.06450727', 'locked': '0'}, {'asset': 'TRX', 'free': '0', 'locked': '0'}, {'asset': 'UNFI', 'free': '0', 'locked': '0'}, {'asset': 'USDT', 'free': '0', 'locked': '0'}, {'asset': 'VET', 'free': '0', 'locked': '0'}, {'asset': 'VTHO', 'free': '0', 'locked': '0'}, {'asset': 'WRX', 'free': '0', 'locked': '0'}, {'asset': 'XEC', 'free': '0', 'locked': '0'}, {'asset': 'XMR', 'free': '0', 'locked': '0'}, {'asset': 'XRP', 'free': '0', 'locked': '0'}, {'asset': 'XTZ', 'free': '0.02970181', 'locked': '0'}, {'asset': 'ZEC', 'free': '0', 'locked': '0'}, {'asset': 'ZIL', 'free': '1.35547048', 'locked': '0'}]}}]
        # for each in data:
        #     print(each)
        # return data
        #
        # # print(json.dumps(data, indent=2))
        # btcprice = b.getCoinPrice('BTC')

    def getTradeFee(self, coin, pairwith='USDT'):
        coin = coin.upper().strip()
        fees = self.bclient.get_trade_fee(symbol=coin)
        if len(fees)>0:        
            return float(fees[0]['takerCommission'])
        else:
            return 0
        
    def getCoinBalance(self, coin):
        data = self.bclient.get_asset_balance(asset=coin)
        free = data['free']
        locked = data['locked']
        if not free.startswith('0.00000'):
            return float(free)
        if not locked.startswith('0.00000'):
            return float(locked)
        return float(0.0)
    
    def previewSell(self, coin):
        currPrice = self.getCoinPrice(coin)
        myBalance = self.getCoinBalance(coin)
        tradeFee = self.getTradeFee(coin)
        bnbBalance = self.getCoinBalance('BNB')
        ttlAmount = currPrice * myBalance
        ttlFee = ttlAmount * (tradeFee/100)
        feetype = 'BNB'
        if bnbBalance < ttlFee:
            ttlAmount = ttlAmount - ttlFee
            feetype = 'USDT'
        data = {}
        data['coin'] = coin
        data['currprice'] = currPrice
        data['mybalance'] = myBalance
        data['total'] = ttlAmount
        data['fee'] = ttlFee
        data['feetype'] = feetype
        return data

    def symbolVolPercentInBinance(self,limit=100):
        
        url = 'https://coinmarketcap.com/exchanges/binance/'
        
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all('tbody')
        results = results[1]
        rows = results.find_all("tr")
        
        data = []
        for each in rows:
            '''
            1 AVAX/USDT 0.67%
            2 BTC/USDT 16.46%
            3 BTC/USDC 1.21%    
            '''
            r = each.find_all('td')
            no = r[0].text
            pair = r[2].text
            volpercent = r[7].text
            
            symbol,pair = pair.split('/')
            volpercent = volpercent.replace('%','')
            volpercent = float(volpercent)
            tmp = [symbol, pair, volpercent]
            data.append(tmp)
        
        lst = sorted(data, key=itemgetter(2), reverse=True)
        resp = []
        cnt = 1
        for each in lst:
            if cnt <= limit:
                resp.append(each)
                cnt += 1
        
        #[symbol, pair, volpercent]
        return resp
        
    
class CoinStats(object):
    
    def __init__(self):
        '''
        Constructor
        '''
        self.tls = xtools.getGlobalTools()
        self.tls.debug('Initializing {0}'.format(self.__class__.__name__))
        
        self.baseUrl = 'https://api.coinstats.app/public/v1'
        
    def getCoinPriceTicker(self,coin):
        '''
        No garuentee, Limit using this fn
        '''    
        url = self.baseUrl + '/tickers?exchange=Binance&pair='+coin.strip().upper()+'-USDT'
        response = requests.request("GET", url)
        return response.text
    
    def getCoinPrice(self,coin,fiet='INR'):
        '''
        No garuentee, Limit using this fn
        '''
        url = self.baseUrl + '/coins?skip=0&limit=2050&currency='+fiet
        response = requests.request("GET", url)
        data = response.json()
        cnt=1
        for each in data['coins']:
            cnt=cnt+1
            if each['symbol'].strip().upper() == coin.strip().upper():
                return (each['name'],each['symbol'],each['price'])
        return None

    
class Giottus(object):
    
    def __init__(self, api_key=''):
        '''
        Constructor
        '''
        self.tls = xtools.getGlobalTools()
        self.tls.debug('Initializing {0}'.format(self.__class__.__name__))
        
        self.baseUrl = 'https://www.giottus.com/api/ticker'
    
    def _urlCall(self ):
        url = self.baseUrl    
        session = Session()
        data = ''
        try:
            response = session.get(url)
            data = json.loads(response.text)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            self.tls.error(e)        
        return data
    
    def getCoinPrice(self, coin, fiet='INR'):
        data = ''
        coin = coin+'/'+fiet
        coin = coin.strip()
        try:
            response = self._urlCall()
            data = response
            prc = data['prices']
            for each in prc:
                if coin == each:
                    return float (prc[each])
                    
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            self.tls.error(e)        
        return data

class CryptoPanic(object):
    
    def __init__(self, api_key=''):
        '''
        Constructor
        '''
        self.tls = xtools.getGlobalTools()
        self.tls.debug('Initializing {0}'.format(self.__class__.__name__))
        
        self.baseUrl = 'https://cryptopanic.com/api/v1/posts/?auth_token=2b6b8188040e2a9e5cea6d13a4a8adde5312df72'
        
    def _urlCall(self,input=''):
        url = self.baseUrl    
        session = Session()
        data = ''
        try:
            self.tls.debug(url+input)
            response = session.get(url+input)
            data = json.loads(response.text) if response.status_code == 200 else {'results':[]}
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            self.tls.info('Unable to process: ' + str(url+input))
            self.tls.error(e)        
        return data
    

    def getCoinInfo(self, coin):
        '''
        bearish, bullish, 
        filter=(rising|hot|bullish|bearish|important|saved|lol)
        
        {'ttlnegative': 0, 'ttlpositive': 2, 'ttlliked': 3, 'ttldisliked': 0, 'ttllol': 0, 'ttlcomments': 0, 'ttlimportant': 0, 'ttlall': 5, 'weekcnt': 20, 'last2dayscnt': 13}
        '''
        res = {}

        input= f'&filter={filter}&currencies={coin}&page=1'
        input= f'&currencies={coin}&page=1'

        try:
            data = self._urlCall(input)
            news7d = 0
            news2d = 0
            if len(data['results'])>0:
                isCoinFound = False
                ttlnegative = 0
                ttlpositive = 0
                ttlliked = 0
                ttldisliked = 0
                ttllol = 0
                ttlimportant = 0
                ttlcomments = 0
                ttlall = 0
                for each in data['results']:
                    currencies = each['currencies']
                    votes = each['votes']
                    negative = votes['negative']
                    positive = votes['positive']
                    liked = votes['liked']
                    disliked = votes['disliked']
                    lol = votes['lol']
                    important = votes['important']
                    comments = votes['comments']
                    date = each['published_at']
                    for eachCur in currencies:
                        inCoin = eachCur['code']
                        if inCoin.upper() == coin.upper():
                            isCoinFound = True
                            ttlnegative += negative
                            ttlpositive += positive
                            ttlliked += liked
                            ttldisliked += disliked
                            ttllol += lol
                            ttlimportant += important
                            ttlcomments += comments  
                            ttlall += negative + positive +  liked + disliked + lol + important + comments
                    date = date.split('T')[0]
                    today = self.tls.getDateCalc(0)
                    diff = self.tls.getDateDiff(today,date)
                    if diff > -7: news7d += 1
                    if diff > -2: news2d += 1
                                    
                if isCoinFound:
                    res['ttlnegative']=ttlnegative
                    res['ttlpositive']=ttlpositive
                    res['ttlliked']=ttlliked
                    res['ttldisliked']=ttldisliked
                    res['ttllol']=ttllol
                    res['ttlcomments']=ttlcomments
                    res['ttlimportant']= ttlimportant   
                    res['ttlreact'] = ttlall
                    res['news7d'] = news7d
                    res['news2d'] = news2d         
                    
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            self.tls.info('Unable to process: ' + str(input))
            self.tls.error(e)        
        return res

    def isCoinTrendingNow(self, coin, usrReactionExpected = 1, news2d = 2, news7d = 3, data = None):
        data = data if data else self.getCoinInfo(coin)
        #{'ttlnegative': 0, 'ttlpositive': 2, 'ttlliked': 3, 'ttldisliked': 0, 'ttllol': 0, 'ttlcomments': 0, 'ttlimportant': 0, 'ttlall': 5, 'weekcnt': 20, 'last2dayscnt': 13}
        self.tls.debug(data)
        if data['ttlreact']  >= usrReactionExpected:
            if data['news2d'] >= news2d:
                if data['news7d'] >= news7d:
                    self.tls.debug(f'Coin {coin} is trending')
                    return True
        self.tls.debug(f'Coin {coin} is not popular now')
        return False
    
class CoinGecko(object):
    
    def __init__(self):
        '''
        Constructor
        '''
        self.tls = xtools.getGlobalTools()
        self.tls.debug('Initializing {0}'.format(self.__class__.__name__))

    def getExchangeToppers(self):
        murl = 'https://www.coingecko.com/en/exchanges/binance'
        
        page = requests.get(murl)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find('tbody', {'data-target':['exchanges.tablebody']})
        rows = results.find_all("tr")
        
        datas = []
        for each in rows:
            _tmp = each.find_all('td')
            
            rank = _tmp[0].text.strip()
            rank = float(rank)
            
            marketCap = _tmp[2].text.strip()
            marketCap = marketCap.replace(',','').replace('$','')
            marketCap = float(marketCap)
            
            pairRaw = _tmp[3].text.strip()
            symbol = pairRaw.replace('/USDT','')
            
            price = _tmp[4].find('div').text.strip()
            price = price.replace(',','').replace('$','').replace('*','').replace(' ','')
            price = float(price)
            
            spreadPercent = _tmp[5].text.strip()
            spreadPercent = spreadPercent.replace(',','').replace('$','').replace('%','')
            spreadPercent = float(spreadPercent)
            
            volTraded24h = _tmp[8].find('div').text.strip()
            volTraded24h = volTraded24h.replace(',','').replace('$','').replace('%','')
            volTraded24h = float(volTraded24h)
            
            volTradedPercent = _tmp[9].text.strip()
            volTradedPercent = volTradedPercent.replace(',','').replace('$','').replace('%','')
            volTradedPercent = float(volTradedPercent)
            
            if '/USDT' in pairRaw:
                tmp = {}
                tmp['rank'] = rank        
                tmp['symbol'] = symbol
                tmp['price'] = price
                tmp['marketCap'] = marketCap
                tmp['spreadPercent'] = spreadPercent
                tmp['volTraded24h'] = volTraded24h
                tmp['volTradedPercent'] = volTradedPercent
                datas.append(tmp)
            
        ndatas = tls.sortListOfDict(datas,'volTraded24h')
        return ndatas
            
if __name__ == '__main__':
    
    c = CoinMarketCap()

    # r = c.getTopGainer(10)
    # for each in r:
    #     print(each)

    r = c.getMarketVolumeToperSpl()
    for each in r:
        print(each)       
    
    # gn = General()
    # #_datas = gn.getCryptoBriefAnalysis(0)
    # #_datas = gn.getCryptoEvents()
    # #_datas = gn.getTopWhaleTranactions()
    #
    # for each in _datas:
    #     tls.info(each)  
    
    # cp = CryptoPanic()
    # d = cp.getCoinInfo('DOT')
    # print(d)
    
    #
    # bn = Binance()
    # # d = bn.getMyFlexibleSavingAccountDetail()
    # # d = bn.getMyFlexibleDefiAccountDetail()
    # # d = bn.getMyLiquiditySwapAccountDetail()
    # d = bn.getMyAssets()    
    # inr = bn.getP2PRate() * d['ttl_usd_value']
    #
    # f = open('mybinance.txt','a')
    # data = f'{tls.getDateTime()},{inr}'
    # f.write(data)
    #
    # print(inr, 'Rs')
    
     
    #
    # for each in d['assets']:
    #     print(each, d['assets'][each])
        
    print('done')