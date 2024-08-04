#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  uniprot.fetch.py
#
#  Copyright 2015 Jan P Buchmann <lejosh@members.fsf.org>
#   Description:
#     A wrapper for the Uniprot website to fetch data for Uniprot accessions
#     via the URL (REST)[0].
#
# [0]: http://www.uniprot.org/help/programmatic_access
#  Version: 1.4

import re
import sys
import argparse
import os
sys.path.insert(0, '/home/jan/simbiont/lib/uniprot')
import fetch

class Params:
  def __init__(self, qry = '', cols = '', fmt = '', lim = 0):
    self.def_cols = 'id,entry name,reviewed,protein names,genes,organism,length'
    self.def_fmt  = 'tab'
    self.def_lim  = lim
    self.params = []
    self.chkQry(qry)
    self.prepCols(cols)
    self.prepFmt(fmt)
    self.params.append(lim)
  def chkQry(self, qry):
    if qry == '':
      print("No Uniprot query given. Abort\n")
      exit()
    self.params.append(qry)

  def prepCols(self, cols):
    cols = self.def_cols if cols == '' else cols
    cols = re.sub(', ', ',', cols)
    self.params.append(cols)

  def prepFmt(self, fmt):
    fmt = self.def_fmt if fmt == '' else fmt
    self.params.append(fmt)

  def getParams(self):
    return self.params

  def getQry(self):
    return self.params[0]

  def getCols(self):
    return self.params[1]

  def getFmt(self):
    return self.params[2]

def main():
  def_cols = 'id,entry name,reviewed,protein names,genes,organism,length'
  def_fmt  = 'tab'
  argparser = argparse.ArgumentParser(description='Fetch Uniprot')
  argparser.add_argument('-qry', type=str, default = '',
                         help = 'Uniport query')
  argparser.add_argument('-cols', type=str, default = def_cols,
                         help = 'Columns to retrieve')
  argparser.add_argument('-fmt',  type=str, default = def_fmt,
                         help = 'Format')
  argparser.add_argument('-lim',  type=str, default = 0,
                         help = 'limit: integer')

  args = argparser.parse_args()

  p = Params(args.qry, args.cols, args.fmt, args.lim)
  print('Query: '  , p.getQry(),  '\n',
        'Columns: ', p.getCols(), '\n',
        'Format: ' , p.getFmt(), sep = '', file = sys.stderr)
  f = fetch.Fetcher()
  f.fetch(*p.getParams())
  f.show()
  return 0

if __name__ == '__main__':
  main()
