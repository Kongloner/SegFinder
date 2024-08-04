#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  ncbi.summary.py
#
#  Copyright 2016 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0


import sys
import argparse
import os
sys.path.insert(1, os.path.join(sys.path[0], '../../lib'))
import esummary.Esummary

def main():
  argparser = argparse.ArgumentParser(description='NCBI esummary')
  argparser.add_argument('-db', help = 'Database.')
  argparser.add_argument('-ids', type=str, help='Comma separated list if UIDs')
  argparser.add_argument('-webenv', type=str, help = 'Webenv')
  argparser.add_argument('-qrykey', type=str, help = 'qrykey')
  args = argparser.parse_args()

  summary = esummary.Esummary()
  if args.ids and (args.web or args.qrykey):
    print("Cannot use -ids and -webenv/-qrykey together. Exiting.")
    sys.exit()
  if args.ids:
    ids = args.ids.split(',')
    summary.summarize(args.db, [x for x in ids])
  else:
    summary.summarize(args.db, webenv=args.webenv, query_key=args.qrykey)
  return 0

if __name__ == '__main__':
  main()
