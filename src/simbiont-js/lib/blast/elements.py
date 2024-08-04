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

class Result:
  def __init__(self, fields = ['qid', 'hid', 'identity', 'alignlen', 'evalue']):
    self.results = []
    self.queries = []
    self.hits    = []
    self.hsp     = []
    self.fields = fields

  def show(self):
    for i in self.hsp:
      i.show()
      #print(i.qry)
      #print(self.queries[i.qry_idx].id, self.queries[i.qry_idx].definition,
            #self.hits[i.hit_idx].acc, self.hits[i.hit_idx].definition,
            #self.hits[i.hit_idx].length, i.evalue, i.alnlen, sep='\t')
      #print(i.qry.)


class Query:
  def __init__(self, atrb, filters = []):
    self.name   = atrb['qid']          if 'qid'     in atrb else ''
    self.title  = atrb['qtitle']       if 'qtitle'  in atrb else ''
    self.length = int(atrb['qlength']) if 'qlength' in atrb else 0
    self.nohit  = False if 'nohit' in atrb else True
    #self.keep   = self.filter(filters) if len(filters) > 0 else True

  def show(self):
    print("Query::ID         : ", self.name)
    print("Query::definition : ", self.title)
    print("Query::length     : ", self.length)

class Hit:
  def __init__(self, atrb, qry = Query({}), filters = []):
    self.name    = atrb['id']          if 'id'        in atrb else ''
    self.acc     = atrb['accession']   if 'accession' in atrb else ''
    self.title   = atrb['title']       if 'title'     in atrb else ''
    self.length  = int(atrb['length']) if 'length'    in atrb else 0
    self.keep    = True
    self.qry_idx = qry

class Hsp:
  attributes = ['bit', 'evalue', 'gaps', 'hbeg', 'hend', 'ident']
  def __init__(self, atrb, qry = Query({}), hit = Hit({}), filters = []):
    self.bit      = float(atrb['bitscore']) if 'bitscore'  in atrb else 0.0
    self.evalue   = float(atrb['evalue'])   if 'evalue'    in atrb else -1.0
    self.gaps     = int(atrb['gaps'])       if 'gaps'      in atrb else -1
    self.hbeg     = int(atrb['hitfrom'])    if 'hitfrom'   in atrb else -1
    self.hend     = int(atrb['hitto'])      if 'hitto'     in atrb else -1
    self.ident    = int(atrb['identity'])   if 'identity'  in atrb else -1
    self.positive = int(atrb['positive'])   if 'positive'  in atrb else -1
    self.qbeg     = int(atrb['queryfrom'])  if 'queryfrom' in atrb else -1
    self.qend     = int(atrb['queryto'])    if 'queryto'   in atrb else -1
    self.qframe   = int(atrb['hitframe'])   if 'hitframe'  in atrb else -1
    self.score    = int(atrb['score'])      if 'score'     in atrb else -1
    self.alnlen   = int(atrb['alignlen'])   if 'alignlen'  in atrb else -1
    self.hseq     = atrb['hseq']  if 'hseq'  in atrb else ''
    self.qseq     = atrb['qseq']  if 'qseq'  in atrb else ''
    self.midline  = atrb['mline'] if 'mline' in atrb else ''
    self.qry      = qry
    self.hit      = hit
    self.hlen     = abs(self.hend - self.hbeg) + 1
    self.qlen     = abs(self.qend - self.qbeg) + 1
    self.hitcov   = self.alnlen / qry.length
    self.keep     = True
    if len(filters) > 0:
      for i in filters:
        self.keep = i.filter(vars(self))

  def show(self):
    attrib = vars(self)
    for i in attrib:
      print(i, attrib[i], end = '\t')
    print()
