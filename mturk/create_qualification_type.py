#! /usr/bin/python

from boto.mturk.connection import MTurkRequestError
from MTurkMappingAfrica import MTurkMappingAfrica

mtma = MTurkMappingAfrica()

mtma.disposeQualificationType()
mtma.createQualificationType()
