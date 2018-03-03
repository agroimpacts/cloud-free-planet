import subprocess
from webob import Request, Response
import psycopg2
import datetime
from MappingCommon import MappingCommon

def application(environ, start_response):
    req = Request(environ)
    res = Response()

    now = str(datetime.datetime.today())

    mapc = MappingCommon()
    logFilePath = mapc.projectRoot + "/log"

    k = open(logFilePath + "/OL.log", "a")
    k.write("\nputkml: datetime = %s\n" % now)

    kmlName = req.params['kmlName']

    kmlTypeDescr = mapc.getKmlTypeDescription(kmlName)
    k.write("putkml: OL reported 'save' without polygons for %s kml = %s\n" % (kmlTypeDescr, kmlName))

    assignmentId = req.params['assignmentId']
    tryNum = int(req.params['tryNum'])
    if len(assignmentId) > 0 and tryNum == 0:
        k.write("putkml: Mapping assignment ID = %s\n" % assignmentId)
    elif len(assignmentId) > 0 and tryNum > 0:
        k.write("putkml: Training assignment ID = %s; try %d\n" % (assignmentId, tryNum))
    else:
        k.write("putkml: Standalone invocation\n")

    del mapc
    k.close()
    return res(environ, start_response)
