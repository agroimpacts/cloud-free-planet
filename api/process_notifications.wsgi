from datetime import datetime
from webob import Request, Response
from ProcessNotifications import ParseRestNotification, ProcessNotifications
from MTurkMappingAfrica import MTurkMappingAfrica

def application(environ, start_response):
    req = Request(environ)
    res = Response()

    now = str(datetime.today())

    mtma = MTurkMappingAfrica()
    logFilePath = mtma.projectRoot + "/log"
    k = open(logFilePath + "/notifications.log", "a")

    # Get serialization lock.
    mtma.getSerializationLock()

    k.write("\ngetnotifications: datetime = %s\n" % now)

    try:
        restNotification = ParseRestNotification(req.params)
        msgOK = True
    except:
        msgOK = False

    k.write("getnotifications: REST message parsed and verified: %s\n" % msgOK)

    if msgOK:
        ProcessNotifications(mtma, k, restNotification.notifMsg)

    # Release serialization lock.
    mtma.dbcon.commit()
    # Destroy mtma object.
    del mtma
    k.close()

    return res(environ, start_response)
