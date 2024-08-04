# -*- coding: utf-8 -*-
#
#  sequence_request_parser.py
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

class NcbiSimpleSequenceRequestParser:

  def __init__(self):
    super().__init__()
    self.fetched = 0
    self.has_callback = False
    self.db = ''

  def check_response(self, response):
    for event, elem in ET.iterparse(response, events=["start", "end"]):
      if elem.tag == 'TSeq' and event == 'end':
        self.fetched += 1

  def parse(self, xml):
    response = io.StringIO(xml.read().decode())
    self.check_response(response)
    print(response.getvalue())
    response.close()
