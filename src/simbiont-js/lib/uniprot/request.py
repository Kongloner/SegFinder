#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  uniprot/request.py
#
#  Copyright 2015 Jan P Buchmann <lejosh@members.fsf.org>
#   Description:
#     Class to send request to Uniprot in the form shown below:
#     'http://www.uniprot.org/uniprot/?query=family:%22Paramyxoviruses%20fusion%20glycoprotein%20family%22&format=tab'
#  Version: 1.4

import urllib.parse
import urllib.request
import urllib.error
import time
import sys

class Requester:
  def __init__(self):
    self.contact = "jan.buchmann@sydney.edu.au"

  def request(self, url, qry, qry_params):
    qry = url + '?query=' + urllib.parse.quote(qry)
    print("Uniprot query: {0}".format(qry), file=sys.stderr)
    qry_params = urllib.parse.urlencode(qry_params)
    qry_params = qry_params.encode('utf-8')
    request = urllib.request.Request(qry, qry_params)
    request.add_header('User-Agent', 'Python %s' % self.contact)
    success = False
    retries = 0
    while success == False:
      try:
        response = urllib.request.urlopen(request)
      except urllib.error.HTTPError as e:
        if retries > 9:
          print("Error:", e.code, file=sys.stderr)
          return e.code
        retries += 1
        time.sleep(0.5)
      else:
        success = True
        retries = 0
    return(response.read().decode())
