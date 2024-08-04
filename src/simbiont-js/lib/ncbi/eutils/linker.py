# -*- coding: utf-8 -*-
#
#  linker.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0


import io
import sys
from .. import request_base

class Linker:

  def __init__(self):
    self.from_db = ''
    self.to_db = ''
    self.linkcmd = ''


#<eLinkResult><LinkSet><DbFrom>protein</DbFrom><IdList><Id>15718680</Id><Id>119703751</Id><Id>157427902</Id></IdList><LinkSetDb><DbTo>gene</DbTo><LinkName>protein_gene</LinkName><Link><Id>522311</Id></Link><Link><Id>16428</Id></Link><Link><Id>3702</Id></Link></LinkSetDb></LinkSet></eLinkResult>
