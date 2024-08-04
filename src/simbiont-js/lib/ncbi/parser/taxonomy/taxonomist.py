# -*- coding: utf-8 -*-
#
#  taxonomy.py
#
#  Copyright 2015 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0

import sys
import xml.etree.ElementTree as ET
from . import lineages

class Taxonomist:
  """
  The Taxonomist class takes care of the XML parsing of NCBI taxonomy requests.
  It's based on the genbank taxonomy files on ftp.ncbi.nih.gov
  """
  def __init__(self):
    self.lineages = []
    self.query = lineages.Taxon()

  def speciate(self, taxa, lineage):
    lineage.taxons = taxa
    lineage.normalize_lineage()
    return lineage

  def parse_taxon(self, event, elem, taxon):
    if event == 'end':
      if elem.tag == 'TaxId':
        taxon.taxid = elem.text
      if elem.tag == 'ScientificName':
        taxon.name = elem.text
      if elem.tag == 'Rank':
        taxon.rank = elem.text
      if elem.tag == 'Division':
        taxon.division = elem.text

  def parse(self, xml, t=lineages.Taxon(), qry=lineages.Taxon()):
    is_lineage = False
    lineage_typ = 'NA'
    taxa = []
    for event, elem in ET.iterparse(xml, events=["start", "end"]):
      if event == 'start' and elem.tag == 'LineageEx':
        is_lineage = True
      if event == 'end' and elem.tag == 'LineageEx':
        is_lineage = False

      if is_lineage == False:
        if elem.tag == 'Taxon' and event == 'start':
          taxa = []
          lineage_typ = 'NA'
          qry = lineages.Taxon()
          qry.is_query = True
        elif elem.tag == 'Taxon' and event == 'end':
          taxa.append(qry)
          self.lineages.append(self.identify(taxa, lineage_typ))
        else:
          self.parse_taxon(event, elem, qry)

      if is_lineage == True:
        if elem.tag == 'Taxon' and event == 'start':
          t = lineages.Taxon()
        elif elem.tag == 'Taxon' and event == 'end':
          taxa.append(t)
        else:
          self.parse_taxon(event, elem, t)
          if t.rank == 'superkingdom':
            lineage_typ = t.name.lower()

  def identify(self, taxa, lin_typ):
    if lin_typ == 'archaea':
      return self.speciate(taxa, lineages.ArchaeaLineage())
    elif lin_typ == 'bacteria':
      return self.speciate(taxa, lineages.BacteriaLineage())
    elif lin_typ == 'eukaryota':
      return self.speciate(taxa, lineages.Lineage())
    elif lin_typ == 'viroids':
      return self.speciate(taxa, lineages.VirusLineage())
    elif lin_typ == 'viruses':
      return self.speciate(taxa, lineages.VirusLineage())
    else:
      return self.speciate(taxa, lineages.UnknownLineage())
