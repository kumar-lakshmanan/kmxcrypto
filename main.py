import os

import functions_framework

import kTools
import main_winner_check
import main_fetch_coins

tls = kTools.KTools()

tls.turnDebugLogs(not tls.isProd())
tls.logSkipFor.append("CoinMarketCap")

tls.info("Kapp Initializing")
tls.info("Env : " + str(os.environ))
tls.info("Production mode: " + str(tls.isProd() and not tls.isLocal()))

# http://192.168.29.185:8080/?action=runcheck

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
            ret = main_winner_check.doWinnerCheck()

        if action == "fetchcoin":
            tls.info("Fetching new coins")
            ret = main_fetch_coins.doFetchCoin(param1)




    tls.info("Request Done")
    return str(ret)
