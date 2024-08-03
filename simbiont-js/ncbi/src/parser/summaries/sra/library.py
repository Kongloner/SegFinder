#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>

import sys

class Library:

  def __init__(self):
    self.isPaired = False
    self.nominal_length = 0
    self.name = 'NA'
    self.strategy = 'NA'
    self.source = 'NA'
    self.selection = 'NA'

  def parse(self, library):
    for i in library:
      if i.tag == 'LIBRARY_NAME' and i.text != None:
        self.name = i.text
      if i.tag == 'LIBRARY_STRATEGY':
        self.strategy = i.text
      if i.tag == 'LIBRARY_SOURCE':
        self.source = i.text
      if i.tag == 'LIBRARY_SELECTION':
        self.selection = i.text
      if i.tag == 'LIBRARY_LAYOUT':
        for j in i:
          if j.tag == 'PAIRED':
            self.isPaired = True
            self.nominal_length = j.attrib.pop('NOMINAL_LENGTH', self.nominal_length)


  def show(self):
    print("Library:\n\tName: {0}            \
                   \n\tStrategy: {1}        \
                   \n\tPaired: {2}          \
                   \n\tNominal length: {3}  \
                   \n\tSource: {4}          \
                   \n\tSelection: {5}".format(self.name,
                                              self.strategy,
                                              self.isPaired,
                                              self.nominal_length,
                                              self.source,
                                              self.selection))
