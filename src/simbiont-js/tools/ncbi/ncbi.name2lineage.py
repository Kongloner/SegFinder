#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  ncbi.name2lineage.py
#
#  Copyright 2015 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0.3


import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '../../lib'))
import ncbi.taxonomy

def main():
  t = ncbi.taxonomy.Taxonomy()
  t.parse(sys.stdin.read())
  for i in t.getTaxa():
    i.printLineage()
  return 0

if __name__ == '__main__':
  main()
