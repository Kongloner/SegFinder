#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  cdd.py
#
#  Copyright 2016 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0


import sys
import re
import time
import ncbi.rest

class CDDSearch:
  def __init__(self):
    self.queries = []
    self.qry = {}
    self.url = "http://www.ncbi.nlm.nih.gov/Structure/bwrpsb/bwrpsb.cgi?"
    self.cdsid = ''
    self.rest = ncbi.rest.REST()
    self.args = ''
    self.status = 6

  def init_search(self):
    self.queries = [x for x in sys.stdin]
    self.qry = {
                'useid1'       : 'true' if self.args.useid1 == 1 else 'false',
                'db'           : self.args.db,
                'smode'        : self.args.smode,
                'compbasedadj' : self.args.compbasedadj,
                'filter'       : 'true' if self.args.filter == 1 else 'false',
                'evalue'       : self.args.evalue,
                'maxhit'       : self.args.maxhit,
                'tdata'        : self.args.tdata,
                'alnfmt'       : self.args.alnfmt,
                'dmode'        : self.args.dmode,
                'qdefl'        : 'true' if self.args.qdefl == 1 else 'false',
                'cddefl'       : 'true' if self.args.cddefl == 1 else 'false',
                'clonly'       : 'true' if self.args.clonly == 1 else 'false',
                'queries'      : '\n'.join(x for x in self.queries)
              }

    cdsid = re.compile("^#cdsid")
    status = re.compile("^#status")
    print(self.url)
    for i in self.rest.request(self.url, self.qry).splitlines():
      if cdsid.match(i):
        self.cdsid = i.split()[1].strip()
      if status.match(i):
        self.status = i.split()[1].strip()
        break
    print("Starting search: Request-ID {0}".format(self.cdsid), file=sys.stderr)

  def search(self, args, wait=5):
    self.args = args
    if args.cdsid != None:
      self.cdsid = self.args.cdsid
    else:
      self.init_search()
      time.sleep(wait)
    self.status = self.check()
    print(self.status,file=sys.stderr)
    while(self.status == 3):
      time.sleep(wait)
      self.status = self.check()
      print(self.status, file=sys.stderr)
    self.retrieve()

  def check(self):
    status = re.compile("^#status")
    checkqry = {
                'tdata' : "hits",
                'cdsid' : self.cdsid
               }
    for i in self.rest.request(self.url, checkqry).splitlines():
      if status.match(i):
        return int(i.split()[1].strip())

  def retrieve(self):
    retrieve_qry = {
                    'tdata'   : self.args.tdata,
                    'cddefl'  : self.args.cddefl,
                    'qdefl'   : self.args.qdefl,
                    'dmode'   : self.args.dmode,
                    'clonly'  : self.args.clonly,
                    'cdsid'   : self.cdsid
                    }
    for i in self.rest.request(self.url, retrieve_qry).splitlines():
      print(i)
