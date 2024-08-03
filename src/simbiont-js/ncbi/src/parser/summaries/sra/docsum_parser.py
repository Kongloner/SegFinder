#  Copyright 2017 The University of Sydney
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
# author: Jan Piotr Buchmann <jan.buchmann@sydney.edu.au>
#
# http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?save=efetch&db=sra&rettype=fullxml&term=SRX001682
#
# ftp://ftp-trace.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByExp/sra/SRX/SRX000/SRX000122/
#  uid for two runs: 25984, uid for numerous runs: 7190
# https://trace.ncbi.nlm.nih.gov/Traces/sra/?run=SRR021354

import sys
import json
import xml.etree.ElementTree as et

from .import summary
from .import submitter
from .import experiment
from .import study
from .import organism
from .import sample
from .import instrument
from .import library
from .import bioproject
from .import biosample
from .import srarun

class NcbiSraDocsumParser:

  class Header:
    def __init__(self):
      self.typ = ''
      self.version = 0.0

    def parse(self, header):
      self.typ = header.pop('type')
      self.version = header.pop('version')

  class Uid:

    def __init__(self, uid):
      self.uid = uid
      self.summary = summary.Summary()
      self.submitter = submitter.Submitter()
      self.experiment = experiment.Experiment()
      self.study = study.Study()
      self.organism = organism.Organism()
      self.sample = sample.Sample()
      self.instrument = instrument.Instrument()
      self.library = library.Library()
      self.bioproject = bioproject.Bioproject()
      self.biosample = biosample.Biosample()
      self.sraruns = []

    def show(self):
      print("UID: ", self.uid)
      self.summary.show()
      self.submitter.show()
      self.experiment.show()
      self.study.show()
      self.organism.show()
      self.sample.show()
      self.instrument.show()
      self.library.show()
      self.bioproject.show()
      self.biosample.show()
      for i in self.sraruns:
        i.show()

  def __init__(self):
    self.uids = []
    self.header = self.Header()

  def parse(self, json_summary):
    summary = json.loads(json_summary)
    self.header.parse(summary.pop('header'))
    for i in summary['result']['uids']:
      uid = self.Uid(i)
      #print(uid)
      for j in et.fromstring(self.xml_decoder(summary['result'][i]['expxml'])):
        if j.tag == 'Summary':
          uid.summary.parse(j)
        elif j.tag == 'Submitter':
          uid.submitter.parse(j)
        elif j.tag == 'Experiment':
          uid.experiment.parse(j)
        elif j.tag == 'Study':
          uid.study.parse(j)
        elif j.tag == 'Organism':
          uid.organism.parse(j)
        elif j.tag == 'Sample':
          uid.sample.parse(j)
        elif j.tag == 'Instrument':
          uid.instrument.parse(j)
        elif j.tag == 'Library_descriptor':
          uid.library.parse(j)
        elif j.tag == 'Bioproject':
          uid.bioproject.parse(j)
        elif j.tag == 'Biosample':
          uid.biosample.parse(j)
        else:
          print("Unrecognized tag: {0}".format(j.tag), file=sys.stderr)
      self.parse_sraruns(uid, self.xml_decoder(summary['result'][i]['runs']))
      self.uids.append(uid)
      #uid.show()

  def parse_sraruns(self, uid, runs):
    for i in et.fromstring(runs):
      uid.sraruns.append(srarun.SraRun(i))

  def xml_decoder(self, expxml):
    xml = '<jpb>'
    xml += expxml.replace('&lt;', '<')
    xml = xml.replace('&gt;', '>')
    xml += '</jpb>'
    return xml
