#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  blast.parse.py
#
#  Copyright 2015 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0

import sys
import argparse
import.os
sys.path.insert(1, os.path.join(sys.path[0], '../../lib'))
import blast.parser  as blast
import blast.filters as bfilters


def parse_options():
  argparser = argparse.ArgumentParser(description='Parse BLAST output')
  argparser.add_argument('-evalue', type=float, default = 10**-6,
                         help = 'max evalue.  Default: 10**-6')
  argparser.add_argument('-aln_len', type=float, default = 0,
                         help = 'min alignment length. Default: 0' )
  argparser.add_argument('-fields', type=str,
                         default = 'qid,sid,ident,alnlen,evalue',
                         help = 'show result fields. \
                                 Default: qid,hid,identity,alignlen,evalue' )
  opts = vars(argparser.parse_args())

  for i in opts:
    if i == 'fields':
      opts[i] = opts[i].split(',')
  return opts

def set_filters():
  filters = {
              'evalue'  : {
                           'upper'  : 10**-6,
                           'closed' : False
                          },
              'aln_len' : {
                            'lower' : 0.8
                          },
            }
def main():
  options = parse_options()
  #bp = blast.Parser.json(options)
  bp= blast.Parser.stdin(options)
  bp.add_filters([bfilters.Hspfilter(options)])
  bp.show_filters()
  bp.parse()
  bp.result.show()
  #r.show_qry()
  return 0

if __name__ == '__main__':
  main()
