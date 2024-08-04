
#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  ncbi.sra.search.py
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
import ncbi.esearch

def main():
  argparser = argparse.ArgumentParser(description='Search NCBI SRA archives')
  argparser.add_argument('-term', type=str)
  args = argparser.parse_args()

  s = ncbi.esearch.Esearch()
  s.searchSRA(args.term)
  return 0

if __name__ == '__main__':
  main()
