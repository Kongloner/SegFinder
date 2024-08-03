#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>

import re
import sys

class Submitter:

  def __init__(self):
    self.acc = 'NA'
    self.lab_name = 'NA'
    self.center_name = 'NA'
    self.contact_name = 'NA'

  def parse(self, submitter):
    self.acc = submitter.attrib.pop('acc', self.acc)
    self.lab_name = submitter.attrib.pop('lab_name', self.lab_name)
    self.center_name = submitter.attrib.pop('center_name', self.center_name)
    self.contact_name = submitter.attrib.pop('contact_name', self.contact_name)

  def show(self):
    print("Submitter:\n\tAcc: {0}         \
                     \n\tCenter_name: {1} \
                     \n\tLab_name: {2}    \
                     \n\tContact_name: {3}".format(self.acc,
                                                   self.center_name,
                                                   self.lab_name,
                                                   self.contact_name))
