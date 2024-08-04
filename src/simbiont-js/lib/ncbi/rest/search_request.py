#  search.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0

import io
import sys
import xml.etree.ElementTree as ET
from . import request

class NcbiSearch:

  def __init__(self, request, term='', followUp=False):
    self.term = term
    self.number = request.follow_ups
    self.url = request.url
    self.tool = request.tool
    self.db = request.db
    self.mode = request.mode
    self.typ = request.typ
    self.usehistory = True
    self.contact = request.contact
    self.webenv = request.webenv
    self.query_key = request.query_key
    self.retstart = request.retstart
    self.retmax = request.retmax
    self.isFollowUp = followUp

  def prepare_qry(self):
    if self.isFollowUp == True:
      return {
                'tool'      : self.tool,
                'email'     : self.contact,
                'db'        : self.db,
                'retmax'    : self.retmax,
                'retstart'  : self.retstart,
                'WebEnv'    : self.webenv,
                'query_key' : self.query_key,
                'retmode'   : self.mode,
                'rettype'   : self.typ
             }
    return {
              'email'   : self.contact,
              'usehistory' : self.usehistory,
              'tool'    : self.tool,
              'db'      : self.db,
              'rettype' : self.typ,
              'retmax'  : self.retmax,
              'retmode' : self.mode,
              'term'    : self.term
            }
"""
  Class handling search requests to NCBI. The class inherits the request base
  class NcbiRequest.
  https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch
"""
class NcbiSearchRequest(request.NcbiRequest):

  class Response(request.NcbiRequest.Response):

    def __init__(self, parser, uids):
      super(NcbiSearchRequest.Response, self).__init__()
      self.parser = parser
      self.count = 0
      self.retmax = 100000
      self.retstart = 0
      self.query_key = ''
      self.webenv = ''
      self.uids = uids

    def parse(self):
      self.parser.parse(self.message, self)

  def __init__(self):
    super(NcbiSearchRequest, self).__init__('esearch.fcgi?')
    self.mode = 'xml'
    self.typ  = 'docsum'
    self.db   = 'pubmed'
    self.retmax = 100000
    self.retstart = 0
    self.usehistory = 'y'
    self.tool = 'jpb_esarch'
    self.limit = 0
    self.uids = []
    self.response = ''
    self.follow_ups = 0
    self.webenv = ''
    self.query_key = ''

  def set_options(self, options):
    if 'db' in options:
      self.db = options['db']
    if 'rettype' in options:
      self.typ = options['rettype']
    if 'wait' in options:
      self.wait = options['wait']
    if 'usehistory' in options:
      if options['usehistory'] == True:
        self.usehistory = 'y'
    if 'limit' in options:
      self.limit = int(options['limit'])

  def fetch_requests(self, parser):
    response = self.Response(parser, self.uids)
    response.retmax = self.retmax
    self.response = self.requester.request(self.requests[0], response)
    self.response.parse()
    if self.requests[0].number == 0:
      if self.limit == 0:
        self.limit = self.response.count
      self.expected_batches = int(self.limit/self.retmax)
    self.show_progress()

  def search(self, parser, term, options={}):
    self.set_options(options)
    if self.limit != 0 and self.limit < self.retmax:
      self.retmax = self.limit
    s = NcbiSearch(self, term)
    self.prepare_batch(s)
    self.requests.append(s)
    self.fetch_requests(parser)
    self.webenv = self.response.webenv
    self.query_key = self.response.query_key

    while len(self.uids) < self.limit:
      self.retstart = self.retstart + self.retmax
      if self.limit < self.retmax + self.retstart:
        self.retmax = self.limit -self.retstart
      self.follow_ups += 1
      s = NcbiSearch(self, followUp=True)
      self.requests[0] = s
      self.fetch_requests(parser)

  def show_progress(self):
    print("Batch {0}/{1}, retstart {2}::retmax {3}::limit {4}::uids {5}".format(
           self.follow_ups+1,self.expected_batches,self.retstart,self.retmax,
           self.limit,len(self.uids)), file=sys.stderr)
