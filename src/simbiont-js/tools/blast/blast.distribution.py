#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  blast.distribution.py
#
#  Copyright 2015 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0


import sys

def collectCoverage():
  dist = {}
  for i in sys.stdin:
    i = i.split()
    beg = int(i[8])
    end = int(i[9])
    tmp = 0
    if beg > end:
      tmp = end
      end = beg
      beg = tmp
    for j in range(beg, end, 1):
      print(j)
      if j in dist:
        dist[j] += 1
      else:
        dist[j] = 1

  for i in dist:
    print(i, dist[i])

def collectReadDistribution():
  dist = {}
  for i in sys.stdin:
    i = i.rstrip()
    if i in dist:
      dist[i] += 1
    else:
      dist[i] = 0

  for i in dist:
    print(i, dist[i])

def main():
  #collectCoverage()
  collectReadDistribution()
  return 0

if __name__ == '__main__':
  main()
