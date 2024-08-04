# -*- coding: utf-8 -*-
#
#  basic_sequences.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0


class BasicSequence:

  def __init__(self):
    self.seq = ''
    self.sid = ''
    self.typ = ''
    self.length = 0

class FastaSequence:

  def __init__(self, header='', seq=''):
    self.seq = seq
    self.header = header

  def show(self):
    print(">{0}\n{1}".format(self.header, self.seq))
