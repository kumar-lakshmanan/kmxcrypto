import functions_framework

import mainDailyPNLAndSentimentCollector
from common_lib import kTools
from lib import utilities
from lib import fetcher    
import mainDailyPNLWinnersCheck
from common_lib import kDatabase

tls = kTools.KTools()
tls.logSys.setLevel("INFO")

@functions_framework.http
def mymainfunction(request):
    tls.info("Incoming request...")
    request_json = request.get_json(silent=True)
    request_args = request.args
    tls.info("Params: " + str(request_args))
    tls.info("Payload: " + str(request_json))

    ret = None
    if request_args and 'action' in request_args:
        action = request_args['action']
        param1 = tls.getSafeDictValue(request_args,'param1', None)
        param2 = tls.getSafeDictValue(request_args, 'param2', None)
        param3 = tls.getSafeDictValue(request_args, 'param3', None)
        param4 = tls.getSafeDictValue(request_args, 'param4', None)

        if action == "runcheck":
            tls.info("Performing winner check")
            ret = mainDailyPNLWinnersCheck.doWinnerCheck()

        if action == "fetchcoin":
            tls.info("Fetching new coins")
            ret = mainDailyPNLAndSentimentCollector.fetchTodaysCoin(param1)

        if action == "dbcheck":
            tls.info("Testing DB Connection....")
            db = kDatabase.SimpleMySql()
            db.connect()
            db.close()
            tls.info("Able to connect!!")

    tls.info("Request Done")
    return str(ret)
