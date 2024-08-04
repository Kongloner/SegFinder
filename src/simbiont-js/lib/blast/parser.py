#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  parser.py
#
#  Copyright 2016 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0


import sys
import xml.etree.ElementTree as ET
import json
from . import elements
from . import filters

class Babelfish:
    def __init__(self):
      self.atrb = {}

    def json(self, json_tags):
      tagmap = {
                'query_id'    : 'qid',
                'query_len'   : 'qlength',
                'query_title' : 'qtitle',
                'num'         : 'num',
                'bit_score'   : 'bitscore',
                'score'       : 'score',
                'evalue'      : 'evalue',
                'identity'    : 'identity',
                'positive'    : 'positive',
                'query_from'  : 'queryfrom',
                'query_to'    : 'queryto',
                'hit_from'    : 'hitfrom',
                'hit_to'      : 'hitto',
                'align_len'   : 'alignlen',
                'gaps'        : 'gaps',
                'len'         : 'length',
                'qseq'        : 'qseq',
                'hseq'        : 'hseq',
                'midline'     : 'mline',
                'id'          : 'hid',
               }
      return self.mapper(tagmap, json_tags)

    def mapper(self, thismap, othermap):
      newmap = {}
      for i in thismap:
        if i in othermap:
          newmap[thismap[i]] = othermap[i]
      return newmap

class JsonFmt:
  def __init__(self, result, filters):
    self.bf = Babelfish()
    self.result = result
    self.filters = filters

  def parse(self, blast):
    for i in blast:
      for j in blast[i]['report']['results']:
        for k in blast[i]['report']['results'][j]:
          q = elements.Query(self.bf.json(k), self.filters)
          self.result.queries.append(q)
          self.extract_hits(k['hits'], q)

  def extract_hits(self, json_hits, qry):
    for i in json_hits:
      atrb = self.bf.json(i)
      for j in i['description'][0]:
        atrb[j] = i['description'][0][j]
      hit = elements.Hit(atrb, qry, self.filters)
      if hit.keep != True:
        continue
      self.result.hits.append(hit)
      self.extract_hsps(i['hsps'], qry, hit)

  def extract_hsps(self, hsps, qry, hit):
    for i in hsps:
      hsp = elements.Hsp(self.bf.json(i), qry, hit, self.filters)
      if hsp.keep == False:
        continue
      self.result.hsp.append(hsp)

class Parser:
  def __init__(self, blast_result, opts, fmt):
    self.opts = opts
    self.blast = blast_result
    self.filters = []
    self.result = elements.Result(opts['fields'])
    self.fmt = fmt

  @classmethod
  def json(cls, opts):
    return cls(json.load(sys.stdin), opts, fmt=13)

  @classmethod
  def stdin(cls, opts):
    return cls(ET.parse(sys.stdin).getroot(), opts, fmt=16)

  @classmethod
  def string(cls, xml_string, opts):
    return cls(ET.fromstring(xml_string), opts, fmt=16)

  def add_filters(self, filters = []):
    self.filters = filters

  def parse_xml(self, qry_idx, hit_idx):
    for i in self.blast.findall('.//Iteration'):
        q = elements.Query(i)
        self.result.queries.append(q)
        for j in i.findall('.//Hit'):
          hit = elements.Hit(j, q)
          self.result.hits.append(hit)
          for k in j.findall('.//Hsp'):
            hsp = elements.Hsp(k, q, hit, qry_idx, hit_idx, self.filters)
            if hsp.keep == True:
              self.result.hsp.append(hsp)
          hit_idx += 1
        qry_idx += 1

  def show_filters(self):
    for i in self.filters:
      i.show()

  def parse(self):
    qry_idx = 0
    hit_idx = 0
    if self.fmt == 13:
      jf = JsonFmt(self.result, self.filters)
      jf.parse(self.blast)

      #self.parse_json(qry_idx, hit_idx)
    print("sss", self.fmt)
    if self.fmt == 16:
      self.parse_xml(qry_idx, hit_idx)
