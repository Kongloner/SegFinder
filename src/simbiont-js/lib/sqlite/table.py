#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  table.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0

import sys
from . import column

class Table:

  class Constraint:

    def __init__(self):
      self.name = ''
      self.columns = []

    def get_definition(self):
      definition = self.name + ' ' + self.columns.pop(0)
      if len(self.columns) > 0:
        for i in self.columns:
          definition += ','+ i
      return definition

  def __init__(self, connection, table_id, attributes=''):
    self.name = table_id
    self.connection = connection
    self.constraints = []
    self.comment = ''
    self.columns = {}
    self.attributes = attributes

  def add_constraints(self, constraints):
    pass  # ToDo

  def isReadOnly(self):
    return self.isReadOnly

  def create(self, definition):
    self.define(definition)
    self.add_columns()

  def define(self, definition):
    if 'columns' not in definition:
      sys.exit("Error: column definitions required")
    if 'attributes' in definition:
      if 'mask' in definition['attributes']:
        stmt = "INSERT INTO {0} (tablename, mask) VALUES (?, ?)".format(self.attributes)
        self.insert(stmt, [(self.name, definition['attributes']['mask'])])
    if 'comment' in definition:
      self.comment = definition['comment']
    for i in definition['columns']:
      self.columns[i] = column.Column(i, len(self.columns))
      self.columns[i].define(definition['columns'][i])


  def add_columns(self):
    stmt = "CREATE TABLE IF NOT EXISTS {0}\n(\n".format(self.name)
    if len(self.comment) > 0:
      stmt += "\t--\n\t-- {0}\n\t--\n".format(self.comment)
    cols = list(self.columns.keys())
    stmt += " " + self.columns[cols[0]].get_definition()
    if len(cols) > 1:
      for i in cols[1:]:
        stmt += "," + self.columns[i].get_definition()
    if len(self.constraints) > 0:
      stmt += '(' + self.constraints[0].get_definition()
    if len(self.constraints) > 1:
      for i in self.constraints[1:]:
        stmt += ',' + i.get_definition()
      stmt += ')'
    stmt += ')'
    #print(stmt)
    c = self.connection.cursor()
    c.execute(stmt)
    self.connection.commit()

  def get_columns(self):
    cur = self.connection.cursor()
    for i in cur.execute("PRAGMA table_info({0})".format(self.name)):
      self.columns[i[1]] = column.Column()
      self.columns[i[1]].idx = i[0]
      self.columns[i[1]].name = i[1]
      self.columns[i[1]].datatype = i[2]

  def delete(self):
    cur = self.connection.cursor()
    cur.execute("DROP TABLE {0}".format(self.table_id))
    self.connection.commit()
    print("Table {0}: deleted".format(self.table_id), file=sys.stderr)

  def insert(self, stmt, values):
    #print(stmt, values)
    c = self.connection.cursor()
    if len(values) > 1:
      c.executemany(stmt, values)
    else:
      c.execute(stmt, values[0])
    self.connection.commit()

  def select(self, stmt, values=[]):
    c = self.connection.cursor()
    if len(values) > 0:
      return e.execute(stmt, values)
    return e.execute(stmt)
