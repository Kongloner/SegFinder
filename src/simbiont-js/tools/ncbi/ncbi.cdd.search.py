#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  ncbi.cdd.py
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
import ncbi.cdd

def prep_args():
  argparser = argparse.ArgumentParser(description='Search NCBI CDD database')
  argparser.add_argument('-db',   type=str, default = 'cdd',
                         help = 'set database. Default: cdd' )
  argparser.add_argument('-smode', type=str, default = 'automatic',
                         help = 'set search mode: automatic, precalc, live.\
                                 Default: automatic')
  argparser.add_argument('-useid1', type=int, default = 1,
                         help = 'search backend [0,1].  Default: 1')
  argparser.add_argument('-compbasedadj', type=int, default = 1,
                         help = 'Use composition corrected set retrieval size. \
                                 Default: 1')
  argparser.add_argument('-filter', type=int, default = 1,
                         help = 'filter out compositionally biased regions \
                                 from the query sequences [0,1].  Default: 1')
  argparser.add_argument('-evalue', type=float, default = 0.01,
                         help = 'specify evalue cutoff. Default: 0.01')
  argparser.add_argument('-maxhit', type=int, default = 500,
                         help = 'specify max. number of hits. Default: 500')
  argparser.add_argument('-tdata', type=str, default='hits',
                         help = 'Specify the target data in the output: hits, \
                         aligns, feats. Default: hits')
  argparser.add_argument('-alnfmt', type=str, default = 'json',
                         help = 'Specify align format if -tdata aligns: ans, \
                         xml, json. Default: hits')
  argparser.add_argument('-dmode', type=str, default = 'std',
                         help = 'Specify the data mode desired in the output:\
                         rep, std, full. Default: hits')
  argparser.add_argument('-qdefl', type=int, default = 1,
                         help = 'Include definition lines for the query \
                                 proteins in the output [0,1]. Default: 1')
  argparser.add_argument('-cddefl', type=int, default=1,
                         help = 'Include the titles of conserved domains in  \
                                 the output [0,1]. Default: 1')
  argparser.add_argument('-clonly', type=int, default = 1,
                         help = 'Only superfamilies will be reported [0,1]. \
                                 Default: 1')
  argparser.add_argument('-cdsid', type=str, default = None,
                         help = 'Check and rehook int status of query with \
                                 cdsid')
  return argparser.parse_args()

def main():
  args = prep_args()
  cs = ncbi.cdd.CDDSearch()
  cs.search(args)
  return 0

if __name__ == '__main__':
  main()
