import functions_framework
from common_lib import kTools
from lib import utilities
from lib import fetcher    
import mainDailyPNLWinnersCheck

tls = kTools.KTools()
tls.logSys.setLevel("INFO")

@functions_framework.http
def mymainfunction(request):
    request_json = request.get_json(silent=True)
    request_args = request.args
    tls.info(request_args)
    tls.info(request_json)
    ret = (0,0)
    if request_args and 'name' in request_args:
        param = request_args['name']
        if param == "runcheck":
            tls.info("Performing winner check")
            ret = mainDailyPNLWinnersCheck.doWinnerCheck()
    return str(ret)
