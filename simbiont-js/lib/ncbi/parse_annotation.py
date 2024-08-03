#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  parse_annotation.py
#
#  Copyright 2015 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#   Parse a GenBank annotation in XML format
#  Version: 0


import sys
import  xml.etree.ElementTree as ET

class Feature:
  pass

class Annotation:
  #def __init__(self, annotation):
  pass

class Parser:
  def __init__(self, gbFile):
    self.tree = ET.parse(gbFile)
    self.root = self.tree.getroot()

  def getFeatures(self):
    for fts in self.root.iter('Seq-feat'):
      for attr in fts


def main():
  p = Parser(sys.argv[1])
  ft = p.getFeatures()
  return 0

if __name__ == '__main__':
  main()
