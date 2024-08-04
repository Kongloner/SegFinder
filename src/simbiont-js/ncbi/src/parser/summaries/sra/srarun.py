#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>

import sys

class SraRun:

  def __init__(self, i):
    self.acc = i.attrib.get('acc', 'NA')
    self.cluster_name = i.attrib.pop('cluster_name', 'NA')
    self.total_bases = i.attrib.pop('total_bases', 0)
    self.total_spots = i.attrib.pop('total_spots', 0)
    self.load_done = i.attrib.pop('load_done', 'NA')
    self.staticDataAvail = i.attrib.pop('static_data_available', 'NA')
    self.isPublic = i.attrib.pop('is_public', 'NA')

  def show(self):
    print("SRA run {0}:\n\tBases:   {1}     \
                       \n\tSpots:   {2}     \
                       \n\tCluster: {3}     \
                       \n\tStatic data: {4}  \
                       \n\tPublic: {5}".format(self.acc,
                                               self.total_bases,
                                               self.total_spots,
                                               self.cluster_name,
                                               self.staticDataAvail,
                                               self.isPublic))
