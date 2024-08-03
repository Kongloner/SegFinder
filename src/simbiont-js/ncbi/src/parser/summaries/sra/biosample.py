#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>

import sys

class Biosample:

  def __init__(self):
    self.acc = 'NA'

  def parse(self, biosample):
    self.acc = biosample.text if biosample.text != None else self.acc

  def show(self):
    print("Biosample:\n\tAcc: {0}".format(self.acc))
