# -*- coding: utf-8 -*-
#
#  tinyseq.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0


import io
import sys
import xml.etree.ElementTree as ET
from ..sequences import sequences

class TinySeqParser:

  class Callback:
    def __init__(self):
      pass

    def run(self, sequences):
      pass

  def __init__(self):
    self.src = sys.stdin
    self.sequences = []
    self.callback = self.Callback()
    self.run_callback = False

  def from_stream(self, stream):
    self.src = io.StringIO(stream)

  def set_callback(self):
    self.run_callback = True

  def parse(self):
    s = sequences.NcbiSequence()
    for event, elem in ET.iterparse(self.src, events=["start", "end"]):
      if event == 'start' and elem.tag == 'TSeq':
        s = sequences.NcbiSequence()
      if event == 'end' :
        if elem.tag == 'TSeq':
          self.sequences.append(s)
          if self.run_callback == True:
            self.callback.run(self.sequences)
        if elem.tag == 'TSeq_seqtype':
          s.typ = elem.attrib['value']
        if elem.tag == 'TSeq_gi':
          s.gi = elem.text
        if elem.tag == 'TSeq_accver':
          s.accver = elem.text
        if elem.tag == 'TSeq_sid':
          s.sid = elem.text
        if elem.tag == 'TSeq_taxid':
          s.taxid = elem.text
        if elem.tag == 'TSeq_orgname':
          s.orgname = elem.text
        if elem.tag == 'TSeq_defline':
          s.defline = elem.text
        if elem.tag == 'TSeq_length':
          s.length = elem.text
        if elem.tag == 'TSeq_sequence':
          s.seq = elem.text
    self.src.close()
