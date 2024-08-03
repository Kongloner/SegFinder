#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  esearch.py
#
#  Copyright 2015 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#   Class to use NCBI's REST interface to search data using esearch [0]
#
# ToDo: - to use 'usehistory', pipe several esearches together, therby passing
#         the WebEnv and query_key as inputs
# [0] http://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch
#  Version: 0

import io
import sys
import json
import xml.etree.ElementTree as ET
from ..rest import search_request
from ..rest import sra_request
from ..parser import search_request_parser

class Esearcher:

  def __init__(self, usehistory=True, wait=0.3):
    self.wait  = wait
    self.useHistory = usehistory
    self.uids = []

  def search(self, term, options={}):
    sr = search_request.NcbiSearchRequest()
    sr.search(search_request_parser.EsearchResponseParser(), term, options)
    self.uids = sr.uids

class SraSearcher:

  def __init__(self, wait=0.3):
    self.wait  = wait
    self.useHistory = True
    self.uids = []
    self.webenv = ''
    self.webkey = ''

  def search(self, term, options={}):
    sr = search_request.NcbiSearchRequest()
    sr.search(search_request_parser.EsearchResponseParser(), term, options)
    self.uids = sr.uids
    self.webenv = sr.webenv
    self.query_key = sr.query_key
    sra = sra_request.NcbiSraRequest()
    #print(sra)
    sra.request(search_request_parser.EsearchResponseParser(), self.webenv, self.query_key, options)
  #def searchSRA(self, term, retmax = def_retmax):
    #qry = {
           #'db'         : 'sra',
           #'term'       : term,
           #'tool'       : self.tool,
           #'retmax'     : retmax,
           #'retmode'    : 'json',
           #'usehistory' : 'y'
          #}

    #r = rest.REST(self.wait)
    #response = json.loads(r.request(self.url, qry))
    #idlist = response['esearchresult']['idlist']
    #print("Found following Ids: ", *idlist, file=sys.stderr)
    #qrykey = response['esearchresult']['querykey']
    #webkey = response['esearchresult']['webenv']
    #url_sra = 'http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi'
    #sra_params = {
                  #'db'        : 'sra',
                  #'save'      : 'efetch',
                  #'rettype'   : 'runinfo',
                  #'WebEnv'    : response['esearchresult']['webenv'],
                  #'query_key' : response['esearchresult']['querykey']
                 #}
    #print(r.request(url_sra, sra_params))
