#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  uniprot/map.py
#
#  Copyright 2015 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#   Moduel to prep a map request from Uniprot
#  Version: 1.4

import sys
import request

class Mapper:
  def __init__(self):
    self.url='http://www.uniprot.org/mapping/'

  def map(self, qry, fmt_in, fmt_out):
    params = {}
    params['to']     = fmt_out
    params['from']   = fmt_in
    params['format'] = 'tab'
    qry  = ','.join(str(i) for i in qry)
    r = request.Requester()
    self.response = r.request(self.url, qry, params)
    return self.response

  def show(self):
    for i in self.response:
      print(i, self.response[i])
