import kDatabase

#Sample Data
#{'date': 20250610023004, 'coin': 'AVAX', 'coinslug': 'avalanche', 'price': 21.31964523555377,
# 'pricechangepercent': -0.57316786, 'binanceTradeVolPercent': 0.32, 'trend7d': -3, 'trendttl': 235, 'rank': 14,
# 'cmcWatchers': 1000000, 'cmcStarRating': 4, 'status': 'pass', 'winDate': 20250610034002,
# 'winDuration': 0, 'isMostVisited': 1, 'isMostTrending': 1, 'isSentimental': 1,
# 'bullvotes': 86, 'bearvotes': 21, 'bullpercent': 80, 'bearpercent': 20, 'ttlvotes': 234, 'trendpercent': 3.3, 'sentimenttype': 'bullish'}

import kTools


class LocalFireStore():

    def __init__(self, db="mydata", dbuser="root", dbpass=None):
        self.tls = kTools.KTools()
        dbpass = dbpass if dbpass else self.tls.getSafeEnv("DB_PASS")
        self.db = kDatabase.SimpleCouchDB(db, dbuser, dbpass)

    def getDocuments(self):
        return self.db.getAllDocuments()

    def getDocumentsByDate(self, date):
        if len(str(date)) == 14:
            date = int(date/1000000)
        if not len(str(date)) == 8:
            self.tls.error(f"Unable to update, Invalid date {date}. Should be 8 digit.")
            return
        selector = {
            "date": {
                "$gte": date * 1000000,
                "$lte": date * 1000000 + 235959
            }
        }
        find_query = {
            "selector": selector
        }
        res = self.db.db.find(find_query)
        docs = list(res)
        if not docs:
            self.tls.error(f"No data found for {selector}")
            return []
        else:
            return docs

    def getDocumentsByDateCoin(self, date, coin=""):
        if len(str(date)) == 14:
            date = int(date/1000000)
        if not len(str(date)) == 8:
            self.tls.error(f"Unable to update, Invalid date {date}. Should be 8 digit.")
            return
        selector = {
            "date": {
                "$gte": date * 1000000,
                "$lte": date * 1000000 + 235959
            },
            "coin": coin
        }
        find_query = {
            "selector": selector
        }
        res = self.db.db.find(find_query)
        docs = list(res)
        if not docs:
            self.tls.error(f"No data found for {selector}")
            return []
        else:
            return docs

    def getDocumentsByStatus(self, status="open"):
        selector = {
            "status": status
        }
        find_query = {
            "selector": selector
        }
        res = self.db.db.find(find_query)
        docs = list(res)
        if not docs:
            self.tls.error(f"No data found for {selector}")
            return []
        else:
            return docs

    def getDocumentsByDateCoinStatus(self, date, coin="", status="open"):
        if len(str(date)) == 14:
            date = int(date/1000000)
        if not len(str(date)) == 8:
            self.tls.error(f"Unable to update, Invalid date {date}. Should be 8 digit.")
            return
        selector = {
            "status": status,
            "date": {
                "$gte": date * 1000000,
                "$lte": date * 1000000 + 235959
            },
            "coin": coin
        }
        find_query = {
            "selector": selector
        }
        res = self.db.db.find(find_query)
        docs = list(res)
        if not docs:
            self.tls.error(f"No data found for {selector}")
            return []
        else:
            return docs

    def updateDocument(self, date, coin):
        docs = self.getDocumentsByDateCoinStatus(date, coin, "open")
        if len(docs)==1:
            doc = docs[0]
            today = self.tls.getDateTimeStamp("%Y%m%d%H%M%S")
            noOfDays = self.tls.getDateDiff(date, today, "%Y%m%d%H%M%S")
            toUpdate = {"winDate": today, "winDuration" : noOfDays, "status" : "pass" }
            doc.update(toUpdate)
            self.db.db.save(doc)
            self.tls.info(f"Updated {date} - {coin}")

    def addDocument(self, data):
        return self.db.setDocument(data)

    def convertDocsToDict(self, docs):
        lst=[]
        for eachDoc in docs:
            lst.append(dict(eachDoc))
        return lst

if __name__ == "__main__":
    lfs = LocalFireStore()

    #docs = lfs.getDocumentsByStatus(status="open")
    #print(docs)

    #docs = lfs.getDocumentsByDateCoinStatus(20250527175706, "ETH", "open")
    #print(docs)

    #lfs.updateDocument(20250527175706, "ETH")

    # docs = lfs.getDocuments()
    # for each in docs:
    #     print(each)

    docs = lfs.getDocumentsByDateCoin(20250527175706, "ETH")
    doc = docs[0]
    print(doc.id, doc.rev)
    print(dict(doc))
    print(dict(doc.items()))

    print("done")
