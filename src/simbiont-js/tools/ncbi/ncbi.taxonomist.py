#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  ncbi.taxonomist.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0


import sys
import argparse
import os
sys.path.insert(1, os.path.join(sys.path[0], '../../lib'))
import ncbi.rest.taxonomy_request
import ncbi.eutils.esearch
import ncbi.parser.taxonomy.taxonomist

class TaxonomyParser(ncbi.parser.taxonomy.taxonomist.Taxonomist):

  def __init__(self):
    super().__init__()
    self.has_callback = True
    self.fetched = 0
    self.callback_style = 0
    self.sep = "\t"

  def add_options(self, args):
    self.sep = args.sep
    if args.decode_qry == True:
      self.callback_style = 1

  def run_callback(self):
    self.fetched = len(self.lineages)
    if self.callback_style == 1:
      for i in self.lineages:
        lin = self.sep.join(x.name for x in i.export())
        print(i.query.taxid, i.query.name, lin, sep=self.sep)
    else:
      for i in self.lineages:
        i.print_lineage()
    self.lineages = []

def main():
  ap = argparse.ArgumentParser(description='Fetch taxonomies from NCBI')
  ap.add_argument('--uids', '-u', nargs='*'),
  ap.add_argument('--wait', '-w', type=float, help='Seconds to wait between requests'),
  #ap.add_argument('--term', '-t', type=str),
  ap.add_argument('--batch_size', '-s', type=int, help='Set batch size', default=500),
  ap.add_argument('--sep', type=str, help='Set separator. Default: tab', default='\t'),
  ap.add_argument('--decode_qry', '-d', action='store_true', help='Show query taxid, query name, query lineage', default=500),
  #ap.add_argument('--fetch', '-f', action='store_true'),
  #ap.add_argument('--limit','-l', type=int, default=0,    help='Set maximum number of uids to retrieve.  Default: all')
  args = ap.parse_args()

  tr = ncbi.rest.taxonomy_request.NcbiTaxonomyRequest()
  ids = []
  if args.uids:
    ids = [x.rstrip() for x in args.uids]
  else:
    for i in sys.stdin:
      ids.append(i.rstrip())
  tp = TaxonomyParser()
  tp.add_options(args)
  tr.request(ids, options={'wait' : args.wait, 'batch_size' : args.batch_size}, parser=tp)
  return 0

if __name__ == '__main__':
  main()
