#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  filter.py
#
#  Copyright 2016 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0


import sys
class Hspfilter:
  def __init__(self, opts):
    self.limits = { # value    [ min, max]
                    'evalue' : [0, opts['evalue']],
                    'alnlen' : [opts['aln_len'], 0]
                  }
    if self.limits['alnlen'][0] > 0 and self.limits['alnlen'][0] <= 1:
      self.limits['hitcov'] = self.limits['alnlen']
      del self.limits['alnlen']

  def set_limits(limits = {}):
    self.limits.update(limits)

  def filter(self, atrb):
    for i in self.limits:
      if i in atrb:
        if i == 'evalue':
          if atrb[i] > self.limits[i][1]:
            return False
        if atrb[i] < self.limits[i][0] and atrb[i] >self.limits[i][1]:
          return False
    return True

  def show(self):
    for i in self.limits:
      print(i, self.limits[i])


class Filterator:

  class Filter:

    def __init__(self):
      self.field = None
      self.lower = None
      self.upper = None
      self.operator = None
      self.closed = None

    def filter(self, value):
      lower = self.lower
      upper = self.upper

      if self.field != 'evalue':
        if self.lower < 1:
          lower = value * self.lower
        if self.upper < 1:
          upper = value * self.upper

      if self.closed:
        if lower < upper:
          if (value >= upper) and (value <= lower):
            return True
        if self.operator == '<' and (value <= lower):
          return True
        if self.operator == '>' and (value >= lower):
          return True

      else:
        if lower < upper:
          if (value > upper) and (value < lower):
            return True
        if self.operator == '<' and (value < lower):
          return True
        if self.operator == '>' and (value > lower):
          return True
      return False

  ## open: does not include endpoints
  ## closed: inlcudes endpoints
  def create(self, field, lower=None, upper=None, closed=True):
    f = Filterator.Filter()
    f.field = field
    f.closed = closed

    if lower and not upper:
      f.lower = lower
      f.operator = '<'

    if upper and not lower:
      f.upper = upper
      f.operator = '>'

    return f

  def prepare_filers(self, filters):
    lower = None
    upper = None
    closed = True
    blast_filters = []
    for i in filters:
      if 'lower' in filters[i]:
        lower = filters[i]['lower']
      if 'upper' in filters[i]:
        upper = filters[i]['upper']
      if 'closed' in filters[i]:
        closed = filters[i]['closed']
      blast_filters.append(self.create(i, lower=lower, upper=upper, closed=closed))
    return blast_filters
