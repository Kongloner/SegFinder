#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>

import sys

class Study:

  def __init__(self):
    self.acc = 'NA'
    self.name = 'NA'

  def parse(self, study):
    self.acc = study.attrib.pop('acc', self.acc)
    self.name = study.attrib.pop('name', self.name)

  def show(self):
    print("Study:\n\tAcc: {0} \
                 \n\tName: {1}".format(self.acc, self.name))
