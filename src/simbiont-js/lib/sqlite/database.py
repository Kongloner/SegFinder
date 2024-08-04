#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  database.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0


import sys
import json
import sqlite3
from . import table

class Database:

  def __init__(self):
    self.db = ''
    self.connection = ''
    self.tablemap = {}
    self.attribute_table = 'simbiont_tbl_attrib'
    self.table_attributes = {}

  def connect(self, db):
    self.connection = sqlite3.connect(db)
    self.db = db
    self.create_table_attributes()
    self.update_table_list()
    self.get_table_attributes()

  def update_table_list(self):
    cur = self.connection.cursor()
    for i in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
      self.tablemap[i[0]] = table.Table(self.connection, i[0])

  def load_definitions(self, definitions):
    fhd = open(definitions, 'r')
    table_def = json.load(fhd)
    fhd.close()
    self.create_tables(table_def)

  def get_table_attributes(self):
    cur = self.connection.cursor()
    for i in cur.execute("SELECT * FROM {0} GROUP BY tablename".format(self.attribute_table)):
      self.table_attributes[i[0]] = i[1]


  def create_tables(self, definitions):
    for i in definitions:
      if i in self.tablemap:
        self.tablemap[i] = table.Table(self.connection,
                                          i,
                                          attributes=self.attribute_table)
        if i in self.table_attributes:
          if self.table_attributes[i] == 0:
            self.tablemap[i].get_columns()
        else:
          self.tablemap[i].create(definitions[i])
      else:
        self.tablemap[i] = table.Table(self.connection,
                                       i,
                                       attributes=self.attribute_table)
        self.tablemap[i].create(definitions[i])

  def get_table(self, name):
    if name in self.tablemap:
      return self.tablemap[name]

  def create_table_attributes(self):
    attributes ={
      self.attribute_table :
      {
        'columns' :
        {
          'tablename' :
          {
            'datatype' : 'TEXT',
            'constraints' :
            [
              ['UNIQUE', 'ignore']
            ]
          },
          'mask' : {'datatype' : 'INT'}
        }
      }
    }
    self.create_tables(attributes)
