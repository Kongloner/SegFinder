#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#  \file esearch.py
#  \copyright 2015-2018 The University of Sydney
#  \author: Jan P Buchmann <lejosh@members.fsf.org>
#  \version 1.0.0
#  \description: Searching NCBI from the command line using EDirect.
#
# (("Bacteria"[Organism]) AND genome[title]) AND "Yersinia pestis"[porgn]
# (("Bacteria"[Organism] OR "Bacteria Latreille et al. 1825"[Organism]) AND genome[title]) AND "Yersinia pestis"[porgn] AND plasmid[filter]
# (("Bacteria"[Organism] OR "Bacteria Latreille et al. 1825"[Organism]) AND genome[title]) AND "Vibrio cholerae"[porgn]
#-------------------------------------------------------------------------------
import sys
import argparse
import os

sys.path.insert(1, os.path.join(sys.path[0], '../../include/blib/ncbi/src'))
import edirect.esearch.esearch_analyzer
import edirect.esearch.esearcher

class SimpleAnalyzer(edirect.esearch.esearch_analyzer.EsearchAnalyzer):

  def __init__(self):
    super().__init__()

  def analyze_result(self):
    print("Db: {}\nCount: {}\nQueryKey: {}\nWebenv: {}".format(self.result.db,
                                                               self.result.count,
                                                               self.result.querykey,
                                                               self.result.webenv))
  def analyze_error(self):
    print("Error: {}".format(self.error))

def main():
  ap = argparse.ArgumentParser(description='Search NCBI using EDirect')
  ap.add_argument('--email', '-e', type=str, required=True,
                  help='Email address for requests')
  ap.add_argument('--query', '-q', type=str, required=True,
                  help='Search query')
  ap.add_argument('--database', '-db', type=str, required=True,
                  help='NCBI database. Default: sequences' )
  ap.add_argument('--rettype', '-t', type=str,
                  help='Set rettype.  Default: docsum')
  ap.add_argument('--retmode','-m', type=str, default='json',
                  help='Set retmode.  Default: json')
  ap.add_argument('--apikey','-k', type=str, default=None,
                  help='NCBI API key')
  args = ap.parse_args()

  es = edirect.esearch.esearcher.Esearcher('SimbiontEsearch', args.email, arg.apikey)

  es.search(args.query,
            analyzer=SimpleAnalyzer(),
            options={'db':args.database,
                     'rettype':args.rettype,
                     'retmode':args.retmode})
  return 0

if __name__ == '__main__':
  main()
