#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  ncbi.fetch.py
#
#  Copyright 2015 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0


import sys
import argparse
import os
sys.path.insert(1, os.path.join(sys.path[0], '../../lib'))
import ncbi.eutils.efetch

def main():
  ap = argparse.ArgumentParser(description='Fetch sequences from NCBI')
  ap.add_argument('--uids', '-u', nargs='*'),
  ap.add_argument('--type', '-t', type=str, default='fasta',
                  help='set rettype.  Default: fasta')
  ap.add_argument('--wait', '-w', type=float, default=0.3,
                  help='set wait time between requestes [seconds]. Default: 0.3s'),
  ap.add_argument('--batch_size', '-b', type=int, default=500,
                  help='set batch size  for requestes. Default: 500'),
  ap.add_argument('--database', '-db', type=str, default='sequences',
                  help='set database. Default: sequences' )

  #ap.add_argument('--webenv', type=str, default=None, help = 'Webenv')
  #ap.add_argument('--qrykey', type=str, default=None, help = 'qrykey')
  args = ap.parse_args()

  fetch = ncbi.eutils.efetch.Efetcher()
  ids = []
  if args.uids:
    ids = [x.rstrip() for x in args.uids]
  else:
    for i in sys.stdin:
      ids.append(i.rstrip())
  fetch.fetch(ids, options={'rettype' : args.type,
                            'db' : args.database,
                            'wait' : args.wait,
                            'batch_size' : args.batch_size})

  return 0

if __name__ == '__main__':
  main()
