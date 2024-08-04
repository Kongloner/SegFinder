#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  esummary.py
#
#  Copyright 2016 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0


import sys
from rest import REST
import esearch

class Esummary:

  def __init__(self, wait = 0.4):
    self.url = "esummary.fcgi?"
    self.wait = wait
    self.tool  = 'esummary'

  def summarize(self, db, ids=None, webenv=None, query_key=None):
    qry = {'db' : db}
    if not ids:
      qry['WebEnv'] = webenv
      qry['query_key'] = query_key
    else:
      qry['id'] = ','.join(x for x in ids)

    r = REST(self.wait)
    rcvr = esearch.Receiver.string(r.request(self.url, qry))
    m = esearch.Message(rcvr.msg)
    m.show()
