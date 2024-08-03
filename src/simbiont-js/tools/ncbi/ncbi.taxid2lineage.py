#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  ncbi.taxid2lineage.py
#
#  Copyright 2016 USYD
#  Author: Jan Piotr Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0.0

import io
import os
import sys
import argparse

sys.path.insert(1, os.path.join(sys.path[0], '../../lib'))
import taxonomy.ncbi
import ncbi.efetch

class Printer:

  def run(self, response):
    t = taxonomy.ncbi.Taxonomist()
    msg = io.StringIO(response.message)
    t.parse(msg)
    msg.close()
    for i in t.lineages:
      i.print_lineage()

class Fetcher:

  def __init__(self):
    pass

  def fetch(self, taxids):
    p = Printer()
    tf = ncbi.efetch.NcbiTaxonomyFetcher()
    tf.fetch(taxids, callback=p)

def main():
  ap = argparse.ArgumentParser(description='Taxid2Linage')
  ap.add_argument('--taxid', '-t', nargs='*')
  args= ap.parse_args()

  f = Fetcher()
  if args.taxid:
    f.fetch([x.rstrip() for x in args.taxid])
  else:
    f.fetch([x.rstrip() for x in sys.stdin])
  return 0

if __name__ == '__main__':
  main()
