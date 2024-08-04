#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  ncbi.elink.py
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
import ncbi.elink

def main():
  argparser = argparse.ArgumentParser(description='Link dbs at NCBI')
  argparser.add_argument('-db0', type=str, help = 'From databse.')
  argparser.add_argument('-db1', type=str, help = 'To database.' )
  args = argparser.parse_args()
  ids = []
  for acc in sys.stdin:
    ids.append(acc.rstrip())
  el = ncbi.elink.Elink()
  el.link(args.db0, args.db1, ids)
  return 0

if __name__ == '__main__':
  main()
