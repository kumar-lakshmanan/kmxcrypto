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


class GeneralServices():

    def __init__(self):
        self.tls = kTools.KTools()

    def isProdLiveData(self):
        return (self.tls.isProd() and not self.tls.isLocal()) or self.tls.kdata['uselivedata']

    def getPercentaged(self, mainValue, percentage):
        '''
        How much value it will increase or decrease for the given Percentage
        '''
        return mainValue * (percentage/100)
        
    def getPercentageIncrDecr(self, mainValue, percentage):
        '''
        How much value it will increase or decrease for the given Percentage
        '''
        return mainValue + self.getPercentaged(mainValue, percentage)
    
    def getPercentageDifference(self, startValue, endValue):
        '''
        How much percent its increased or decreased between these too
        '''
        return ((endValue - startValue) / abs(startValue)) * 100
    
    def isPercentageAchived(self, startValue, endValue, percentage):
        return self.getPercentageDifference(startValue, endValue) >= percentage