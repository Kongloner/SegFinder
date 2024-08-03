#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>

import sys

class Organism:

  def __init__(self):
    self.taxid = 0
    self.scientific_name = 'NA'


  def parse(self, organism):
    self.taxid = organism.attrib.pop('taxid', self.taxid)
    self.scientific_name = organism.attrib.pop('ScientificName', self.scientific_name)

  def show(self):
    print("Organism:\n\tTaxid: {0} \
                    \n\tScientific Name: {1}".format(self.taxid,
                                                     self.scientific_name))
