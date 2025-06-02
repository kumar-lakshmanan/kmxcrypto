'''
Created on 09-Sep-2021

@author: kayma
'''
#-----------------------
from requests import Session
from bs4 import BeautifulSoup
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

from common_lib import kTools

class General(object):

    def __init__(self):
        
        self.tls = kTools.KTools()
        self.tls.debug('Initializing {0}'.format(self.__class__.__name__))
        
        self.diffFor = ['inr','usdt','wrx']
        self.marketPriceCache=None
        
        #Twitter API 
        self.apikey = 'nIwelYBfBnyGu28l4zpDT9P3G'
        self.apikeysecret = 'spLEwRlZS5YxQMZjcDe5iMMwiMoTCmZjqnJyEP1Y1kBxPOYViL'
        self.accesstoken = '1136767650111971329-Elzpa1L5lv5iskLAsbmzqFQoI8d49j'
        self.accesstokensecret = 'fx3Gulv7cB48w7npUDPmO3vpco4cm5IYGlxA37jzH5ueh'     
        
        self.clankAppApiKey = '3c13c61d22a41e05a2fcbdbb6378edd5'
        self.coinMarketCalAPIKey = 'jSf8OdeFuM1MBUIGKhYHuICOcrcfR2GyYgcvQzj0'
        #
        # self.p2prate = None
        #
        # self.cmc = CoinMarketCap()
        # self.bn = Binance()
    
    def getCryptoEventsExt(self, sourcelink):
        '''
        https://coinmarketcal.com/event/kucoin-listing-127442
        https://coinmarketcal.com/en/event/coinfest-asia-119925
        https://coinmarketcal.com/event/dfk-colosseum-expansion-261655
        '''
        confidence_percent = 0
        votes = 0               
        viewed = 0      
           
        if sourcelink: 
            headers = {'User-Agent': 'Mozilla/5.0'}        
            page = requests.get(sourcelink, headers=headers)
            soup = BeautifulSoup(page.content,'xml')
            tmp1 = soup.findAll("span", {"class" : "count-to"})
            tmp2 = soup.findAll("div", {"class" : "tip"})
            
            if len(tmp1)==2:
                confidence_percent = tmp1[0].attrs['data-countto'] if 'data-countto' in tmp1[0].attrs else 0
                votes = tmp1[1].attrs['data-countto']  if 'data-countto' in tmp1[0].attrs else 0
                confidence_percent = int(confidence_percent)
                votes = int(votes)
    
            if len(tmp2)==1:
                viewed = tmp2[0].text.split()
                viewed = viewed[0].strip() 
                viewed = int(viewed)
        
        data = {}
        data['confidence_percent'] = confidence_percent
        data['votes'] = votes
        data['viewed'] = viewed
            
        return data      
    
    def getCryptoEvents(self):
        self.tls.debug("Fetching crypto events...")
        url = "https://developers.coinmarketcal.com/v1/events"
        querystring = {"max":"75","page":"1","sortBy":"created_desc", "showViews":"true"}
        payload = ""
        headers = {
           'x-api-key': self.coinMarketCalAPIKey,
           'Accept-Encoding': "deflate, gzip",
           'Accept': "application/json"
        }
        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
        data = response.json()
        
        def _symbols(data_tmp):
            _allsymbols = []
            if len(data_tmp)<=3:
                for each in data_tmp[:3]:
                    _allsymbols.append(each['symbol'])
            return _allsymbols
        
        resp = []
        if 'body' in data and '_metadata' in data:
            cnt = data['_metadata']['total_count']
            for each in data['body']:
                title = each['title']['en']
                symbols = _symbols(each['coins'])
                eventOn = each['date_event']
                informedOn = each['created_date']
                category = each['categories'][0]['name']
                sourcelink = each['source']
                tobj = self.tls.getDateTimeObjFor(informedOn,'%Y-%m-%dT%H:%M:%SZ')
                informedOn = self.tls.getDateTimeForObj(tobj)                
                tobj = self.tls.getDateTimeObjFor(eventOn,'%Y-%m-%dT%H:%M:%SZ')
                eventOn = self.tls.getDateTimeForObj(tobj)                 
                
                informDate = informedOn.split()[0]
                today = self.tls.getDateTime('%Y%m%d')
                diff = self.tls.getDateDiff(informDate, today,'%Y%m%d')
                
                extData=''                
                if 0<=diff<=1:
                    if len(symbols):
                        for eachSymbol in symbols:
                            tmp = {}
                            tmp['informedOn'] = informedOn
                            tmp['symbol'] = eachSymbol
                            tmp['title'] = title
                            tmp['category'] = category
                            tmp['eventOn'] = eventOn
                            tmp['sourcelink'] = sourcelink
                            # extData = self.getCryptoEventsExt(sourcelink)
                            # tmp['confPercent'] = extData['confidence_percent']
                            # tmp['votes'] = extData['votes']
                            # tmp['viewed'] = extData['viewed'] 
                            resp.append(tmp)
        
        return resp
    
    # def getTopWhaleTranactions(self,limit=500):
    #     '''
    #     Whale Actions
    #     '''
    #
    #     url = 'https://api.clankapp.com/v2/explorer/tx?s_date=desc&size=150&api_key=' + self.clankAppApiKey
    #     page = requests.get(url)
    #     data = page.json()
    #
    #     ignoresymbol = self.tls.cfg.crypts_ignoreProcessingSymbols
    #
    #     def _conv(symbol, bc):
    #         '''
    #         symbol = usdt
    #         bc = ethereum
    #
    #         2022-05-20T07:21:01  ethereum  usdt  transfer  huobi  binance
    #         2022-05-20T07:20:06  tron  usdt  transfer  unknown wallet  unknown wallet
    #         '''
    #         giveBack = symbol
    #         if giveBack == 'usdt':
    #             giveBack = bc
    #             if giveBack == 'ethereum':
    #                 giveBack = 'eth'
    #         return giveBack
    #
    #     def _conv2(location):
    #         '''
    #         location = unknown wallet or multiple addresses 
    #
    #         '''
    #         giveBack = location
    #         if giveBack == 'unknown wallet':
    #             giveBack = '-'
    #         if giveBack == 'multiple addresses':
    #             giveBack = 'mulitple'
    #         return giveBack       
    #
    #     lst = data['data']
    #
    #     finData = []
    #     for each in lst:
    #         symbol = _conv(each['symbol'], each['blockchain'])
    #         symbol = CoinMarketCap().findSymbolWithWord(symbol)
    #         if not symbol in ignoresymbol: 
    #             date = each['date']
    #             tobj = self.tls.getDateTimeObjFor(date,'%Y-%m-%dT%H:%M:%S')
    #             date = self.tls.getDateTimeForObj(tobj, '%Y%m%d') 
    #             time = self.tls.getDateTimeForObj(tobj, '%H%M%S')                                
    #             amount_usd = each['amount_usd']
    #             transaction_type = each['transaction_type']
    #             from_owner = _conv2(each['from_owner'])
    #             to_owner = _conv2(each['to_owner'])
    #             tmp = [date,time,symbol,from_owner,to_owner,transaction_type,amount_usd]
    #             finData.append(tmp)
    #
    #     lst = sorted(finData, key=itemgetter(6), reverse=True)
    #     resp = []
    #     cnt = 1
    #     for each in lst:
    #         if cnt <= limit:
    #             resp.append(each)
    #             cnt += 1 
    #
    #     return resp

    def getGoldRate(self):
        self.tls.info('Fetching gadget360 - todays gold rate...')
        url = 'https://gadgets360.com/finance/digital-gold-price-in-india'
        page = requests.get(url)
        data = str(page.text)
        search1 = '<span>&#8377; '
        t1 = data.find(search1)
        ndata1 = data[t1:]
        t2 = ndata1.find('/g</span>')
        ndata2 = data[t1+len(search1):t1+22]
        ndata2 = ndata2.replace(',','')
        ndata2 = ndata2.replace('/','')
        
        data = float(ndata2)
        self.tls.info(f'Gold Rate: {data} Rs')
        return data 
    
    # def getBTCDominance(self):
    #     self.tls.info('Fetching twitter for BTC Dominance for today...')
    #     user = '@btcdominance'
    #     t = Twitter(auth=OAuth(self.accesstoken, self.accesstokensecret, self.apikey, self.apikeysecret))
    #     d = t.statuses.user_timeline(screen_name=user)
    #     whn = d[0]['created_at']
    #     txt = d[0]['text']
    #     if '#Bitcoin' in txt and '#Altcoin' in txt and '#Cryptocurrency' in txt:
    #         txt = txt.replace('Current BTC Dominance: ', '')
    #         txt = txt.replace(' #Bitcoin #Altcoin #Cryptocurrency','')
    #         txt = txt.replace('%','')
    #         txt = txt.strip()
    #     else:
    #         txt = '0.0'
    #     self.tls.info(f'BTC Dominance: {txt} %')
    #     return float(txt)
    
    # def getFearGreedIndex(self):
    #     '''
    #     Above 50 means all are buying
    #     '''
    #     self.tls.info('Fetching twitter for BTC FG Index for today...')
    #     user = '@BitcoinFear'
    #     t = Twitter(auth=OAuth(self.accesstoken, self.accesstokensecret, self.apikey, self.apikeysecret))
    #     d = t.statuses.user_timeline(screen_name=user)
    #     for each in d:
    #         if 'Bitcoin Fear and Greed Index is ' in each['text']:
    #             dt = each['created_at']
    #             txt = each['text']
    #             val = txt.replace('Bitcoin Fear and Greed Index is ','')
    #             val = val[0:2]
    #             matter = txt.replace('Bitcoin Fear and Greed Index is ','')
    #             matter = matter[3:]
    #             matterls = matter.split(' ',1)
    #             if len(matterls)==2:
    #                 matterls2=matterls[1]
    #                 matterls2=matterls2.split('\n')
    #                 matter = matterls2[0]
    #             self.tls.info(f'FG Index: {int(val)}, {matter}')
    #             return (dt, int(val), matter)
    #     self.tls.info(f'FG Index: {int(val)}, {matter}')
    #     return ('',0,'') 

if __name__ == '__main__':
    tls = kTools.GetKTools()
    gn = General()
    
    tls.info("getCryptoEventsExt")  #FAIL
    datas = gn.getCryptoEventsExt("https://coinmarketcal.com/event/dfk-colosseum-expansion-261655")
    tls.info(datas)
    
    tls.info("getCryptoEvents")
    datas = gn.getCryptoEvents()
    tls.info(datas)
    
    # tls.info("getTopWhaleTranactions")  #Fail
    # datas = gn.getTopWhaleTranactions()    
    # tls.info(datas)

    tls.info("getGoldRate")
    datas = gn.getGoldRate()
    tls.info(datas)    
    
    # tls.info("getBTCDominance")
    # datas = gn.getBTCDominance()
    # tls.info(datas)    
      
    # tls.info("getFearGreedIndex")
    # datas = gn.getFearGreedIndex()
    # tls.info(datas)
    
    print('done')