#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  parser.py
#
#  Copyright 2016 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0

import sys
import re
import gff.tokens as tokens

class GFF:
  pragma = re.compile("^\#\#([^#].+)")
  end = re.compile("^\#\#\#")
  comment = re.compile("^\#[^#]")
  entry = re.compile("^[^#|\s]")

  def __init__(self, gff):
    self.gff = gff
    self.version = 0
    self.region = ''
    self.region_start = 0
    self.region_end   = 0
    self.regions = []
    self.elements = []

  @classmethod
  def stdin(cls):
    return cls(sys.stdin)

  @classmethod
  def string(cls, gff_string):
    return cls(gff_string)

  @classmethod
  def file(cls, gff_file):
    return cls(open(gff_string, 'rt'))

  def parse(self):
    element_map = {}
    level = 0
    elements = []
    for i in self.gff:
      pragma = GFF.pragma.match(i)
      end = GFF.end.match(i)
      comment = GFF.comment.match(i)
      entry = GFF.entry.match(i)
      if end:
        print("End")
      if pragma:
        pragma_fields = pragma.group(1).strip().split()
        if pragma_fields[0] == 'gff-version':
          self.version = pragma_fields[1]
        if pragma_fields[0] == 'sequence-region':
          self.region = pragma_fields[1]
          self.region_start = pragma_fields[2]
          self.region_end = pragma_fields[3]

      if comment:
        continue

      if entry:
        fields = i.strip().split('\t')
        if len(fields) != 9:
          print("Wrong number of fields for GFF. Require 9, got {0}".format(len(fields)))
          exit()
        e = tokens.Element(fields)
        if len(e.parents) == 0:
          elements.append(e)

        if e.id in element_map:
          element_map[e.id].add_subelement(fields)
        else:
          element_map[e.id] = e

    for i in element_map:
      if len(element_map[i].parents) > 0:
        self.resolve(element_map[i], element_map)

    for i in element_map:
      print("parent", element_map[i].id)
      for j in element_map[i].children:
        print('\tchildren', j.id)

      #for j in element_map[i].subelements:
        #print('\tsubelements', j.id)
      #print(element_map[i], element_map[i].subelements, element_map[i].children)
      #print()

  def resolve(self, element, emap):
    for i in element.parents:
      emap[i].children.append(element)
