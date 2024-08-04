# -*- coding: utf-8 -*-
#
#  lineages.py
#
#  Copyright 2016 The University of Sydney
#  Author: Jan P Buchmann <lejosh@members.fsf.org>
#  Description:
#
#  Version: 0
import sys
import json

class Taxon:

   def __init__(self):
     self.taxid = 0
     self.name = 'NA'
     self.rank = 'NA'
     self.division = 'NA'
     self.is_query = False

class Lineage:
  """
  The base class Lineage. Basically, the Eukaryota NCBI Lineage template.
  Should work for most encountered taxonomies. Designed for NCBI taxonomies [0]
  and will be changed if anything more generic is needed.  All 'no rank' values
  are discarded from the lineage for now. They cannot be distinguished since
  the lineage string in NCBI's taxonomy XML does not indicate missing fields,
  rendering a position dependent identification unfeasible.

  References:
  [0]: http://www.ncbi.nlm.nih.gov/taxonomy
  """
  def __init__(self):
    self.typ = 'euk'
    self.query = Taxon()
    self.taxons = []
    self.taxid_alias = {}
    self.name_alias = {}
    self.ranks = {
                    'superkingdom' : 0,
                    'kingdom'      : 1,
                    'phylum'       : 2,
                    'subphylum'    : 3,
                    'class'        : 4,
                    'superorder'   : 5,
                    'order'        : 6,
                    'suborder'     : 7,
                    'family'       : 8,
                    'subfamily'    : 9,
                    'genus'        : 10,
                    'subgenus'     : 11,
                    'species'      : 12
                  }
    self.lineage = [Taxon() for x in range(len(self.ranks))]

  def normalize_lineage(self):
    for i in self.taxons:
      if i.is_query:
        self.query = i
      if i.rank in self.ranks:
        self.lineage[self.ranks[i.rank]] = i

  def export(self):
    return self.lineage

  def export_json(self):
    lineage = [{'rank' : x.rank, 'taxid' : x.taxid, 'name' : x.name} for x in self.lineage]
    query = {'rank' : self.query.rank, 'taxid' : self.query.taxid, 'name' : self.query.name}
    return json.dumps([query, lineage])

  def print_lineage(self):
    print(self.query.taxid, '\t'.join(str(i.name) for i in self.lineage), sep='\t')


class UnknownLineage(Lineage):
  def __init__(self):
    super(UnknownLineage, self).__init__()
    self.typ = 'unk'
    self.lineage = []

class VirusLineage(Lineage):
  """
  An inherited Taxon class for viruses.
  The default hierarchy is adapted for viral taxa according to ICTV [0]
  Ranks passed into the class need to be dictionaries with the following
  keys/values setup:

    e.g. Enterobacteria phage T4T [1]:
    # Key (Description)                    : Value (Rank)
      'Viruses'                            : 'superkingdom',
      'dsDNA viruses, no RNA stage'        : 'no rank',
      'Hepadnaviridae'                     : 'family',
      'Caudovirales'                       : 'order',
      'Myoviridae'                         : 'family',
      'Tevenvirinae'                       : 'subfamily',
      'T4likevirus'                        : 'genus',
      'Enterobacteria phage T4 sensu lato' : 'species',
      'Enterobacteria phage T4'            : 'no rank'

  NCBI does not distinguisehd between DNA reverse transcribing viruses
  (Baltimore 6, Hepadnaviridae) and DNA reverse transcribing viruses (Baltimore
  7, Caulimoviridae), this class uses the corresponding taxid to make this
  distinction (taken from [2]).

  References:
  [0]: http://www.ictvonline.org/virusTaxInfo.asp
  [1]: http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=857277&lvl=3&lin=f&keep=1&srchmode=1&unlock
  [2]: http://viralzone.expasy.org/all_by_species/235.html
  """
  def __init__(self):
    super(VirusLineage, self).__init__()
    self.typ = 'vrs'
    self.ranks = {
                    'superkingdom' : 0,
                    'group'        : 1,
                    'order'        : 2,
                    'family'       : 3,
                    'subfamily'    : 4,
                    'genus'        : 5,
                    'species'      : 6
                 }
    self.lineage = [Taxon() for x in range(len(self.ranks))]

  def add_lineage(self, taxons):
    self.normalize_lineage(taxons)

  def normalize_lineage(self):
    baltimore = {
                  35237  : 1, # dsDNA viruses, no RNA stage
                  29258  : 2, # ssDNA viruses
                  35325  : 3, # dsRNA viruses
                  35278  : 4, # ssRNA positive-strand viruses, no DNA stage
                  35301  : 5, # ssRNA negative-strand viruses
                  35268  : 6, # Retro-transcribing viruses
                  10404  : 7, # DNA reverse transcribing viruses, Hepadnaviridae
                  186534 : 7, # DNA reverse transcribing viruses, Caulimoviridae
                }

    buchmann = {  # Extended baltimore using bitmasks
                  35237   :   5, # dsDNA viruses, no RNA stage
                  29258   :   9, # ssDNA viruses
                  35325   :   6, # dsRNA viruses
                  35278   :  10, # ssRNA positive-strand viruses, no DNA stage
                  35301   :  26, # ssRNA negative-strand viruses
                  35268   :  42, # Retro-transcribing viruses
                  10404   :  37, # DNA reverse transcribing viruses, Hepadnaviridae
                  186534  :  37, # DNA reverse transcribing viruses, Caulimoviridae
                  12877   :  64, # Satellites (clade)
                  198600  :  64, # Satellite Viruses
                  1778568 :  73, # ssDNA satellites
                  198607  : 134, # Double-stranded RNA satellites nucleic acid
                  1250315 : 130, # RNA Satellites nucleic acid
                  361688  : 137, # Single stranded DNA satellites nucleic acid
                  373507  : 138, # Single stranded RNA satellites nucleic acid
                  198610  : 128  # unclassified Satellite Nucleic Acids
                }

    for i in self.taxons:
      if i.is_query:
        self.query = i
      if i.taxid in baltimore:
        i.rank = 'group'
        i.name = buchmann[i.taxid]
      if i.rank in self.ranks:
        self.lineage[self.ranks[i.rank]] = i


class ArchaeaLineage(Lineage):
  """
  The archaea Lineage. Inherits the Lineage base class.
  Taxonomy class for archaeas on NCBI.
  """
  def __init__(self):
    super(ArchaeaLineage, self).__init__()
    self.typ = 'arc'
    self.ranks = {
                    'superkingdom' : 0,
                    'phylum'       : 1,
                    'class'        : 2,
                    'order'        : 3,
                    'family'       : 4,
                    'genus'        : 5,
                    'species'      : 6
                  }
    self.lineage = [Taxon() for x in range(len(self.ranks))]

class BacteriaLineage(Lineage):
  """
  The bacteria Lineage. Inherits the Lineage base class.
  Taxonomy class for bacteria on NCBI. So far it's identical to the Archaela.
  """
  def __init__(self):
    super(BacteriaLineage, self).__init__()
    self.typ = 'bac'
    self.ranks = {
                    'superkingdom' : 0,
                    'phylum'       : 1,
                    'class'        : 2,
                    'order'        : 3,
                    'family'       : 4,
                    'genus'        : 5,
                    'species'      : 6
                  }
    self.lineage = [Taxon() for x in range(len(self.ranks))]


class ViroidLineage(Lineage):
  """
  The Viroid Lineage. Inherits the Lineage base class.
  Taxonomy class for viroids on NCBI. Expands when necessary.
  """
  def __init__(self):
    super(ViroidLineage, self).__init__()
    self.typ = 'vrs'
    self.ranks = {
                    'superkingdom' : 0,
                    'family'       : 4,
                    'genus'        : 5,
                    'species'      : 6
                  }
    self.lineage = [Taxon() for x in range(len(self.ranks))]
