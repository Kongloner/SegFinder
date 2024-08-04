#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  search_request_parser.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0

import io
import sys
import xml.etree.ElementTree as ET

class EsearchResponseParser:

  def parse(self, xml, response):
    # Think about a XMLPullParser at some point
    xml = io.StringIO(xml.read().decode())
    print(xml.getvalue(), file=sys.stderr)
    for event, elem in ET.iterparse(xml, events=["start", "end"]):
      if event == 'end' and elem.tag == 'Count':
        response.count = int(elem.text)
      if event == 'end' and elem.tag == 'RetMax':
        response.retmax = int(elem.text)
      if event == 'end' and elem.tag == 'RetStart':
        response.retstart = int(elem.text)
      if event == 'end' and elem.tag == 'QueryKey':
        response.query_key = int(elem.text)
      if event == 'end' and elem.tag == 'WebEnv':
        response.webenv = elem.text
      if event == 'end' and elem.tag == 'Id':
        response.uids.append(elem.text)
      if event == 'end' and elem.tag == 'IdList':
        break
    xml.close()
