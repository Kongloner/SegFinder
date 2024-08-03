#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  parseASN1.py
#
#  Copyright 2015 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0


import sys


class Parser:
  def read():
    value = ''
    lvl = 0
    for ch in sys.stdin.read():
      if ch == '{':
        lvl += 1
        print(value)
        value = ''
      value += ch

class Struct:
    name = 'None'



def main():

  p = Parser;
  p.read()
  return 0

if __name__ == '__main__':
  main()
