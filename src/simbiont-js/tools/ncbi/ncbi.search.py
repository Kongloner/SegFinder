#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  ncbi.search.py
#
#  Copyright 2015 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#   Searching NCBI fromt the command line.
#  Version: 0


import sys
import argparse
import os
sys.path.insert(1, os.path.join(sys.path[0], '../../lib'))
import ncbi.eutils.esearch

def main():
  ap = argparse.ArgumentParser(description='Search NCBI')
  ap.add_argument('--term', '-t', type=str)
  ap.add_argument('--database', '-db', type=str, default='sequences',
                  help='set database. Default: sequences' )
  ap.add_argument('--type', '-tp', type=str, default='uilist',
                  help='set rettype.  Default: uilist')
  ap.add_argument('--usehistory', type=bool, default=True,
                  help='Use NCBI Sserver webhistory.  Default: True')
  ap.add_argument('--mode','-m', type=str, default='xml',
                  help='set retmode.  Default: xml')
  ap.add_argument('--limit','-l', type=int, default=0,
                  help='Set maximum number of uids to retrieve.  Default: all')
  args = ap.parse_args()
  #if args.database.lower() == 'sra':
    #s = ncbi.eutils.esearch.SraSearcher()
    #s.search(args.term, options={'rettype':args.type,  'retmode':args.mode,
                               #'db':args.database, 'limit':args.limit})


  #else:
    #s = ncbi.eutils.esearch.Esearcher()
    #s.search(args.term, options={'rettype':args.type,  'retmode':args.mode,
                               #'db':args.database, 'limit':args.limit})
    #for i in s.uids:
      #print(i)
  s = ncbi.eutils.esearch.Esearcher()
  s.search(args.term, options={'rettype':args.type,  'retmode':args.mode,
                               'db':args.database, 'limit':args.limit})
  for i in s.uids:
    print(i)
  return 0

if __name__ == '__main__':
  main()
