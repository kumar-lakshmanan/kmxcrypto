'''
ktools

Generic tools
@author: Kumaresan
'''
import os, sys

from pathlib import Path
from datetime import timedelta
from decimal import Decimal
from pytz import timezone
from time import strftime

import logging
import logging.config
import logging as log
import socket
import json
import zipfile
import subprocess
import traceback
import datetime
import getpass
import inspect
import locale
import socket
import pprint
import pickle
import random
import shutil
import atexit
import codecs
import time
import uuid
import math
import re

class KTools(object):
    '''
    KTools

    Append tools path and import ktools and create instance as given below.

    import os, sys
    sys.path.append("G:/pythoncodes/KmaxPyLib")

    import ktools

    Use:
    def __init__(self):
        self.tls = ktools.GetKTools()
        self.tls.log.info("JSON Tree")

    # More Config
    - customPyLookUp - Python Module with all look up values. Check the ktoolsDefaultLookUps
    - customConfigFile - JSON Config file to over ride the values in LookUp.

    '''
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("Creating KTools instance...")
            cls._instance = super(KTools, cls).__new__(cls)
        return cls._instance

    def __init__(self, customPyLookUp=None, customJsonConfigFile=None, appName="kmxapp"):
        if not hasattr(self, '_initialized'):
            self.appName = appName
            self.cfgFile = None
            self.cfg = None
            self.qapp = None
    
            self.exitCallBackFn = None
            self.entryCallBackFn = None
            self.logCustomLogPrintFn = None
            self.logFormatter = None
            self.passwordMasking = 1
            self.passwordLists = [] 
            self.allPubSubSignals = {}
    
            if not appName: raise Exception(f"Unknown app or AppName is missing.")
            if not self.isAppNameValid(appName): raise Exception(f"AppName:[{appName}] is not valid.")
    
            self.lookUp = self.setUpLookUp(customPyLookUp)
            self.cfg = self.setUpConfig(customJsonConfigFile)
            self.logSys = self.setUpLogger()
    
            self.randomSeed = self.lookUp.randomSeed + int(self.getDateTime('%I%M%S'))
            self.rand = random.Random(self.randomSeed)
    
            self.noLogPrintOnly = int(self.getSafeConfig(['logging','logProdMode'], 0)) if self.cfg else 0
    
            self.addSysPaths()
            self._initialized = True  # Mark as initialized

    
    def helloworld(self):
        self.info("Hello world from KTools")

    def addSysPaths(self, singlePath='', multiPaths=[]):

        def pathToSysPath(inpPath):
            if inpPath and not inpPath=="":
                inpPath = Path(inpPath)
                inpPath = inpPath.resolve(strict=True)
                if inpPath.is_dir() and not str(inpPath) in os.environ:
                    sys.path.append(str(inpPath))

        #0. Basic System Paths:
        pathToSysPath('.')
        pathToSysPath(Path().cwd())
        for eachPath in Path().cwd().parents:
            pathToSysPath(eachPath)

        #1. add env config sys paths if given:
        envVariable = 'KLIBPATH'
        if envVariable in os.environ:
            for eachPath in os.environ[envVariable].split(';'):
                pathToSysPath(eachPath)

        #2. add config paths if given:
        configSysPaths = self.getSafeConfig(['general','sysPaths'], [])
        for eachPath in configSysPaths:
            pathToSysPath(eachPath)

        #3. addSingleGivenPath
        pathToSysPath(singlePath)

        #4. addMulitpleGivenPath
        for eachPath in multiPaths:
            pathToSysPath(eachPath)

        #Clean/Remove duplicates
        oldSysPaths = sys.path
        newSysPaths = []
        for eachPath in oldSysPaths:
            eachPath = eachPath.strip()
            eachPath = Path(eachPath)
            eachPath = eachPath.resolve(strict=False)
            eachPath = eachPath.absolute()
            eachPath = eachPath.as_posix()
            eachPath = str(eachPath)
            if not eachPath in newSysPaths: newSysPaths.append(eachPath)

        sys.path.clear()

        for eachPath in newSysPaths:
            sys.path.append(eachPath)

    def getSafeConfig(self, lst, default=None):
        current = self.cfg
        for key in lst:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def isAppNameValid(self, appName):
        #AppName - FileName - Should be more then 5 and less then 25 char.
        r1 = 5 <= len(appName) <= 25
        r2 = appName.find(' ') == -1
        return r1 and r2

    def setUpLookUp(self, customPyLookUp=None):
        """
            This is to override the default lookup and use custom lookup.
            Each Projects can have thier own lookups.
            Copy the ktoolsDefaultLookUps.py to your app , rename
            and use it as customLookUp for your project.
            MAKE SURE YOU DONT REMOVE EXISITNG LOOKUPS.
            JUST ADD YOU LOOKUPS. OR MODIFY VALUE OF EXISITNG LOOKUPS.
        """
        if customPyLookUp:
            return customPyLookUp
        else:
            from common_lib import kToolsDefaultLookUps
            return kToolsDefaultLookUps

    def setUpConfig(self, jsonConfigFile=None):
        """
        Read config file and load for internal reference
        """

        self.cfgFile = self.getConfigFile(jsonConfigFile)
        if not self.isFileExists(self.cfgFile):
            self.raiseError(f"CFG file is must. File [{self.cfgFile}] is missing.\nAtleast, set the env variable {self.lookUp.envVarJsonConfigFile} with config.json")
            return None
        else:
            print(f"Loading config: {self.cfgFile}...", end=" ")
            with open(self.cfgFile) as fobj: self.cfg = json.load(fobj)
            print(f"done.")
            return self.cfg

    def setUpLogger(self):
        """
        Logging for your modules.
        Create ttls and start logging like given below
        """
        if hasattr(self, 'logSys') and self.logSys: return self.logSys

        currentConfig = {}
        currentConfig['version'] = 1
        currentConfig['disable_existing_loggers'] = 0
        logging.config.dictConfig(currentConfig)

        for eachHandler in logging.root.handlers:
            logging.root.removeHandler(eachHandler)

        self.logFormatter  = logging.Formatter(fmt=self.cfg["logging"]["logFormat"], datefmt=self.cfg["logging"]["logDateTimeFormat"])
        self.logSys = logging.getLogger(self.appName)
        self.logSys.setLevel(self.cfg["logging"]["logLevel"])
        self.logSys.disabled = self.cfg["logging"]["logDisable"]

        if self.cfg["logging"]["logToConsole"]:
            streamHandler = logging.StreamHandler()
            streamHandler.set_name(f"StreamHandler_{self.appName}")
            streamHandler.setFormatter(self.logFormatter)
            self.logSys.addHandler(streamHandler)

        if self.cfg["logging"]["logToFile"]:
            fileHandler = logging.FileHandler(self.cfg["logging"]["logFile"])
            fileHandler.set_name(f"FileHandler_{self.appName}")
            fileHandler.setFormatter(self.logFormatter)
            self.logSys.addHandler(fileHandler)

        return self.logSys

    def addCustomLogPrinter(self, logCustomLogPrintFn):
        if logCustomLogPrintFn:
            self.logCustomLogPrintFn = logCustomLogPrintFn
            customHandler = CustomLogHandler(self.logCustomLogPrintFn)
            customHandler.set_name(f"CustomHandler_{self.appName}")
            customHandler.setFormatter(self.logFormatter)
            self.logSys.addHandler(customHandler)

    def _logFormatter(self, msg, skipLevel=2):
        fnName, clsName, modName, modFile = self.getCallerInfo(skipLevel)
        if self.cfg and self.cfg["logging"]["logModuleName"]:
            if not clsName:
                return f'[{modName}-{fnName}] {msg}'
            else:
                return f'[{modName}-{clsName}-{fnName}] {msg}'
        else:
            if not clsName: clsName = modName
            return f'[{clsName}-{fnName}] {msg}'

    def passwordCleanInfo(self, msg):
        if self.passwordMasking:
            for each in self.passwordLists:
                if each in msg:
                    mask = 'X' * len(each)
                    msg = msg.replace(each, mask)
        return msg

    def createNewSignalSetup(self, signalName = "default"):
        self.allPubSubSignals[signalName] = signal(signalName) 
        return True
    
    def subscribeToSignal(self, signalName, callBack):
        '''
        Call back when signal appears
        ''' 
        if not signalName in self.allPubSubSignals:
            self.info(f"Signal {signalName} not yet created!")
            return False
        
        curSignal = self.allPubSubSignals[signalName]
        curSignal.connect(callBack)
        return True
    
    def publishSignal(self, signalName, data=None):
        if not signalName in self.allPubSubSignals:
            self.info(f"Signal {signalName} not yet created!")
            return False
        
        curSignal = self.allPubSubSignals[signalName]
        curSignal.send(data)
        return True        

    def alignedParams(self, key, value, justify=25, justfyChar='.'):
        "Display good KEY..........VALUE"
        return str(key).strip().ljust(justify, justfyChar) + str(value).strip()

    def getArgs(self):
        if len(sys.argv) > 1:
            return sys.argv[1:]
        return []

    def isArgPresent(self, checkFor):
        for each in self.getArgs():
            if each.lower().startswith(checkFor.lower()):
                return True
        return False

    def getArgValue(self, argName):
        #['arg="Sdf sd"','fe=xcvx', 'dv=er' ]
        # getArgVALUE('fe') -> xcvx
        if self.isArgPresent(argName):
            for each in self.getArgs():
                if each.lower().startswith(argName.lower()):
                    data = each.split('=')
                    if len(data) == 2:
                        return data[1]
        return ''    

    def prittyPrint(self, data=''):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(data)   

    def info(self, msg, skipLevel=2):
        msg = self._logFormatter(msg, skipLevel)
        msg = self.passwordCleanInfo(msg)
        print(msg) if self.noLogPrintOnly else self.logSys.info(msg)

    def debug(self, msg, skipLevel=2):
        msg = self._logFormatter(msg, skipLevel)
        msg = self.passwordCleanInfo(msg)
        print(msg) if self.noLogPrintOnly else self.logSys.debug(msg)

    def warn(self, msg, skipLevel=2):
        msg = self._logFormatter(msg, skipLevel)
        msg = self.passwordCleanInfo(msg)
        print(msg) if self.noLogPrintOnly else self.logSys.warning(msg)

    def error(self, msg, skipLevel=2):
        msg = self._logFormatter(msg, skipLevel)
        if self.noLogPrintOnly:
            print(msg)
        else:
            self.logSys.error(msg) if hasattr(self, 'logSys') and self.logSys else print(msg)

    def errorAndExit(self, msg, skipLevel=2):
        msg = self._logFormatter(msg, skipLevel)
        if self.noLogPrintOnly:
            print(msg)
        else:
            self.logSys.error(msg) if hasattr(self, 'logSys') and self.logSys else print(msg)
        sys.exit(-1)

    def shellExecuteWait(self, command):
        subprocess.call(command)

    def shellExecuteNoBlock(self, command):
        subprocess.Popen(command)
    
    def shellExecuteWithIO(self, cmdLine, wd, inputs=[], futureArgs={}):
        showWindow = self.getSafeDictValue(futureArgs, 'showWindow', False)
        cmdList = cmdLine.split(' ')
        
        # Hide console window if needed (Windows-specific)
        startupinfo = None
        if os.name == 'nt' and not showWindow:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
        # Start the subprocess
        proc = subprocess.Popen(
            cmdList,
            cwd=os.path.abspath(wd),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            startupinfo=startupinfo
        )
    
        output_lines = []
        isInputAvailable = len(inputs)
        input_iter = iter(inputs)
        
        try:
            for line in proc.stdout:
                output_lines.append(line.rstrip())
                if isInputAvailable:
                    try:
                        # Feed next input line, if available                    
                        next_input = next(input_iter)
                        proc.stdin.write(next_input + '\n')
                        proc.stdin.flush()
                    except StopIteration:
                        pass
    
            proc.wait()
        except Exception as e:
            proc.kill()
            raise e
    
        return output_lines
    
    #------------------------------------------------------------------------
    
    def shellExecuteWithInteractiveIO(self, cliBinary, wd, io=[], lastExpectation="", futureArgs={}):
        '''
        inputs is list of tuples
        should be expectedWord and commandForThat
        ("expected","command For That")
        ("expected1","command For That1")
        ("expected2","command For That2")
        '''
        self.info(f"Executing interactive shell for {cliBinary}")
        timeOut = self.getSafeDictValue(futureArgs, 'timeout', 30)        
        proc = wexpect.spawn(cliBinary, timeout=timeOut)
        outputCollection = ""
        for eachIO in io:
            expectation = eachIO[0]
            commandToExecute = eachIO[1]
            timeCover = eachIO[2] if len(eachIO) >= 3 else 10
            self.debug(f"Expecting [{expectation}] to Execute [{commandToExecute}]")
            matchPos = proc.expect(expectation, timeCover)
            if matchPos >= 0:
                tmp = proc.sendline(commandToExecute)
                outputCollection += proc.before + proc.after
        while (proc.isalive()):
            proc.expect(lastExpectation)
            outputCollection += proc.before + proc.after
            proc.close()
        outputCollection = outputCollection.replace('\r\n', '\n')
        return outputCollection
    
    def fileLauncherWithBin(self, bin, fileToOpen):
        cmd = f'"{bin}" "{fileToOpen}"'
        self.shellExecuteNoBlock(cmd)

    def raiseError(self, msg='Technical Error'):
        self.error(f"Technical Error: {msg}")
        raise Exception(msg)

    def doSystemErrorHandle(self, expType, expVal, traceBack):
        lastErrorInfo = self.getLastErrorInfo(expType, expVal, traceBack)
        if not 'No error' in lastErrorInfo:
            lastError = traceback.format_exception(expType, expVal, traceBack)
            lastErrorInfo = ""
            for eachLine in lastError:
                lastErrorInfo += eachLine
            errorContent = f"\nError happend on {strftime('%Y-%m-%d %I:%M:%S %p')}\n{lastErrorInfo}"
        else:
            errorContent = f"\nNo system error on {strftime('%Y-%m-%d %I:%M:%S %p')}"
        self.error(errorContent, 4) if hasattr(self, 'logSys') else print(errorContent)
        #print(errorContent)
        fileName = f"error_{strftime('%Y%m%d')}.log"
        self.writeFileContent(fileName, errorContent, 'a')

    def doEntryStartUp(self):
        self.info(f"Starting app {self.appName} startup activity....")
        if hasattr(self, 'entryCallBackFn') and self.entryCallBackFn: self.entryCallBackFn()
        self.info(f"App {self.appName} initialized.")

    def doExitCleanUp(self):
        self.info(f"Starting app {self.appName} shutdown cleanup activity....")
        if hasattr(self, 'exitCallBackFn') and self.exitCallBackFn: self.exitCallBackFn()
        self.info(f"Thank you for using the app {self.appName}.")

    def encrypt(self, text, cryptoKey=None):
        cryptoKey = cryptoKey if cryptoKey else self.lookUp.ciperKey
        cipher = ''
        for each in text:
            c = (ord(each) + int(cryptoKey)) % 126
            if c < 32: c += 31
            cipher += chr(c)
        return cipher

    def decrypt(self, text, cryptoKey=None):
        cryptoKey = cryptoKey if cryptoKey else self.lookUp.ciperKey
        plaintext = ''
        for each in text:
            p = (ord(each) - int(cryptoKey)) % 126
            if p < 32: p += 95
            plaintext += chr(p)
        return plaintext

    def printObjInfos(self, obj):
        lst = self.getObjInfos(obj)
        for each in lst:
            info = f'{each[0]} - {each[1]}'
            self.debug(info)
            print(info)

    def getCallerInfo(self, skipLevel=1):
        fnName, clsName, modName, modFile = "", "", "", ""
        try:
            stack = inspect.stack()
            stack = stack[skipLevel + 1:]
            if len(stack) > 0:
                entry = stack[0]
                if len(entry) > 3:
                    fcode = entry[0]
                    fnName = str(entry[3])
                    clsName = ''
                    modName = ''
                    modFile = str(entry[1])
                    if hasattr(fcode, 'f_locals'):
                        lcls = fcode.f_locals
                        if 'self' in lcls:
                            selfObj = lcls['self']
                            if selfObj:
                                clsName = str(selfObj.__class__.__name__)
                                modName = str(selfObj.__module__)
                        else:
                            modName = os.path.basename(modFile)
                            modName = os.path.splitext(modName)[0]
                    else:
                        modName = os.path.basename(modFile)
                        modName = os.path.splitext(modName)[0]
        except:
            return fnName, clsName, modName, modFile
        return fnName, clsName, modName, modFile

    def getLastErrorInfo(self, expType=None, expVal=None, traceBack=None, skipLevel=1):
        if traceBack!=None:
            lastErrorData = traceback.format_tb(traceBack)
        elif expVal!=None and traceBack==None:
            lastErrorData = expVal.__str__()
        else:
            lastErrorData = traceback.format_exc()

        if 'NoneType: None' in lastErrorData:
            errorContent = f"No error found recently."
        else:
            errorContent = f"Error happend on {strftime('%Y-%m-%d %I:%M:%S %p')}\n{lastErrorData}"
        return errorContent

    def getTraceInfo(self, skipLevel=1):
        stack = inspect.stack()
        stack = stack[skipLevel + 1:]
        stack = reversed(stack)
        traceInfo = ''
        head = '\nTraceback (code reference)\n'
        for each in stack:
            mod = each[1]
            lineNo = str(each[2])
            fn = each[3]
            line = str(each[4][0]).strip() if each[4] else ''
            traceInfo += f'\n File "{mod}", line {lineNo}, in {fn}'
            traceInfo += f'\n {line}'
            traceInfo += f'\n'
        traceInfo = head + traceInfo.strip()
        return traceInfo

    def getRandom(self, stop, start=0):
        return self.rand.randrange(start, stop)

    def getSystemName(self):
        return str(socket.gethostname())

    def getCurrentPath(self):
        return os.path.abspath(os.curdir)

    def getCurrentUser(self):
        return getpass.getuser()

    def getRelativeFolder(self, folderName):
        return os.path.join(self.getCurrentPath(), folderName)

    def getDateCalc(self, addRemoveDays=0, format='%Y-%m-%d', fromDate=None):
        fromDate = fromDate if fromDate else datetime.datetime.today() 
        res = fromDate + timedelta(days=addRemoveDays)
        return res.strftime(format)

    def getDateCalcObj(self, addRemoveDays=0, fromDate=None):
        fromDate = fromDate if fromDate else datetime.datetime.today() 
        res = fromDate + timedelta(days=addRemoveDays)
        return res

    def getDateTimeObjFor(self, input, format='%Y-%m-%d'):
        return datetime.datetime.strptime(str(input), format)

    def getDateTimeForObj(self, dateTimeObj, format='%Y%m%d %H%M%S'):
        return dateTimeObj.strftime(format)

    def getDateBetweenTwoDate(self, startDate, endDate, format='%Y%m%d'):
        sdate = self.getDateTimeObjFor(startDate, format)   # start date
        edate =self.getDateTimeObjFor(endDate, format)   # end date
        lst = [sdate+timedelta(days=x) for x in range((edate-sdate).days)]
        nlst = []
        for each in lst: nlst.append(self.getDateTimeForObj(each, format))
        return nlst

    def getMissingDatesInList(self, startDate, endDate, crossCheckList):
        notToday = True
        cdateStr = startDate
        cdateObj = self.getDateTimeObjFor(startDate, '%Y%m%d')
        missingDateFor = []
        while(notToday):
            if cdateStr == endDate:
                notToday = False
            else:
                cdateObj = self.getDateCalcObj(1, cdateObj)
                cdateStr = self.getDateTimeForObj(cdateObj, '%Y%m%d')
                if not cdateStr in crossCheckList:
                    missingDateFor.append(cdateStr)
        return missingDateFor
    
    def getDictDefault(self, inputDict, keyName, defaultValue):
        return self.getSafeDictValue(inpDict, keyName, defaultValue)
    
    def getDictSpecifics(self, inputDict, *keys):
        newDict = {}
        for eachKey in keys:
            newDict[eachKey] = self.getDictDefault(inputDict, eachKey, None) 
        return newDict
    
    def getDictFormatted(self, inputDict):
        return pprint.pprint(inputDict)
        
    def getDateDiff(self, date1, date2, format='%Y-%m-%d'):
        '''
        ret 1 means date1 is 1 day old than date 2
        ret 0 measn both are same
        ret -1 means date1 is 1 day after date2
        '''
        d1 = self.getDateTimeObjFor(date1, format)
        d2 = self.getDateTimeObjFor(date2, format)
        res = d2 - d1
        return res.days

    def getDateTimeStamp(self, format="%Y%m%d%H%M%S"):
        return self.getDateTime(format)

    def getDateTime(self, format='%Y%m%d'):
        """
        "%Y-%m-%d %H:%M:%S"
        Directive Meaning Notes
        %a Locale's abbreviated weekday name.
        %A Locale's full weekday name.
        %b Locale's abbreviated month name.
        %B Locale's full month name.
        %c Locale's appropriate date and time representation.
        %d Day of the month as a decimal number [01,31].
        %H Hour (24-hour clock) as a decimal number [00,23].
        %I Hour (12-hour clock) as a decimal number [01,12].
        %j Day of the year as a decimal number [001,366].
        %m Month as a decimal number [01,12].
        %M Minute as a decimal number [00,59].
        %p Locale's equivalent of either AM or PM. (1)
        %S Second as a decimal number [00,61]. (2)
        %U Week number of the year (Sunday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Sunday are considered to be in week 0. (3)
        %w Weekday as a decimal number [0(Sunday),6].
        %W Week number of the year (Monday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Monday are considered to be in week 0. (3)
        %x Locale's appropriate date representation.
        %X Locale's appropriate time representation.
        %y Year without century as a decimal number [00,99].
        %Y Year with century as a decimal number.
        %Z Time zone name (no characters if no time zone exists).
        %% A literal "%" character.
        """
        format = format if format else self.cfg["general"]["dateTimeFormat"]
        now_utc = datetime.datetime.now(timezone('UTC'))
        now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
        return now_asia.strftime(format)
        #return datetime.datetime.now().strftime(format)
    
    def getTimeStamp(self):
        return self.getDateTime(self.cfg["general"]["timeStampFormat"])

    def getTemp(self):
        return self.cfg["folders"]["temp"]

    def getUUID(self):
        return str(uuid.getnode())

    def getUUID4(self):
        return str(uuid.uuid4())

    def getObjInfos(self, obj):
        infos = []
        members = inspect.getmembers(obj)
        for eachMember in members:
            obj = eachMember[1]
            mem = eachMember[0]
            tp = 'Obj'
            if inspect.isfunction(obj) or inspect.ismethod(obj):
                tp = 'Fn'
            elif inspect.isbuiltin(obj):
                tp = 'Fn-BuiltIn'
            elif inspect.isclass(obj):
                tp = 'Class'
            elif inspect.ismodule(obj):
                tp = 'Module'
            elif inspect.iscode(obj):
                tp = 'Code'
            elif (type(obj) is type(1) or
                type(obj) is type('') or
                type(obj) is type([]) or
                type(obj) is type(()) or
                type(obj) is type({})
              ):
                tp = 'Variable'
            elif type(obj) is type(None):
                tp = 'Obj'
            else:
                tp = 'Obj'

            infos.append([mem, tp, eachMember[1]])
        return infos

    def getConfigFile(self, customJsonConfigFile=None):
        """
            Returns config file to be used.

            Order:
                1. Parameter / Argument
                2. Env Variable with LookUp Name
                3. Default LookUp File Or Overriden LookUp
                3. Relative File
        """
        nowFile = customJsonConfigFile
        if nowFile and os.path.exists(nowFile) and os.path.isfile(nowFile):
            return os.path.abspath(nowFile)

        nowFile = self.lookUp.envVarJsonConfigFile
        nowFile = os.getenv(nowFile)
        if nowFile and os.path.exists(nowFile) and os.path.isfile(nowFile):
            return os.path.abspath(nowFile)

        nowFile = self.lookUp.JsonConfigFile
        if nowFile and os.path.exists(nowFile) and os.path.isfile(nowFile):
            return os.path.abspath(nowFile)

        return "config.json"

    def getRandom(self, stop, start=0):
        return self.rand.randrange(start, stop)

    def getSystemName(self):
        return str(socket.gethostname())

    def getCurrentPath(self):
        return os.path.abspath(os.curdir)

    def getCurrentUser(self):
        return getpass.getuser()

    def getRelativeFolder(self, folderName):
        return os.path.join(self.getCurrentPath(), folderName)

    def getSafeDictValue(self, inpDict, keyToLookUp, defaultValue=None):
        finValue = defaultValue
        if type(inpDict) == type({}): 
            if keyToLookUp in inpDict.keys():
                return inpDict[keyToLookUp]            
        return finValue

    def convertDictStrToDict(self, strDict):
        return json.loads(strDict)

    def convertDictToDictStr(self, dictObj):
        return json.dumps(dictObj)

    def isNotPresentInDict(self, inThisDict, checkForThis):
        return not checkForThis in inThisDict.keys()

    def isWindows(self): return os.name == 'nt'
    
    def isLinux(self): return os.name == 'posix'
        
    def isLocalDev(self):
        if self.isWindows():
            if 'COMPUTERNAME' in os.environ:
                if os.environ['COMPUTERNAME'].upper() == self.cfg.desktopName.upper():
                    return 1
        return 0    
    
    def isItMorning(self):
        return self.getDateTime('%p').lower() == 'am'

    def addOnlyUniqueToDict(self, inThisDict, keyToAdd, valueToAdd, forceAddLatest=0):
        if self.isNotPresentInDict(inThisDict, keyToAdd):
            inThisDict[keyToAdd] = valueToAdd
        else:
            if forceAddLatest:
                inThisDict[keyToAdd] = valueToAdd
                self.error(f"{keyToAdd} is not unique. Updating same with new value!")
            else:
                self.error(f"{keyToAdd} is not unique. Not adding new!")

    def createZip(self, folderToCompress, outputZipFile):
        with zipfile.ZipFile(outputZipFile, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folderToCompress):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folderToCompress)  # Preserve folder structure
                    zipf.write(file_path, arcname)

    def getFileContent(self, fileName):
        f = open(fileName, "r")
        content = str(f.read())
        f.close()
        return content

    def writeFileContent(self, fileName, data, mode='w'):
        f = open(fileName, mode, encoding='utf-8')
        f.write(str(data))
        f.close()

    def cleanFolder(self, folder):
        folder = os.path.abspath(folder)
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

    def copyFile(self, src, dst):
        src = os.path.abspath(src)
        dst = os.path.abspath(dst)
        shutil.copy(src, dst)

    def copyFolderSpl(self, src, dst):
        src = os.path.abspath(src)
        dst = os.path.abspath(dst)
        shutil.copytree(src, dst)

    def copyFolder(self, source_folder, destination_folder, latest_overwrite=1, forced_overwrite=0, verbose=1):
        source_folder = os.path.abspath(source_folder)
        destination_folder = os.path.abspath(destination_folder)
        for root, dirs, files in os.walk(source_folder):
            for item in files:
                src_path = os.path.join(root, item)
                dst_path = os.path.join(destination_folder, os.path.basename(src_path))
                if os.path.exists(dst_path):
                    if (not forced_overwrite and not latest_overwrite):
                        if(verbose):
                            self.info("Already exist, Skipping..." + src_path + " to " + dst_path)
                    if (not forced_overwrite and latest_overwrite):
                        if os.stat(src_path).st_mtime > os.stat(dst_path).st_mtime:
                            if(verbose):
                                self.info("Overwriting latest..." + src_path + " to " + dst_path)
                            shutil.copy2(src_path, dst_path)
                    if (forced_overwrite):
                        if(verbose):
                            self.info("Forced Overwriting..." + src_path + " to " + dst_path)
                        self.forceDeleteFile(dst_path)
                        shutil.copy2(src_path, dst_path)
                else:
                    if(verbose):
                        self.info("Copying..." + src_path + " to " + dst_path)
                    shutil.copy2(src_path, dst_path)
            for item in dirs:
                src_path = os.path.join(root, item)
                dst_path = os.path.join(destination_folder, src_path.replace(source_folder, ""))
                if not os.path.exists(dst_path):
                    if(verbose):
                        self.info("Creating folder..." + dst_path)
                    os.mkdir(dst_path)
        if(verbose):
            print("Copy process completed!")

    def forceDeleteFile(self, fpath):
        try:
            os.remove(fpath)
        except PermissionError:
            self.debug("Force delete: " + fpath)
            subprocess.run(["cmd", "/c", "del", "/F", "/Q", fpath], shell=False)

    def isListedItemPresentInText(self, lookUpList = [], searchInText=""):
        checkIsPresent = lambda lookUpList, searchInText: any(word in searchInText for word in lookUpList)
        return checkIsPresent(lookUpList, searchInText)

    def getFileList(self, dirToScan, ext=".py", allowed=[], disallowed=[]):
        """Recursively lists all files with the given extension in a directory and its subdirectories.

        Args:
            directory (str): The root directory to scan.
            extension (str): The file extension to look for (e.g., ".txt").

        Returns:
            list: A list of file paths matching the extension.
        """
        matched_files = []

        for root, _, files in os.walk(dirToScan):
            for file in files:
                if file.endswith(ext):
                    if allowed and disallowed and self.isListedItemPresentInText(allowed, file) and not self.isListedItemPresentInText(disallowed, file):
                        matched_files.append(os.path.abspath(os.path.join(root, file)))
                    elif allowed and not disallowed and self.isListedItemPresentInText(allowed, file):
                        matched_files.append(os.path.abspath(os.path.join(root, file)))
                    elif not allowed and disallowed and not self.isListedItemPresentInText(disallowed, file):
                        matched_files.append(os.path.abspath(os.path.join(root, file)))
                    elif not allowed and not disallowed:
                        matched_files.append(os.path.abspath(os.path.join(root, file)))

        return matched_files

    def _buildCallerPath(self, parentOnly=0):
        stack = inspect.stack()
        path = ""
        for eachStack in stack:
            if("self" in eachStack[0].f_locals.keys()):
                the_class = eachStack[0].f_locals["self"].__class__.__name__
                the_method = eachStack[0].f_code.co_name
                if(the_class != "basic"):
                    if(parentOnly):
                        path = "{}.{}()->".format(the_class, the_method)
                    else:
                        path += "{}.{}()->".format(the_class, the_method)
        return path

    def makeEmptyFile(self, fileName):
        fileName = os.path.abspath(fileName)
        self.makePathForFile(fileName)
        self.writeFileContent(fileName, '')

    def makePathForFile(self, file):
        file = os.path.abspath(file)
        base = os.path.dirname(file)
        self.makePath(base)

    def makePath(self, path):
        path = os.path.abspath(path)
        if(not os.path.exists(path) and path != ''):
            os.makedirs(path)
        else:
            self.warn("Path exists " + path)

    def isFileExists(self, path):
        return os.path.isfile(path) and os.path.exists(path) and path != '' and path is not None

    def isFolderExists(self, path):
        return os.path.isdir(path) and os.path.exists(path) and path != '' and path is not None

    def isItFile(self, path):
        return os.path.isfile(path) and path != '' and path is not None

    def isItFolder(self, path):
        return os.path.isdir(path) and path != '' and path is not None

    def getFileParts(self, fileNameWithPath):
        if self.isItFile(fileNameWithPath):
            filePath = os.path.dirname(fileNameWithPath)
            fileName = os.path.basename(fileNameWithPath)
            fileName,fileExt = os.path.splitext(fileName)
            return filePath, fileName, fileExt
        else:
            return None, None, None

    def pathClean(self, inputFile):
        inputFile = os.path.normpath(inputFile)
        inputFile = os.path.abspath(inputFile)
        return inputFile

    def pathParts(self, inputFile):
        inputFile = self.pathClean(inputFile)
        fileNameWithExt = os.path.basename(inputFile)
        fileName, Ext = os.path.splitext(fileNameWithExt)
        filePath = os.path.dirname(inputFile)
        Ext = Ext[1:] if Ext.startswith('.') else Ext
        return filePath, fileName, Ext
    
    def pathReady(self, inputPath):
        inputPath = self.pathClean(inputPath)
        if os.path.exists(inputPath):
            return inputPath
        if os.path.isfile(inputPath):
            inputPath, fileName, Ext = self.pathParts(inputPath)
        os.makedirs(inputPath)
        return inputPath

    def pathJoin(self, basePath, *joins):
        finPath = basePath
        for each in joins:
            finPath = os.path.join(finPath, each)
        return self.pathClean(finPath)    
    
    def readyCachePath(self):
        if self.isLocalDev(): self.pathReady(self.localCachePath)
        
    def isCacheAvailable(self, fileName, dated=0):
        if dated: fileName = self._cacheName(fileName)
        fileName = self._applyLocalCachePath(fileName)
        return os.path.exists(fileName)

    def getCache(self, fileName, defaultData=None, dated=0):
        if dated: fileName = self._cacheName(fileName)
        fileName = self._applyLocalCachePath(fileName)
        if self.isCacheAvailable(fileName):
            #self.debug(f'Reading cache {fileName}')
            f = open(fileName, 'rb')
            data = pickle.load(f)
            f.close()
        else:
            self.debug(f'Cache not found: {fileName}')
            self.setCache(fileName, defaultData)
            data = defaultData
        return data
    
    def setCache(self, fileName, data, dated=0):
        if dated: fileName = self._cacheName(fileName)
        fileName = self._applyLocalCachePath(fileName)
        self.debug(f'Writing cache {fileName}')
        picData = pickle.dumps(data)
        f = open(fileName, 'wb')
        f.write(picData)
        f.close()
    
    def _applyLocalCachePath(self, fileName):
        localCachePath = self.getSafeConfig(["folders", "cache"], ".")
        self.pathReady(localCachePath)
        return self.pathJoin(localCachePath, fileName)

    def _cacheName(self, fileName):
        nw = self.getDateTime('%Y%m%d')
        cacheName = f'{nw}_{fileName}'
        return cacheName        

    def pickleSaveObject(self, obj, file=""):
        if(obj is None):
            self.log.error("Pass me valid object to save" + obj)
        className = obj.__class__.__name__
        if(file is None or file == ""):
            file = className + ".txt"
        base = os.path.dirname(file)
        if(not os.path.exists(base) and base != ''):
            os.makedirs(base)
        f = open(file, "wb")
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        f.close()
        self.log("Saved!" + className + "-" + file)

    def pickleLoadObject(self, file):
        x = None
        if(file is None or file == ""):
            self.log.error("Pass me file name to read and pass the object")
        if(os.path.exists(file)):
            try:
                f = open(file, "rb")
                x = pickle.load(f)
                f.close()
                self.log.info ("File read and obj returned " + file + " obj: " + x.__class__.__name__)
            except:
                self.log.error ("Error loading the pickle. Passing default!")
        else:
            self.log.error ("Error! File doesn't exist " + file)
        return x

    def shortHandNumberConverter(self, value: str) -> int:
        """
        Converts shorthand notation like '1K', '2.5M', '3T', '0.4P' into integers.
    
        Supports:
            K = Thousand (1_000)
            M = Million (1_000_000)
            B = Billion (1_000_000_000)
            T = Trillion (1_000_000_000_000)
            P = Quadrillion (1_000_000_000_000_000)
    
        Args:
            value (str): Input string, e.g., '720K', '1.5M', '2B'
    
        Returns:
            int: Equivalent integer value
    
        Raises:
            ValueError: If format is unrecognized
        """
        multipliers = {
            'K': 1_000,
            'M': 1_000_000,
            'B': 1_000_000_000,
            'T': 1_000_000_000_000,
            'P': 1_000_000_000_000_000,
        }
    
        value = value.strip().upper().replace(',', '')
        
        if not value:
            raise ValueError("Empty value")
    
        suffix = value[-1]
    
        if suffix in multipliers:
            num_part = value[:-1]
            try:
                return int(float(num_part) * multipliers[suffix])
            except ValueError:
                raise ValueError(f"Invalid numeric part: {num_part}")
        elif value.isdigit():
            return int(value)
        else:
            raise ValueError(f"Unrecognized format: {value}")

    def doBackup(self, srcFile, bckUpToPath=1, bckUpPath='G:/pythonworkspace/myscripts/dataBackup', bckUpFmt='[FILENAME]_BKUP[TIMESTAMP].[EXT]'):
        self.debug('Backup Src: ' + srcFile)
        if not os.path.exists(srcFile):
            self.raiseError(
                'Unable to do old as src file not found ' + srcFile)
            return 0
        timeStamp = self.getDateTime('%Y%m%d%H%M%S')
        filePath, fileName, Ext = self.pathParts(srcFile)
        dstPath = self.pathReady(
            bckUpPath) if bckUpToPath else self.pathClean('.')
        dstFileName = bckUpFmt
        dstFileName = dstFileName.replace('[FILENAME]', fileName)
        dstFileName = dstFileName.replace('[TIMESTAMP]', timeStamp)
        dstFileName = dstFileName.replace('[EXT]', Ext)
        dstFile = self.pathJoin(dstPath, dstFileName)
        self.debug('Backup Dst: ' + dstFile)
        self.copyFile(srcFile, dstFile)
        self.debug('Backup Done!')
        return 1

    def raiseError(self, msg='CustomError'):
        raise Exception(msg)    

    def smartBool(self, s):
        if s is True or s is False: return s
        s = str(s).strip().lower()
        return not s in ['false', 'f', 'n', '0', '']

def handleUnknownException(expType, expVal, traceBack):
    """
    To capture last error happend, invoked by sys exception hook
    sys.excepthook = handleUnknownException
    """
    tls = GetKTools()
    if tls:
        tls.doSystemErrorHandle(expType, expVal, traceBack)
    else:
        lastErrorInfo = traceback.format_exc()
        lastErrorInfo = lastErrorInfo.strip()
        if lastErrorInfo == "NoneType: None" or lastErrorInfo == "None":
            lastError = traceback.format_exception(expType, expVal, traceBack)
            lastErrorInfo = ""
            for eachLine in lastError:
                lastErrorInfo += eachLine
        errorContent = f"\nError happend on {strftime('%Y-%m-%d %I:%M:%S %p')}\n{lastErrorInfo}"
        try:
            print(f'--------\n{errorContent}--------')
            f = open(f"error_{strftime('%Y%m%d')}.log", "a")
            f.write(errorContent)
            f.close()
            sys.exit()
        except IOError:
            pass

def handleAppExit():
    '''
    Invoke if app terminate due to error or shutdown by user
    Check doExitCleanUp
    '''
    tls = GetKTools("AppError")
    if tls:
        tls.doExitCleanUp()
    else:
        print('App shutdown initiated, Unable to do ktool based cleanup explicitly.')
        print('Hope, App handled exit cleanup activity internally.')
        print('Anyway, Thank you for using the app.')

def GetKTools(appName=None, customLookUp=None, customJsonConfigFile=None) -> KTools:
    """
        Creates single tool instance common for entire project.
        Optional you can provide custom lookups and configs
    """

    gblKey = 'KAppName'
    gbl = globals()
    if gblKey in gbl: appName = gbl[gblKey]
    if not appName: appName = os.path.basename(sys.argv[0])
    currentApp = appName.strip().lower().replace('.py','').replace(' ','').upper()

    if currentApp:
        if currentApp in gbl:
            tls = gbl[currentApp]
            #tls.debug(f"Using existent ktool instance for app: {currentApp}")
        else:
            print(f"Creating new ktool instance for app: {currentApp}")
            gbl[currentApp] = KTools(customLookUp, customJsonConfigFile, currentApp)
            gbl[gblKey] = currentApp
            # Handle Unknown Exceptions and AppExit
            sys.excepthook = handleUnknownException
            atexit.register(handleAppExit)

            # App Startup
            gbl[currentApp].doEntryStartUp()
        return gbl[currentApp]
    else:
        print("Missing app name. Unable to create ktools.")
        sys.exit()
        return None
