import kTools
from lib import utilities
from lib import local_firestore
from lib import gcp_firestore

class WinnerChecker():

    def __init__(self):
        self.tls = kTools.KTools()
        self.utls = utilities.GeneralServices()

        if self.utls.isProdLiveData():
            self.gfs = gcp_firestore.GCPFireStore()
        else:
            self.lfs = local_firestore.LocalFireStore()

    def getCurrentOpenItems(self):
        if self.utls.isProdLiveData():
            openDocs = self.gfs.getDocumentsByStatus("open")
        else:
            openDocs = self.lfs.getDocumentsByStatus("open")
            openDocs = self.lfs.convertDocsToDict(openDocs)
        return openDocs

    def updateWinner(self, entryDate, coin):
        if self.utls.isProdLiveData():
            self.gfs.updateDocument(entryDate, coin)
        else:
            self.lfs.updateDocument(entryDate, coin)

class FetchCoin():
    def __init__(self):
        self.tls = kTools.KTools()
        self.utls = utilities.GeneralServices()

        if self.utls.isProdLiveData():
            self.gfs = gcp_firestore.GCPFireStore()
        else:
            self.lfs = local_firestore.LocalFireStore()

    def getTodaysCollection(self):
        if self.utls.isProdLiveData():
            todaysCollection = self.gfs.getDocumentsByDate(int(self.tls.getDateTimeStamp("%Y%m%d")))
        else:
            todaysCollection = self.lfs.getDocumentsByDate(int(self.tls.getDateTimeStamp("%Y%m%d")))
            todaysCollection = self.lfs.convertDocsToDict(todaysCollection)
        return todaysCollection

    def addToCollection(self, data):
        if self.utls.isProdLiveData():
            return self.gfs.addDocument(data)
        else:
            return self.lfs.addDocument(data)

if __name__ == "__main__":
    # wc = WinnerChecker()
    # wc.getCurrentOpenItems()

    fc = FetchCoin()
    docs = fc.getTodaysCollection()
    print(docs)

