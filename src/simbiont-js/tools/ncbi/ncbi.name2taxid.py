#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  ncbi.name2taxid.py
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

class Name2TaxID:
  def __init__(self, excl_list):
    if len(excl_list) > 0:
      self.excl = {}
      self.checkArgs(excl_list)
    self.names = []
    self.prepNames()

  def checkArgs(self, excl_list):
    for i in excl_list.split(','):
      self.excl[i.strip()] = 1

  def prepNames(self):
    for i in sys.stdin:
      for j in i.rstrip().split():
        if j in self.excl:
          continue
        self.names.append(j)

  def lookup(self):
    s = esearch.Esearch()
    for i in self.names:
      response = ncbi.esearch.Esearch().search(term = i, db = 'taxonomy', stream = 'ret')
      rcvr = nsbi.esearch.Receiver.string(response)
      if 'err' in rcvr.msg:
        print("Error: {err}".format(err = rcvr.msg['err']))
        continue
      if 'PhraseNotFound' in rcvr.msg:
        print(i, 'Not Found', sep = '\t')
        continue
      print(i, rcvr.msg['Id'][0], sep = '\t')

def main():
  argparser = argparse.ArgumentParser(description='Name to TaxID (NCBI)')
  argparser.add_argument('-excl', type=str, default = '',
                          help = 'Comma-delimited list of names to exclude')
  args = argparser.parse_args()
  n2t = Name2TaxID(args.excl)
  n2t.lookup()
  return 0

if __name__ == '__main__':
  main()
