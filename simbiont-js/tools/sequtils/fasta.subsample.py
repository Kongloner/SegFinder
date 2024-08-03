#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  fasta.subsample.py
#
#  Copyright 2015 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#   Quick and dirty tool to get a random subset from a FASTA flat file, e.g.
#   200 random sequences from 500 sequences.
#  Version: 0
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import sys
import re
import random
import argparse
import math
sys.path.insert(0, '/home/jan/simbiont/lib/')
import fasta
from fasta  import sequences
from fasta import read

class Sampler:

  def __init__(self):
    self.seqs = []
    self.size = 0

class Subsample:

  def sample(self, args, population):
    popsize = list(range (len(population)))
    samples = args.rand
    if args.rand < 1:
      samples = len(popsize) * args.rand
    subsamples = random.sample(popsize, math.ceil(samples))
    return [population[x] for x in subsamples]

class Batch(fasta.read.Activator):
  count = 0

  def __init__(self):
    self.basename = ''

  def activate(self, lst):
    if len(lst) % self.mark == 0:
      outf = open (self.basename + "." + str(Batch.count), 'w')
      for i in lst:
        outf.write(i.as_fasta(header=True))
      Batch.count += 1
      lst.clear()

  def squeeze(self, lst):
      outf = open (self.basename + "." + str(Batch.count), 'w')
      for i in lst:
        outf.write(i.as_fasta(header=True))

def main():
  ap = argparse.ArgumentParser(description='Subsample FASTA flat files',
                               usage='%(prog)s [options] < [FILE]')
  ap.add_argument('-r','--rand', type=float, default=0,
                  help='Subsample RAND random sequences. If 0 < RAND < 1, the \
                        corresponding random percenatge of sequences will be  \
                        sampled')
  ap.add_argument('-b', '--batch', type=int, default=0,
                  help = 'Split into files containing max. BATCH sequences' )
  ap.add_argument('-id', '--sample_id', type=str, default='sample',
                    help = 'Set a base name for the subsamples' )

  args = ap.parse_args()
  fa = fasta.read.Reader()
  if args.batch > 0:
    b = Batch()
    b.set_mark(args.batch)
    b.basename = args.sample_id
    b.squeeze(fa.read(b))

  if args.rand > 0:
    s = Subsample()
    for i in s.sample(args, fa.read()):
      print(i.as_fasta())
  return 0

if __name__ == '__main__':
  main()
