#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  ncbi.tinyseq2fasta.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0

import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '../../lib'))
import converter.tinyseqxml

def main():
  c = converter.tinyseqxml.TinyXmlToFasta()
  c.convert()
  return 0

if __name__ == '__main__':
  main()
