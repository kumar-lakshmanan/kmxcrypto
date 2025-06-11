import kTools
from lib import local_firestore
from lib import gcp_firestore

class WinnerChecker():

    def __init__(self):
        self.tls = kTools.KTools()
        self.lfs = local_firestore.LocalFireStore()
        self.gfs = gcp_firestore.GCPFireStore()

    def getCurrentOpenItems(self):
        if self.tls.isProd() and not self.tls.isLocal():
            openDocs = self.gfs.getDocumentsByStatus("open")
        else:
            openDocs = self.lfs.getDocumentsByStatus("open")
            openDocs = self.lfs.convertDocsToDict(openDocs)
        return openDocs

    def updateWinner(self, entryDate, coin):
        if self.tls.isProd() and not self.tls.isLocal():
            self.gfs.updateDocument(entryDate, coin)
        else:
            self.lfs.updateDocument(entryDate, coin)

class FetchCoin():
    def __init__(self):
        self.tls = kTools.KTools()
        self.lfs = local_firestore.LocalFireStore()
        self.gfs = gcp_firestore.GCPFireStore()

    def getTodaysCollection(self):
        if self.tls.isProd() and not self.tls.isLocal():
            todaysCollection = self.gfs.getDocumentsByDate(int(self.tls.getDateTimeStamp("%Y%m%d")))
        else:
            todaysCollection = self.lfs.getDocumentsByDate(int(self.tls.getDateTimeStamp("%Y%m%d")))
            todaysCollection = self.lfs.convertDocsToDict(todaysCollection)
        return todaysCollection

    def addToCollection(self, data):
        if self.tls.isProd() and not self.tls.isLocal():
            return self.gfs.addDocument(data)
        else:
            return self.lfs.addDocument(data)

if __name__ == "__main__":
    # wc = WinnerChecker()
    # wc.getCurrentOpenItems()

    fc = FetchCoin()
    docs = fc.getTodaysCollection()
    print(docs)

