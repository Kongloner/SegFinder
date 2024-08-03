#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  uniprot.map.py
#
#  Copyright 2015 Jan P Buchmann <lejosh@members.fsf.org>
#   Description:
#     A wrapper for the Uniprot website to map accessions from one database to
#     another via the URL (REST)[0].
#
# [0]: http://www.uniprot.org/help/programmatic_access
#  Version: 1.4

import re
import sys
import argparse
sys.path.insert(0, '/home/jan/simbiont/lib/uniprot')
import map

def main():
  argparser = argparse.ArgumentParser(description='Map src-identifier \
    to dest-identifier from STDIN via Uniprot')
  argparser.add_argument('-src', type=str, default = 'ACC',
                         help = 'Map from format')
  argparser.add_argument('-dest', type=str, default = 'EMBL_ID',
                         help = 'Map to format')

  args = argparser.parse_args()
  fmt_in  = args.src
  fmt_out = args.dest
  batch = []
  batch_size = 500
  qry = ''
  m = map.Mapper()
  for accs in sys.stdin:
    batch.append(accs.rstrip())
    if(len(batch) == batch_size):
      print(m.map(batch, fmt_in, fmt_out))
      batch.clear()
  print(m.map(batch, fmt_in, fmt_out))
  return 0

if __name__ == '__main__':
  main()
