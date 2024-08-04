#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  taxonomy_request_parser.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0

import io
import sys
import xml.etree.ElementTree as ET
from ..sequences import sequences

class FetchedNcbiUid:
  def __init__(self, uid, db):
    self.uid = uid
    self.db = db

class NcbiTaxonomyRequestParser:

  def __init__(self):
    self.fetched = 0
    self.db = ''

  def parse(self, xml):
    xml = io.StringIO(xml.read().decode())
    print(xml.getvalue())
    uid = 0
    for event, elem in ET.iterparse(xml, events=["start", "end"]):
      if event == 'start' and elem.tag == 'Lineage':
        if taxid == 0:
          break
      if event == 'start' and elem.tag == 'TaxId':
        uid = FetchedNcbiUid(elem.text, self.db)
        self.fetched += 1
        break
    xml.close()
