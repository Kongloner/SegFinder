#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#  \file ncbi.callimachus_pubmed.py
#  \copyright 2015-2018 The University of Sydney
#  \author Jan P Buchmann <lejosh@members.fsf.org>
#  \description Fetch NCBI pubmed info for NCBI accession and uids
#  \version 1.0.0
#-------------------------------------------------------------------------------
import os
import sys
import argparse


sys.path.insert(1, os.path.join(sys.path[0], '../../include/blib/ncbi/src'))
import edirect.callimachus.ncbi_callimachus
import edirect.efetch.efetch_analyzer
import pubmed.xml_parser

class PubmedAnalyzer(edirect.efetch.efetch_analyzer.EfetchAnalyzer):

  def __init__(self):
    super().__init__()
    self.parser = pubmed.xml_parser.NcbiPubmedXmlParser()
    self.library = {}

  def analyze_result(self, request):
    self.library.update(self.parser.parse(request.response))

  def list_results(self, linksets):
    journal_header = ["Journal_Title", "Journal_Volume", "Journal_Issue",
                      "Journal_Pages", "Journal_PubYear", "Journal_PubMonth"]
    author_header = ["Name / Lastname / Initials / Affiliation(s)"]
    header = ["Query", "PMID", "DOI", "Title"] + journal_header + author_header
    print('\t'.join( x for x in header))
    for i in linksets:
      for j in linksets[i].links:
        if j in self.library:
          print(i, end='\t')
          self.show_article(self.library[j])

  def show_article(self, article):
    print("{}\t{}\t{}".format(article.pmid, article.doi, article.title), end='\t')
    print("{}\t{}\t{}\t{}\t{}\t{}".format(article.journal.title, article.journal.volume,
                              article.journal.issue, article.journal.pages,
                              article.journal.pubdate.year,
                              article.journal.pubdate.month), end='\t')
    print("\"", end='')
    if len(article.authors) > 0:
      print("{}/{}/{}".format(article.authors[0].lastname,
                              article.authors[0].name, article.authors[0].initials), end='')
      for i in article.authors[0].affiliations:
        print("/"+self.parser.affiliations[i], end='')
    if len(article.authors) > 1:
      for i in article.authors[1:]:
        print("\t{}/{}/{}".format(i.lastname, i.name, i.initials), end='')
        for j in i.affiliations:
          print("/"+self.parser.affiliations[j], end='')
      print("\"")

class PubmedCallimachus(edirect.callimachus.ncbi_callimachus.NcbiCallimachus):

  def __init__(self, email):
    super().__init__(email)
    self.options={'db':'pubmed', 'retmode':'xml'}

def main():
  ap = argparse.ArgumentParser(description='Callimachus Pubmed. Fetch NCBI Pubmed \
                               details for NCBI uids or accessions. Example: \
                               ./ncbi_callimachus.py -e your@email -u  CM000880 KZ622962 -db nuccore')
  ap.add_argument('-db', type=str, required=True,
                  help='NCBI database name for input accessions or uids, e.g. nuccore'),
  ap.add_argument('-e', '--email', type=str, required=True,
                  help='email address, required by NCBI')
  ap.add_argument('-u', '--uids', nargs='*',
                  help='List of accession or uids. If from STDIN, one per line.\
                        Otherwise, space separated, e.g. CM000880 KZ622962')

  args = ap.parse_args()
  uids = []
  if not args.uids:
    for i in sys.stdin:
      uids.append(i.strip())
  else:
    uids = args.uids
  pa = PubmedAnalyzer()
  pc = PubmedCallimachus(args.email)
  linker = pc.link(args.db, 'pubmed', uids)
  pc.fetch(linker, pc.options, analyzer=pa)
  pa.list_results(linker.linksets)
  return 0

if __name__ == '__main__':
  main()
