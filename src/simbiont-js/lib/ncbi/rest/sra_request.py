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

class SraBatch:

  def __init__(self):
    self.number = 0
    self.start = 0
    self.size = 0
    self.webenv = ''
    self.query_key = ''
    self.url = ''
    self.tool = ''
    self.db = ''
    self.mode = ''
    self.typ = ''
    self.contact = ''

  def prepare_qry(self):
    return {
              'email'   : self.contact,
              'tool'    : self.tool,
              'db'      : self.db,
              'rettype' : self.typ,
              'retmode' : self.mode,
              'WebEnv'    : self.webenv,
              'query_key' : self.query_key
            }

class NcbiSraRequest(request.NcbiRequest):

  class Response(request.NcbiRequest.Response):

    def __init__(self, parser, db):
      super().__init__()
      self.db = db
      self.sequences = []
      self.parser = parser
      self.parser.db = self.db

    def parse(self):
      self.parser.parse(self.message)
      if self.parser.has_callback == True:
        self.parser.run_callback()


  def __init__(self, wait=0.3):
    super().__init__('sra.cgi?', wait=wait)
    self.baseurl = 'http://trace.ncbi.nlm.nih.gov/Traces/sra/'
    self.mode = 'xml'
    self.typ  = 'runinfo'
    self.db   = 'sra'
    self.batch_size = 500
    self.tool = 'jpb_srafetch'
    self.num_req_uids = 0
    self.expected_batches = 0

  def set_options(self, options):
    if 'wait' in options:
      self.wait = options['wait']

  def fetch_requests(self, parser):
    batch = 0
    fetched_uids = 0
    for i in self.requests:
      batch += 1
      response = self.Response(parser, self.db)
      self.analyze_response(self.requester.request(i, response))
      #self.check_integrity(i, len(response.parser.fetched))
      #fetched_uids += len(response.parser.fetched)
      #self.calc_progress(batch, fetched_uids)
      response.parser.fetched = []

  def analyze_response(self, response):
    response.parse()

  def request(self, parser, webenv, query_key, options={}):
    print("asas")
    self.set_options(options)
    start = 0
    batch_num = 0
    b = SraBatch()
    b.webenv = webenv
    b.query_key = query_key
    b.id = batch_num
    b.tool = self.tool
    b.db   = self.db
    b.typ  = self.typ
    b.mode = self.mode
    b.size = self.batch_size
    b.start = start
    batch_num += 1
    start += self.batch_size
    self.prepare_batch(b)
    self.requests.append(b)
    print(self.requests)
    self.fetch_requests(parser)

  def check_integrity(self, batch, fetched):
    if fetched != batch.size:
      print("Error batch {0}: expected:{1} :: fetched: {2}".format(batch.id,
            batch.size, fetched), file=sys.stderr)

  def calc_progress(self, batch,  fetched):
    print("\rBatch: {0}/{1} :: UIDs: {2}/{3} ({4:.2f})".format(batch,
          self.expected_batches, fetched, self.num_req_uids,
          (fetched/self.num_req_uids)), end='', file=sys.stderr)
