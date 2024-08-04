#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>

import re
import xml.etree.ElementTree as et

class Summary:

    def __init__(self):
      self.title = 'NA'
      self.platform = 'NA'
      self.instrument_model = 'NA'
      self.total_runs = 0
      self.total_spots = 0
      self.total_bases = 0
      self.total_size = 0
      self.cluster_name = ''
      #self.load_done = False  # no clue what this really indicates. SRA docs are not clear on that

    def parse(self, summary):
      for i in summary:
        if i.tag == 'Title':
          self.title = i.text if i.text != None else self.title
        if i.tag == 'Platform':
          self.platform = i.text if i.text != None else self.platform
          self.instrument_model = i.attrib.pop('instrument_model', "NA")
        if i.tag == 'Statistics':
          self.total_runs = i.attrib.pop('total_runs', self.total_runs)
          self.total_size = i.attrib.pop('total_size', self.total_size)
          self.total_spots = i.attrib.pop('total_spots', self.total_spots)
          self.total_bases = i.attrib.pop('total_bases', self.total_bases)
          #self.load_done = i.attrib.pop('load_done', )
          self.cluster_name = i.attrib['cluster_name']

    def show(self):
      print("Summary:\n\tTitle: {0}       \
                     \n\tPlatform: {1}    \
                     \n\tInstrument: {2}  \
                     \n\tRuns: {3}        \
                     \n\tSize: {4}        \
                     \n\tBases: {5}       \
                     \n\tSpots: {6}       \
                     \n\tCluster_name: {7}".format(self.title,
                                                   self.platform,
                                                   self.instrument_model,
                                                   self.total_runs,
                                                   self.total_size,
                                                   self.total_bases,
                                                   self.total_spots,
                                                   self.cluster_name))
