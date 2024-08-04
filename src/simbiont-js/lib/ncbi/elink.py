#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  elink.py
#
#  Copyright 2016 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0


import sys
from . import rest
from . import esearch
class Elink:
  def __init__(self, wait = 0.4):
    self.baseurl = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?"
    self.wait = wait
    self.tool  = 'elink'

  def link(self, db0, db1, ids):
    qry = {
            'dbfrom' : db0,
            'db'     : db1,
            'id'     : '&id='.join(x for x in ids),
            'linkname' : db0 + "_" + db1,
    #        'cmd'    : 'neighbor',
            #'usehistory' : 'y'
          }
    r = rest.REST(self.wait)
    rcvr = esearch.Receiver.string(r.request(self.baseurl, qry))
    #print(rcvr.msg['QueryKey'][0], rcvr.msg['WebEnv'][0], db1, sep='\t')
    m = esearch.Message(rcvr.msg)
    m.show()
