from datetime import datetime
from webob import Request, Response
from ProcessNotifications import ParseRestNotification, ProcessNotifications
from MTurkMappingAfrica import MTurkMappingAfrica

def application(environ, start_response):
    req = Request(environ)
    res = Response()

    notiftime = str(datetime.today())
    mtma = MTurkMappingAfrica()

    # Get serialization lock.
    mtma.getSerializationLock()

    logFilePath = mtma.projectRoot + "/log"
    k = open(logFilePath + "/notifications.log", "a")

    now = str(datetime.today())
    k.write("\ngetnotifications: datetime = %s\n" % now)
    k.write("getnotifications: notification arrived = %s\n" % notiftime)

    try:
        restNotification = ParseRestNotification(req.params)
        msgOK = True
    except:
        msgOK = False

    k.write("getnotifications: REST message parsed and verified: %s\n" % msgOK)

    if msgOK:
        ProcessNotifications(mtma, k, restNotification.notifMsg)

    now = str(datetime.today())
    k.write("getnotifications: processing completed = %s\n" % now)

    k.close()

    # Commit any uncommitted changes
    mtma.dbcon.commit()

    # Release serialization lock.
    mtma.releaseSerializationLock()

    # Destroy mtma object.
    del mtma

    return res(environ, start_response)
