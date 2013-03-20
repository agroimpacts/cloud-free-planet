from datetime import datetime
from webob import Request, Response
from ProcessNotifications import ParseRestNotification, ProcessNotifications
from MTurkMappingAfrica import MTurkMappingAfrica

def application(environ, start_response):
    req = Request(environ)
    res = Response()

    now = str(datetime.today())

    mtma = MTurkMappingAfrica()
    mtma.cur.execute("select value from configuration where key = 'ProjectRoot'")
    logFilePath = mtma.cur.fetchone()[0] + "/log"
    mtma.close()
    k = open(logFilePath + "/notifications.log", "a")
    k.write("\ngetnotifications: datetime = %s\n" % now)

    try:
        restNotification = ParseRestNotification(req.params)
        msgOK = True
    except:
        msgOK = False

    k.write("getnotifications: REST message parsed and verified: %s\n" % msgOK)
    k.close()

    if msgOK:
        ProcessNotifications(restNotification.notifMsg)

    return res(environ, start_response)
