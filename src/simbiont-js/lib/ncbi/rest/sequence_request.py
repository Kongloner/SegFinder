#  request_sequences.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0

import sys
import math
from . import request
from .. parser import sequence_request_parser
"""
  The NcbiSequenceRequest class handles NCBI sequence requests.
  Since it's based on fetching UIDs, tere is the idea to creat an
  UID fetcher class which will serve as base for all kinds of UID requetse,
  e.g. taxonomy
  https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.EFetch
"""

class SequenceResponse(request.Response):

  def __init__(self):
    super().__init__()

class SequenceBatch(request.Batch):

  def __init__(self):
    super().__init__()
    self.ids = ''

  def prepare_qry(self):
    return {
              'email'   : self.contact,
              'tool'    : self.tool,
              'db'      : self.db,
              'rettype' : self.typ,
              'retmode' : self.mode,
              'id'      : self.ids
            }

class NcbiSequenceRequest(request.NcbiRequest):

  class Response(request.NcbiRequest.Response):

    def __init__(self, parser, db):
      super(NcbiSequenceRequest.Response, self).__init__()
      self.db = db
      self.parser = parser
      self.parser.db = self.db

    def parse(self):
      self.parser.parse(self.message)

  def __init__(self, wait=0.3):
    super().__init__('efetch.fcgi', wait=wait)
    print("30.05.2017 : Changed order of request arguments", file=sys.stderr)
    self.mode = 'xml'
    self.typ  = 'fasta'
    self.db   = 'sequences'
    self.batch_size = 500
    self.tool = 'jpbnsf'
    self.num_req_uids = 0
    self.expected_batches = 0

  def set_options(self, options):
    self.wait = options.pop('wait', self.wait)
    self.typ  = options.pop('rettype', self.typ)
    self.db   = options.pop('db', self.db)
    self.batch_size = options.pop('batch_size', self.batch_size)
    print("Mode: {0}\nDatabase: {1}\nBatch size: {2}\nRettype: {3}".format(self.mode,
           self.db, self.batch_size, self.typ), file=sys.stderr)

  def fetch_requests(self, parser):
    batch = 0
    fetched_uids = 0
    for i in self.requests:
      batch += 1
      response = self.Response(parser, self.db)
      self.analyze_response(self.requester.request(i, response))
      fetched_uids += response.parser.fetched
      self.check_integrity(i, response.parser.fetched)
      self.calc_progress(batch, fetched_uids)

  def analyze_response(self, response):
    response.parse()

  def request(self, uids, options={}, parser=sequence_request_parser.NcbiSimpleSequenceRequestParser()):
    self.set_options(options)
    self.num_req_uids = len(uids)
    self.expected_batches = math.ceil(self.num_req_uids/self.batch_size)
    start = 0
    batch_num = 0
    batch_size = self.batch_size
    while start < self.num_req_uids:
      if start + batch_size  > self.num_req_uids:
        batch_size = self.num_req_uids - start
      b = SequenceBatch()
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
      print("Error for batch # {0}: expected:{1} :: fetched: {2}".format(batch.id,
            batch.size, fetched), file=sys.stderr)

  def calc_progress(self, batch,  fetched):
    print("\rBatch: {0}/{1} :: UIDs: {2}/{3} ({4:.2f})".format(batch,
          self.expected_batches, fetched, self.num_req_uids,
          (fetched/self.num_req_uids)), end='', file=sys.stderr)
