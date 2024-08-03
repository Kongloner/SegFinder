#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  efetch.py
#
#  Copyright 2015 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#   Class to use NCBI's REST interface to fetch data using efetch [0,1]
#
# [0] http://www.ncbi.nlm.nih.gov/books/NBK25497/
# [1] http://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.EFetch
#  Version: 0

import io
import re
import sys
import xml.etree.ElementTree as ET
from ..rest import sequence_request
from ..parser import sequence_request_parser

class Efetcher:

  def __init__(self, wait=0.3):
    self.wait  = wait
    self.fetched = []
    self.expected_batches = 0
    self.batch_start = 0

  def add_parser(self, parser):
    self.parser = parser
    self.parser.fetched = self.fetched

  def fetch(self, uids, options={}):
    r = sequence_request.NcbiSequenceRequest()
    r.request(uids, options)

  def get_erroneous_uids(self, expected, fetched):
    exp_dict = {x.a:0 for x in fetched}
    print("Erroneous sequences: ",file=sys.stderr)
    for i in fetched:
      if i.accver in exp_dict:
        exp_dict.pop(i.accver)
      elif i.gi in exp_dict:
        exp_dict.pop(i.gi)
      else:
        i.show()


#class NcbiTaxonomyFetcher(NcbiEfetch):

  #def __init__(self, batch_size = 500, wait = 0.33):
    #super(NcbiTaxonomyFetcher, self).__init__(batch_size, wait)
    #self.tool = 'NcbiTaxonomyFetcher'
    #self.mode = 'xml'
    #self.unit = 'taxa'
    #self.typ = ''
    #self.db = 'taxonomy'
