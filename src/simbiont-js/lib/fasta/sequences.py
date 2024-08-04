#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  sequences.py
#
#  Copyright 2016 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0

import json
import sequences

class NcbiSequence(sequences.Sequence):

  def __init__(self):
    super(NcbiSequence, self).__init__()
    self.accver = ''
    self.orgname = ''
    self.defline = ''
    self.db = ''
    self.gi = 0
    self.taxid = 0

  def show(self):
      print(self.accver, self.gi, self.sid, self.taxid, self.typ, self.length,
            self.db, sep='\t', file=sys.stderr)

  def show_as_fasta(self):
    s = sequences.FastaSequence(header=self.defline, seq=self.seq)
    s.show()

class Sequence:
  def __init__(self, header, seq):
    self.header = header
    self.sequence  = seq
    self.seqid = header.split(' ')[0]

  def as_json(self, header=False):
    if header == True:
      return {
             'seqid' : self.seqid,
             'seq' : self.sequence,
             'header': self.header
             }

    return {
            'seqid' : self.seqid,
            'seq' : self.sequence
           }

  def as_fasta(self, header=False):
    if header == True:
      return ">"+self.header + "\n" + self.sequence + "\n"
    return ">"+self.seqid + "\n" + self.sequence + "\n"
