#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>

import sys

class Instrument:

  def __init__(self):
    self.instrument = 'NA'
    self.model = 'NA'

  def parse(self, instrument):
    for i in instrument.attrib:
      self.instrument = i
      self.model = instrument.attrib[i]

  def show(self):
    print("Instrument:\n\tInstrument: {0} \
                      \n\tModel: {1}".format(self.instrument,
                                             self.model))
