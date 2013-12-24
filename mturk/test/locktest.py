#! /usr/bin/python

import time
from MTurkMappingAfrica import MTurkMappingAfrica

# Usage
mtma = MTurkMappingAfrica()

mtma.getSerializationLock()
print "I acquired the lock"

time.sleep(10)

mtma.releaseSerializationLock()
print "I released the lock"
