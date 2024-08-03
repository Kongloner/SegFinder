#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>

import sys

class Bioproject:

  def __init__(self):
    self.acc = 'NA'

  def parse(self, bioproject):
    self.acc = bioproject.text if bioproject.text != None else self.acc

  def show(self):
    print("Bioproject:\n\tAcc: {0}".format(self.acc))
