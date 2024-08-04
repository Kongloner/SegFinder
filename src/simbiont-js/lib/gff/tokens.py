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

class Assembler:
  def
class Subelement:
  def __init__(self, fields):
    self.start = fields[3]
    self.end = fields[4]
    self.score = fields[5]
    self.phase = fields[7]
    self.id = ''
    self.name = ''
    self.set_attributes(fields[8])

  def set_attributes(self, attributes = ''):
    if len(attributes) != 0:
      for i in attributes.split(';'):
        feature = i.split('=')
        if feature[0] == 'ID':
          self.id = feature[1]
        if feature[0] == 'Parent':
          self.parents = feature[1].split(',')
        if feature[0] == 'Name':
          self.name = feature[1]

class Element:
  def __init__(self, fields):
    self.seqid = fields[0]
    self.source = fields[1]
    self.typ = fields[2]
    self.start = fields[3]
    self.end = fields[4]
    self.score = fields[5]
    self.strand = 0 if fields[6] == '+' else 1
    self.phase = fields[7]
    self.lineage = {}
    self.subelements = []
    self.children = []
    self.id = ''
    self.name = ''
    self.parents = []
    self.is_circular = False
    self.attributes = { }
    self.set_attributes(fields[8])
    self.parts = []

  def set_attributes(self, attributes = ''):
    if len(attributes) != 0:
      for i in attributes.split(';'):
        feature = i.split('=')
        if feature[0] == 'ID':
          self.id = feature[1]
        elif feature[0] == 'Parent':
          self.parents = feature[1].split(',')
        elif feature[0] == 'Name':
          self.name = feature[1]
        elif feature[0] == 'Is_circular':
          self.is_circular = True
        else:
          self.attributes[feature[0]] = feature[1].split(',')

  def add_subelement(self, fields):
    self.subelements.append(Subelement(fields))

  def update_lineage(self, parent):
    self.lineaeg[parent] = 1
