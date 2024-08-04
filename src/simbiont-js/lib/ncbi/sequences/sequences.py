# -*- coding: utf-8 -*-
#
#  sequences.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '../../lib'))
from basic_sequences import basic_sequences

class NcbiSequence(basic_sequences.BasicSequence):

  def __init__(self):
    super(NcbiSequence, self).__init__()
    self.accver = ''
    self.orgname = ''
    self.defline = ''
    self.gi = 0
    self.taxid = 0
    self.db = ''

  def show(self):
      print(self.accver, self.gi, self.sid, self.taxid, self.typ, self.length,
            self.db, sep='\t', file=sys.stderr)

  def show_as_fasta(self):
    s = basic_sequences.FastaSequence(header=self.accver+", "+self.defline,
                                      seq=self.seq)
    s.show()
