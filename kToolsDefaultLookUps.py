'''
KTools Configuration

#Desc:
All CONSTANTS, STRING HARD CODES. SETTINGS ARE PRESENT HERE

#Usage (Via KTOOLS):
self.lookUp = self.tls.setUpLookUp(customPyLookUp)
self.lookUp.JsonConfigFile

#Also:
KTOOLS.GETPARAMETER

'''
__app__ = 'KDefApp'
__appName__ = 'KMX Default App'
__desc__ = 'KDefault App - Default template for any apps'
__creater__ = 'Kumaresan Lakshmanan'
__date__ = '2025-01-12'
__version__ = '0.0.1'
__updated__ = '2025-03-09'
__release__ = 'Test'

versionStr = "v%s" % __version__
versionInfo ='%s (%s)' % (versionStr, __updated__)
contactInfo = 'Contact kaymatrix@gmail.com for more info.'

#Env Variables
envVarJsonConfigFile = 'K_CONFIG'       #Config File location
envVarIsProd = 'K_ISPROD'               #Is it Prod

#More Config
lookUpType = 'static'
JsonConfigFile = 'config.json'
ciperKey = 4132                         #Four digit secret key
randomSeed = 54