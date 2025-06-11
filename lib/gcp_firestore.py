import os,sys

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.oauth2 import service_account

import kTools
#
# for doc in docs:
#     print(doc.id, doc.to_dict())

#{'date': 20250610023004, 'coin': 'AVAX', 'coinslug': 'avalanche', 'price': 21.31964523555377, 'pricechangepercent': -0.57316786, 'binanceTradeVolPercent': 0.32, 'trend7d': -3, 'trendttl': 235, 'rank': 14, 'cmcWatchers': 1000000, 'cmcStarRating': 4, 'status': 'pass', 'winDate': 20250610034002, 'winDuration': 0, 'isMostVisited': 1, 'isMostTrending': 1, 'isSentimental': 1, 'bullvotes': 86, 'bearvotes': 21, 'bullpercent': 80, 'bearpercent': 20, 'ttlvotes': 234, 'trendpercent': 3.3, 'sentimenttype': 'bullish'}

class GCPFireStore():

    def __init__(self, proj="kaymatrix", db="mydatastore"):
        self.tls = kTools.KTools()
        self.collectionName = "cryptos"

        if self.tls.isProd() and not self.tls.isLocal():
            self.db = firestore.Client(database=db)
        else:
            cred_file = self.tls.getSafeEnv("GCP_CRED")
            gcp_creds = service_account.Credentials.from_service_account_file(cred_file)
            self.db = firestore.Client(credentials = gcp_creds, project = proj, database = db)

    def getDocumentsByDate(self, date):
        if len(str(date)) == 14:
            date = int(date/1000000)
        if not len(str(date)) == 8:
            self.tls.error(f"Unable to update, Invalid date {date}. Should be 8 digit.")
            return []
        filters = []
        filters.append( FieldFilter("date", ">=", date * 1000000) )
        filters.append( FieldFilter("date", "<=", date * 1000000 + 235959) )
        return self._coreQry(filters)

    def getDocumentsByStatus(self, status="open"):
        filters = []
        filters.append( FieldFilter("status", "==", status) )
        return self._coreQry(filters)

    def getDocumentsByDateCoinStatus(self, date, coin, status="open"):
        if len(str(date)) == 14:
            date = int(date/1000000)
        if not len(str(date)) == 8:
            self.tls.error(f"Unable to update, Invalid date {date}. Should be 8 digit.")
            return []
        filters = []
        filters.append( FieldFilter("status", "==", "open") )
        filters.append( FieldFilter("coin", "==", coin) )
        filters.append( FieldFilter("date", ">=", date * 1000000) )
        filters.append( FieldFilter("date", "<=", date * 1000000 + 235959) )
        return self._coreQry(filters)

    def updateDocument(self, date, coin):
        docs = self.getDocumentsByDateCoinStatus(date, coin, "open")
        if len(docs)==1:
            docId = self._getDocId(docs[0])
            today = self.tls.getDateTimeStamp("%Y%m%d%H%M%S")
            noOfDays = self.tls.getDateDiff(date, today, "%Y%m%d%H%M%S")
            toUpdate = {"winDate": today, "winDuration" : noOfDays, "status" : "pass" }
            self._updateDoc(docId, toUpdate)
            self.tls.info(f"Updated {date} - {coin}")
            return 1
        return 0

    def addDocument(self, data):
        collRef = self.db.collection(self.collectionName)
        docRef = collRef.document()
        docRef.set(data)
        self.tls.info(f"Added: {data}")
        return docRef.id

    def _updateDoc(self, docId, updateDict):
        collRef = self.db.collection(gcpfs.collectionName)
        docRef = collRef.document(docId)
        docRef.update(updateDict)
        self.tls.debug(f"Updating {docId} with {updateDict}")

    def _getDocId(self, doc):
        return doc.to_dict()['_id']

    def _coreQry(self, filters):
        query = self.db.collection(self.collectionName)
        for eachFilter in filters:
            query = query.where(filter = eachFilter)
        docs = query.stream()
        result = []
        for doc in docs:
            doc_data = doc.to_dict()
            doc_data['_id'] = doc.id  # include document id
            result.append(doc_data)
        return result

if __name__ == "__main__":
    gcpfs = GCPFireStore()
    coll = "cryptos"
    # datas = [{'date': 20250521235219, 'coin': 'PI', 'coinslug': 'pi', 'price': 0.81316044474824, 'pricechangepercent': 9.77281953, 'binanceTradeVolPercent': 0.0, 'trend7d': 7, 'trendttl': 117, 'rank': 3195, 'cmcWatchers': 210000, 'cmcStarRating': 0, 'status': 'pass', 'winDate': 20250522061815, 'winDuration': 0, 'isMostVisited': 1, 'isMostTrending': 1, 'isSentimental': 1, 'bullvotes': 1864, 'bearvotes': 206, 'bullpercent': 90, 'bearpercent': 10, 'ttlvotes': 3380, 'trendpercent': 1.5, 'sentimenttype': 'bullish'},
    #         {'date': 20250610023004, 'coin': 'AVAX', 'coinslug': 'avalanche', 'price': 21.31964523555377, 'pricechangepercent': -0.57316786, 'binanceTradeVolPercent': 0.32, 'trend7d': -3, 'trendttl': 235, 'rank': 14, 'cmcWatchers': 1000000, 'cmcStarRating': 4, 'status': 'pass', 'winDate': 20250610034002, 'winDuration': 0, 'isMostVisited': 1, 'isMostTrending': 1, 'isSentimental': 1, 'bullvotes': 86, 'bearvotes': 21, 'bullpercent': 80, 'bearpercent': 20, 'ttlvotes': 234, 'trendpercent': 3.3, 'sentimenttype': 'bullish'}]
    # for eachData in datas:
    #     print("Inserting...",eachData['coin'])
    #     #gcpfs.insert_doc(coll, eachData)

    # filter = { "status": "open" }
    # data = gcpfs.find_docs(collection_name=coll, filter_dict=filter)
    # print(data)
    print("done")
