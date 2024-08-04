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
          qry = qry=lineages.Taxon()
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
      lin = self.speciate(taxa, lineages.ArchaeaLineage())
      return (self.speciate(taxa, lineages.ArchaeaLineage()))
    elif lin_typ == 'bacteria':
      lin = self.speciate(taxa, lineages.BacteriaLineage())
      return (self.speciate(taxa, lineages.BacteriaLineage()))
    elif lin_typ == 'eukaryota':
      lin = self.speciate(taxa, lineages.Lineage())
      return (self.speciate(taxa, lineages.Lineage()))
    elif lin_typ == 'viroids':
      lin = self.speciate(taxa, lineages.VirusLineage())
      return (self.speciate(taxa, lineages.VirusLineage()))
    elif lin_typ == 'viruses':
      lin = self.speciate(taxa, lineages.VirusLineage())
      return (self.speciate(taxa, lineages.VirusLineage()))
    else:
      lin = lineages.UnknownLineage()
      lin.taxons = taxa
      return lin


class Taxonomy:

  def __init__(self):
    print("------------------------------------------")
    print("ncbi.taxonomy::Obsolete, adjust code")
    print("------------------------------------------")
    sys.exit()
    #for taxon in taxatree.findall('Taxon'):
      #div = taxon.find('Division').text
      #if div == 'Environmental samples':
        #return
      #l = self.get_lineage_class(div)
      #t = lineages.Taxon()
      #t.taxid = int(taxon.find('TaxId').text)
      #t.name  = taxon.find('ScientificName').text
      #t.rank  = taxon.find('Rank').text
      #t.is_query = True
      #l.taxons.append(t)

      #for i in taxon.iter('OtherName'):
        #if i.tag == 'Synonym':
          #l.name_alias[i.text] = 1
        #if i.tag == 'OtherName':
          #l.name_alias[i.text] = 1
      #for i in taxon.iter('AkaTaxIds'):
        #for j in i.findall('TaxId'):
          #l.taxid_alias[int(j.text)] = 1
      #self.get_taxons(taxon, l.taxons)
      #l.normalize_lineage()
      #self.taxa.append(l)
