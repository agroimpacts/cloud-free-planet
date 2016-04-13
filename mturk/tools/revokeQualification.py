from boto.mturk.connection import MTurkRequestError,MTurkConnection
from MTurkMappingAfrica import MTurkMappingAfrica
from datetime import datetime

mtma = MTurkMappingAfrica(debug=0)

workerId = raw_input("Please enter a Worker ID: ")

now = str(datetime.today())

mtma.revokeQualificationUnconditionally(workerId, now)
print("Mapping Africa Qualification revoked from worker %s" % workerId)
