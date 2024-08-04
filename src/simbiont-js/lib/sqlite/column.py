#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  column.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0
from . import constraints

class Column:


  def __init__(self, name='', idx=0):
    self.name = name
    self.datatype = ''
    self.constraints = []
    self.comment = ''
    self.idx = idx

  def get_definition(self):
    definition = self.name
    if len(self.datatype) > 0:
      definition += '\t'  + self.datatype
    if len(self.constraints) > 0:
      for i in self.constraints:
        definition += ' ' + i.get_definition()
    if len(self.comment) > 0:
      definition += "\t--  " + self.comment
    return definition + '\n'

  def define(self, definition):
    if 'comment' in definition:
      self.comment = definition.pop('comment')
    if 'datatype' in definition:
      self.datatype = definition.pop('datatype').upper()
    if 'constraints' in definition:
      for i in definition['constraints']:
        if i[0].upper() == 'UNIQUE':
          self.constraints.append(constraints.UniqueConstraint(i[1]))
        if i[0].upper() == 'DEFAULT':
          self.constraints.append(constraints.DefaultConstraint(i[1]))
      ##print("Created: Table {0}".format(self.table_id), file=sys.stderr)
