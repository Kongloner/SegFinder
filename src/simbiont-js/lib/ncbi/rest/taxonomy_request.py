#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  taxonomy_request.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0

import io
import sys
import math
from . import request
from .. parser import taxonomy_request_parser

class TaxonomyTermBatch:
  def __init__(self):
    self.number = 0
    self.start = 0
    self.size = 0
    self.qry = ''
    self.url = ''
    self.tool = ''
    self.db = ''
    self.mode = ''
    self.typ = ''
    self.term = ''
    self.contact = ''


  def prepare_qry(self):
    return {
            'email'   : self.contact,
            'tool'    : self.tool,
            'db'      : self.db,
            'rettype' : self.typ,
            'retmode' : self.mode,
            'term'    : self.term
            }

class TaxonomyBatch:

  def __init__(self):
    self.number = 0
    self.start = 0
    self.size = 0
    self.qry = ''
    self.url = ''
    self.tool = ''
    self.db = ''
    self.mode = ''
    self.typ = ''
    self.ids = ''
    self.contact = ''


  def prepare_qry(self):
    return {
            'email'   : self.contact,
            'tool'    : self.tool,
            'db'      : self.db,
            'rettype' : self.typ,
            'retmode' : self.mode,
            'id'      : self.ids
            }

class NcbiTaxonomyRequest(request.NcbiRequest):

  class Response(request.NcbiRequest.Response):

    def __init__(self, parser, db):
      super().__init__()
      self.db = db
      self.parser = parser
      self.parser.db = self.db

    def parse(self):
      self.parser.parse(self.message)
      if self.parser.has_callback == True:
        self.parser.run_callback()

  def __init__(self, wait=0.3):
    super().__init__('efetch.fcgi', wait=wait)
    self.mode = 'xml'
    self.typ  = ''
    self.db   = 'taxonomy'
    self.batch_size = 500
    self.tool = 'simbiont::taxonomist'
    self.num_req_uids = 0
    self.expected_batches = 0

  def set_options(self, options):
    self.wait = options.pop('wait', self.wait)
    self.batch_size = options.pop('batch_size', self.batch_size)
    print("Taxonomist:: mode: {0}\nDatabase: {1}\nBatch size: {2}".format(self.mode,
           self.db, self.batch_size), file=sys.stderr)

  def fetch_requests(self, parser):
    batch = 0
    total_fetched_uids = 0
    for i in self.requests:
      batch += 1
      response = self.Response(parser, self.db)
      self.analyze_response(self.requester.request(i, response))
      total_fetched_uids += response.parser.fetched
      self.check_integrity(i, response.parser.fetched)
      self.calc_progress(batch, total_fetched_uids)

  def analyze_response(self, response):
    response.parse()

  def request(self, uids, options={}, parser=taxonomy_request_parser.NcbiTaxonomyRequestParser()):
    self.set_options(options)
    self.num_req_uids = len(uids)
    self.expected_batches = math.ceil(self.num_req_uids/self.batch_size)
    start = 0
    batch_num = 0
    batch_size = self.batch_size
    while start < self.num_req_uids:
      if start + batch_size  > self.num_req_uids:
        batch_size = self.num_req_uids - start
      b = TaxonomyBatch()
      b.id = batch_num
      b.tool = self.tool
      b.db   = self.db
      b.typ  = self.typ
      b.mode = self.mode
      b.size = batch_size
      b.start = start
      b.ids = ','.join(x for x in uids[start:start+self.batch_size])
      batch_num += 1
      start += self.batch_size
      self.prepare_batch(b)
      self.requests.append(b)
    self.fetch_requests(parser)

  def check_integrity(self, batch, fetched):
    if fetched != batch.size:
      print("Error batch {0}: expected:{1} :: fetched: {2}".format(batch.id,
            batch.size, fetched), file=sys.stderr)

  def calc_progress(self, batch,  fetched):
    print("\rBatch: {0}/{1} :: UIDs: {2}/{3} ({4:.2f})".format(batch,
          self.expected_batches, fetched, self.num_req_uids,
          (fetched/self.num_req_uids)), end='', file=sys.stderr)
