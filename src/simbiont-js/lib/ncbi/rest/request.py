#  requests.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0
import io
import sys
import time
import urllib.parse
import urllib.request
import urllib.error

class Response:

  def __init__(self):
    self.message = ''
    self.request_error = urllib.error.HTTPError
    self.parser = ''
    self.batch = Batch()
    self.base_url = ''
    self.qry_url = ''

  def get_base_url(self):
    return self.batch.base_url

  def get_query_url(self):
    pass
    #return self.batch.
  def parse(self):
    pass

class Batch:

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
    self.contact = ''

  def prepare_qry(self):
    return {
              'email'   : self.contact,
              'tool'    : self.tool,
              'db'      : self.db,
              'rettype' : self.typ,
              'retmode' : self.mode,
            }

class NcbiRequest:
  """
  The base class for NCBI requests.
  """
  class Requester:

    def __init__(self, wait):
      self.wait = wait
      self.max_retries = 9
      self.timeout = 10

    def request(self, batch, response):
      retries = 0
      success = False
      while success == False:
        wait = self.wait
        try:
          data = urllib.parse.urlencode(batch.prepare_qry()).encode('utf-8')
          response.base_url = batch.url
          response.qry_url = data.decode()
          print(response.base_url, response.qry_url, file=sys.stderr)
          request = urllib.request.Request(batch.url, data=data)
          response.message = urllib.request.urlopen(request, timeout=self.timeout)
        except urllib.error.URLError as url_err:
          print("URL error:", url_err.reason, file=sys.stderr)
          wait = 2
        except urllib.error.HTTPError as http_err:
          print("HTTP error:", httperr.code, http_err.reason, file=sys.stderr)
          if retries > self.max_retries:
            response.request_error = http_err
            print("HTTP error:", http_err.code, http_err.reason, file=sys.stderr)
            #sys.exit("Abort. Retrieving failed after: " + str(retries) + " tries.")
          retries += 1
          wait = 1
        else:
          success = True
        #print("Temporary check. Remove when happy. Sleeping: {0}s".format(wait), file=sys.stderr)
        time.sleep(wait)
      return response

  class Response:

    def __init__(self):
      self.message = ''
      self.request_error = urllib.error.HTTPError
      self.parser = ''
      self.batch = Batch()
      self.base_url = ''
      self.qry_url = ''

    def parse(self):
      pass

  def __init__(self, rest, wait=0.33):
    self.contact = 'jan.buchmann@sydney.edu.au'
    self.baseurl = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    self.uids = []
    self.wait = wait
    self.max_retries = 9
    self.batchsize = 0
    self.requests = []
    self.responses = []
    self.url = self.baseurl + '/' + rest
    self.requester = NcbiRequest.Requester(self.wait)

  def fetch_requests(self):
    for i in self.requests:
      response = NcbiRequest.Response()
      self.responses.append(self.requester.request(i, response))



  def prepare_batch(self, batch):
    batch.contact = self.contact
    batch.url = self.url

  def analyze_responses(self):
    pass

  def request(self, uids, options):
    pass
