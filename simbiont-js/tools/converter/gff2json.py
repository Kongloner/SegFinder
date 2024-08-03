#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  gff2json.py
#
#  Copyright 2016 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0


import sys
sys.path.append("/home/jan/simbiont/lib/")
import gff.parser as gffp

def main():
  gp = gffp.GFF.stdin()
  gp.parse()
  return 0

if __name__ == '__main__':
  main()
