#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  uniprot/fetch.py
#
#  Copyright 2015 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#   Moduel to prep a fetch request from Uniprot
#  Version: 1.4

import sys
import request

class Fetcher:
  def __init__(self):
    self.url='http://www.uniprot.org/uniprot/'
    self.params = []

  def fetch(self, qry, cols, fmt = 'tab', lim = 0):
    #qry = ','.join(str(x) for x in qry)
    params = { 'columns' : cols,
               'format'  : fmt,
               'limit'   : lim}
    r = request.Requester()
    self.response = r.request(self.url, qry, params)
    return self.response

  def show(self):
    for i in self.response.splitlines():
      print(i)
