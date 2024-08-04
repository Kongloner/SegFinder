#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>

import sys

class Experiment:

  def __init__(self):
    self.acc = 'NA'
    self.name = 'NA'
    self.ver = 0
    self.status = 'NA'

  def parse(self, experiment):
    self.acc = experiment.attrib.pop('acc', self.acc)
    self.ver = experiment.attrib.pop('ver', self.ver)
    self.name = experiment.attrib.pop('name', self.name)
    self.status = experiment.attrib.pop('status', self.status)

  def show(self):
    print("Experiment:\n\tAcc: {0} \
                     \n\tVersion: {1} \
                     \n\tName: {2}    \
                     \n\tStatus: {3}".format(self.acc,
                                             self.ver,
                                             self.name,
                                             self.status))
