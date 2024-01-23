import argparse
import pandas as pd
import numpy as np
import argparse
import os
import logging
from Bio import SeqIO
from os import system


class Trim_contamination(object):
    def __init__(self,db,out_tsv,threads,evalue):
        """Instantiate the class."""
        self.threads = threads 
        self.out_tsv = out_tsv
        self.db = db
        self.evalue = evalue
        self.logger = logging.getLogger('timestamp')
    
    def run(self,input_file,output_nt_fasta):

        system(f'blastn -query {input_file} \
               -db {self.db} \
               -out {self.out_tsv} -evalue {self.evalue} \
               -outfmt "6 qacc qlen sseqid slen pident length qstart qend sstart send evalue bitscore qcovs" \
               -num_threads {self.threads} \
               -max_target_seqs 5')

        blastn_table = pd.read_csv(self.out_tsv, sep='\t', 
                                   names = ["qacc","qlen","NT_sseqid","NT_slen","NT_pident","NT_length",
                                            "qstart","qend","NT_sstart","NT_send","NT_evalue","NT_bitscore","NT_qcovs"],encoding = "utf-8")


        ID_list = blastn_table['qacc'].to_list()
        dict_fasta = SeqIO.to_dict(SeqIO.parse(input_file, "fasta"))

        with open(output_nt_fasta, 'w') as fw:
            for seq_id in dict_fasta.keys():
                if seq_id in ID_list:                                                                                      
                    line = blastn_table.loc[blastn_table['qacc'] == seq_id]
                    qstart = int(min(line["qstart"]))
                    qend = int(max(line["qend"]))
                    origin_qlen = len(str(dict_fasta[seq_id].seq))
                    now_start = qstart if qstart < qend else qend
                    now_end = qend if qstart < qend else qstart
                    left = now_start-1
                    right = origin_qlen-(now_start-1) - int(qend-qstart+1)
                    if left > right and left > 600:
                        left_seq = str(dict_fasta[seq_id].seq)[:left]
                        fw.write(">"+seq_id + '\n')
                        fw.write(left_seq + '\n')
                    elif right > left and right > 600:
                        right_seq = str(dict_fasta[seq_id].seq)[now_end:]
                        fw.write(">"+seq_id + '\n')
                        fw.write(right_seq + '\n')
                    else:
                        continue
                else:
                    fw.write(">"+seq_id + '\n')
                    fw.write(str(dict_fasta[seq_id].seq) + '\n')
        return output_nt_fasta
    

def parse_arguments():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        usage=argparse.SUPPRESS,
        description="Centroid based sequence clustering"
    )
    parser.add_argument('--input', type=str, required=True, metavar='PATH',
        help="""Path to nucleotide sequences""")
    parser.add_argument('--out_fasta', type=str, required=True, metavar='BASENAME',
        help="""Path to output file""")
    parser.add_argument('--out_tsv', type=str, metavar='PATH',
        help="")
    parser.add_argument('--threads', type=str, metavar='PATH',
        help="")
    parser.add_argument('--evalue', type=str, metavar='PATH',
        help="")
    parser.add_argument('--db', type=str, required=True, metavar='PATH',
        help="""Path to the blastn database""")
    return vars(parser.parse_args())


args = parse_arguments()
if __name__ == '__main__':
    args['out'] = Trim_contamination(args['db'],args['out_tsv'],args['threads'],args['evalue']).run(
        args['input'],args['out_fasta'])

