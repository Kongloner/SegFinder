#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>

import sys

class Sample:

  def __init__(self):
    self.acc = 'NA'
    self.name = 'NA'

  def parse(self, sample):
    self.acc = sample.attrib.pop('acc', self.acc)
    self.name = sample.attrib.pop('name') if len(sample.attrib['name']) > 0 else self.name

  def show(self):
    print("Sample:\n\tAcc: {0} \
                  \n\tName: {1}".format(self.acc, self.name))
