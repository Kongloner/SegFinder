#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  read.py
#
#  Copyright 2016 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0


import sys
from fasta import sequences

class Activator:

  def __init__(self):
    self.mark = 0

  def set_mark(self, mark):
    self.mark = mark

  def activate(self, lst):
    pass

class Reader:

  def __init__(self):
    self.seqlist = []

  def read(self, activator=None):
    header = ''
    seq = ''
    a = Activator()

    if activator:
      a = activator

    for i in sys.stdin:
      if i[0] == '>':
        if len(header) > 0:
          self.seqlist.append(sequences.Sequence(header, seq))
          a.activate(self.seqlist)
          seq = ''
        header = i.strip().split('>')[1]
        continue
      seq += i.strip()
    self.seqlist.append(sequences.Sequence(header, seq))
    return self.seqlist
