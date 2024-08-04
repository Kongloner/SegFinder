#  hsp.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0

class Hsp:

  def __init__(self, blast_hsp, query, hit, count):
    self.bitscore =  blast_hsp.get('bit_score', 0)
    self.num = blast_hsp.get('num', 0)
    self.score = blast_hsp.get('score', 0)
    self.evalue = blast_hsp.get('evalue', 100)
    self.identify = blast_hsp.get('identity', 0)
    self.positive = blast_hsp.get('positive', 0)
    self.alength = blast_hsp.get('align_len', 0)
    self.gaps = blast_hsp.get('gaps', 0)
    self.hid = count
    self.query = query
    self.hit = hit
