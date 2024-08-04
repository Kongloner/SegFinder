#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  basespace.py
#
#  Copyright 2016 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0


import sys
import json

class Fetch:

  def __init__(self):
    self.token = ''
    self.client_id = '46b11f792c294056ad694f1714d1daf2'
    self.client_secret = 'd8a52ca1016a44bdb5bf628ba14f9fb5'
    self.baseaddres = 'http://api.basespace.illumina.com/'
