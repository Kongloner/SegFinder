#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#  \file efetch.py
#  \author Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  \copyright 2018 The University of Sydney
#  \version 1.0.1
#  \description A simple Edirect fetch example
#-------------------------------------------------------------------------------

import sys
import argparse
import os

sys.path.insert(1, os.path.join(sys.path[0], '../../include/blib/ncbi/src'))
import edirect.efetch.efetch_analyzer
import edirect.efetch.efetcher

class SimpleAnalyzer(edirect.efetch.efetch_analyzer.EfetchAnalyzer):

  def __init__(self):
    super().__init__()

  def analyze_result(self, request):
    if self.response_format == 'xml':
      print(request.response.getvalue())
    else:
      print(request.response)

  def analyze_error(self, request):
    if self.response_format == 'xml':
      print(request.response.getvalue())
    else:
      print(request.response)

def main():
  ap = argparse.ArgumentParser(description='Fetch NCBI entries using EDirect')
  ap.add_argument('--email', '-e', type=str, required=True,
                  help='Email address for requests')
  ap.add_argument('--uids', '-u', nargs='*', required=True,
                  help='Uid to fetch')
  ap.add_argument('--database', '-db', type=str, required=True,
                  help='NCBI database. Default: sequences' )
  ap.add_argument('--rettype', '-t', type=str,
                  help='Set rettype.  Default: docsum')
  ap.add_argument('--retmode','-m', type=str, default='json',
                  help='Set retmode.  Default: json')
  ap.add_argument('--request_size','-s', type=int, default=500,
                  help='Set request size.  Default (max): 500')
  args = ap.parse_args()
  uids = args.uids
  if len(uids) == 0:
    for i in sys.stdin:
      uids.append(i.strip())

  ef = edirect.efetch.efetcher.Efetcher('SimbiontEfetch', args.email)

  ef.fetch(uids,
           analyzer=SimpleAnalyzer(),
           options={'db':args.database,
                    'rettype':args.rettype,
                    'retmode':args.retmode})
  return 0

if __name__ == '__main__':
  main()
