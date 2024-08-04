#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  blastlib.py
#
#  Copyright 2015 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0


import sys
import xml.etree.ElementTree as ET

class Hit:
  def __init__(self, hit_attr):
    self.id         = hit_attr['id']
    self.acc        = hit_attr['acc']
    self.definition = hit_attr['def']
    self.length     = int(hit_attr['len'])
    self.bit        = float(hit_attr['bit'])
    self.evalue     = float(hit_attr['evalue'])
    self.gaps       = int(hit_attr['gaps'])
    self.hbeg       = int(hit_attr['hbeg'])
    self.hend       = int(hit_attr['hend'])
    self.ident      = int(hit_attr['ident'])
    self.positive   = int(hit_attr['positive'])
    self.qbeg       = int(hit_attr['qbeg'])
    self.qend       = int(hit_attr['qend'])
    self.qframe     = int(hit_attr['qframe'])
    self.score      = int(hit_attr['scr'])
    self.alnlen     = int(hit_attr['alnlen'])

  def show(self):
    print("Hit::ID           : ", self.id)
    print("Hit::accession    : ", self.acc)
    print("Hit::definition   : ", self.definition)
    print("Hit::length       : ", self.length)
    print("Hit::bit score    : ", self.bit)
    print("Hit::score        : ", self.score)
    print("Hit::evalue       : ", self.evalue)
    print("Hit::positive     : ", self.positive)
    print("Hit::identity     : ", self.ident)
    print("Hit::align length : ", self.alnlen)
    print("Hit::gaps         : ", self.gaps)
    print("Hit::sbeg         : ", self.hbeg)
    print("Hit::send         : ", self.hend)
    print("Hit::qbeg         : ", self.qbeg)
    print("Hit::qend         : ", self.qend)

class Query:
  def __init__(self, qry_attributes):
    self.id         = qry_attributes['id']
    self.definition = qry_attributes['def']
    self.length     = int(qry_attributes['len'])
    self.hits      = []

  def show(self):
    print("Query::ID         : ", self.id)
    print("Query::definition : ", self.definition)
    print("Query::length     : ", self.length)

class Result:
  def __init__(self):
    self.results = []

  def show(self, what = 'all'):
    for q in self.results:
      if what == 'all' or what == 'qry':
        q.show()
      if what == 'all' or what == 'hit':
        for j in q.hits:
          j.show()

class Parser:
  def __init__(self, blast_xml):
    self.r = Result()
    self.parse(blast_xml)

  @classmethod
  def stdin(cls):
    return cls(ET.parse(sys.stdin).getroot())

  @classmethod
  def string(cls, xml_string):
    return cls(ET.fromstring(xml_string))

  def get_results(self):
    return self.r

  def get_qry_attributes(self, qry):
    attrib = {
              'id'    : qry.find('Iteration_query-ID').text,
              'len'   : qry.find('Iteration_query-len').text,
              'def'   : qry.find('Iteration_query-def').text,
              'nohit' : 0
             }

    if qry.findtext('Iteration_message'):
      attrib['nohit'] = 1
    return attrib

  def get_hit_attributes(self, hit):
    return  {
              'id'  : hit.find('Hit_id').text,
              'def' : hit.find('Hit_def').text,
              'len' : hit.find('Hit_len').text,
              'acc' : hit.find('Hit_accession').text
            }

  def get_hsp_attributes(self, hsp):
    return  {
              'bit'      : hsp.find('Hsp_bit-score').text,
              'evalue'   : hsp.find('Hsp_evalue').text,
              'gaps'     : hsp.find('Hsp_gaps').text,
              'hbeg'     : hsp.find('Hsp_hit-from').text,
              'hend'     : hsp.find('Hsp_hit-to').text,
              'ident'    : hsp.find('Hsp_identity').text,
              'positive' : hsp.find('Hsp_positive').text,
              'qframe'   : hsp.find('Hsp_hit-frame').text,
              'qbeg'     : hsp.find('Hsp_query-from').text,
              'qend'     : hsp.find('Hsp_query-to').text,
              'scr'      : hsp.find('Hsp_score').text,
              'alnlen'   : hsp.find('Hsp_align-len').text,
            }

  def parse(self, blast_xml):
    for i in blast_xml.findall('.//Iteration'):
      q = Query(self.get_qry_attributes(i))
      for j in i.findall('.//Hit'):
        hit_attrib = self.get_hit_attributes(j)
        for k in j.findall('.//Hsp'):
          hit_attrib.update(self.get_hsp_attributes(k))
          q.hits.append(Hit(hit_attrib))
      self.r.results.append(q)
