#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  ncbi.parser.py
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
import json
import insd.gbreader

class Printer(insd.gbreader.XmlReader.Provider):

  def __init__(self):
    super(Printer, self).__init__()
    self.view = { "locus" : [ "locus", "organism"],
                  "source": ["taxid"]}
    self.delim = '\t'
    self.columns = []

  def set_view(self, view, delim='\t'):
    self.delim = delim
    fh = open(view, 'r')
    self.view.update(json.load(fh))
    fh.close()
    if 'comment' in self.view:
      del(self.view['comment'])

  def show(self, locus):
    for feat in locus.feature.get_many():
      print(feat.get_sources())
      for i in feat.get_qualifier('product'):
        print(i.value, end='\t')
      print()

  def provide(self, locus):
    self.show(locus)


def main():
  ap = argparse.ArgumentParser(description='NCBI XML parser')
  ap.add_argument('-s', '--subset', type=str, default=None,
                  help = 'File describing features and fields to parse in JSON format')
  ap.add_argument('-p', '--prefix', type=str, default="GB",
                  help = 'Tag prefix for the XML file')
  ap.add_argument('-c', '--columns', type=str, default=None,
                  help = 'File describing the display of the results in JSON format')
  ap.add_argument('-i', '--input', type=str, default=None,
                  help = 'Input file')


  args = ap.parse_args()
  r = insd.gbreader.XmlReader(tag_prefix=args.prefix)
  if args.subset:
    r.set_subset(args.subset)
  if args.input:
    r.read_file(args.input)
  else:
    r.read()
  p = Printer()
  if args.columns:
    p.set_view(args.columns)
  r.iterate(p)
  return 0

if __name__ == '__main__':
  main()
