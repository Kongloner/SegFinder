#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#  \file ncbi.taxonomist.py
#  \author Jan P Buchmann <lejosh@members.fsf.org>
#  \copyright 2017-2018 The University of Sydney
#  \version 1.0.1
#  \description NCBI Taxonomist parses NCBI taxonomies. The class parses the
#               corresponding XML and assembles lineages.
#-------------------------------------------------------------------------------

import os
import io
import sys
import argparse


sys.path.insert(1, os.path.join(sys.path[0], '../../include/blib/ncbi/src'))
sys.path.insert(1, os.path.join(sys.path[0], '../../include/blib/taxonomy/src'))
import edirect.efetch.efetcher
import edirect.edbase.edanalyzer
import taxonomist

class TaxonomyAnalyzer(edirect.edbase.edanalyzer.EdAnalyzer):

  def __init__(self, taxonomist):
    super().__init__()
    self.taxonomist = taxonomist
    self.queries = {}

  def parse(self, request):
    request.response = io.StringIO(request.response.read().decode())
    self.analyze_result(request)

  def analyze_result(self, request):
    self.queries.update(self.taxonomist.parse(request.response))

  def dump_database(self, sink=None):
    self.taxonomist.store_query_lineages(self.queries)
    self.taxonomist.dump_database(sink)

  def dump_list(self):
    for i in self.queries:
      self.taxonomist.get_clade_from_taxid(i)
    clades = self.taxonomist.get_clades()
    for i in clades:
      print('\t'.join(['taxid']+[x for x in self.taxonomist.get_clade_ranks(i)]))
      for j in clades[i].lineages:
        lin = clades[i].get_normalized_lineage(j)
        if lin[-1].taxid != j[-1].taxid:
          lin.append(self.taxonomist.taxa[j[-1].taxid])
        print('\t'.join(map(str, [lin[-1].taxid]+[x.name for x in lin])))


def main():
  ap = argparse.ArgumentParser(description='Fetch taxonomies from NCBI')
  ap.add_argument('--ids', '-i', nargs='*', required=True,
                  help='NCBI taxids. Space separated. \
                        If omitted STDIN is read one id per line'),
  ap.add_argument('--email', '-e', type=str ,required=True,
                   help='user email')
  ap.add_argument('--apikey', '-k', type=str,
                   help='NCBI API key')
  ap.add_argument('--dump_list', action='store_true',
                   help='Dump results as tab-delimited list')
  ap.add_argument('--dump_sql', action='store_true',
                   help='Dump results as sqlite3 database')
  ap.add_argument('--dump_file', type=str, default=None,
                   help='Name of dump file. Default: stdout')
  args = ap.parse_args()

  ids = []
  if args.ids:
    ids = [int(x.rstrip()) for x in args.ids]
  else:
    for i in sys.stdin:
      ids.append(int(i.rstrip()))
  analyzer = TaxonomyAnalyzer(taxonomist.NcbiTaxonomist())
  fetcher = edirect.efetch.efetcher.Efetcher('simbiontTaxonomist', args.email)
  fetcher.fetch(ids, options={'db': 'taxonomy', 'retmode': '', 'rettype':'xml'},
                analyzer=analyzer)
  if args.dump_sql:
    analyzer.dump_database(args.dump_file)
  if args.dump_list:
    analyzer.dump_list()
  return 0

if __name__ == '__main__':
  main()
