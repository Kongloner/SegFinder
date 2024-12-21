import os
import subprocess
import argparse

def run_command(command):
    subprocess.run(command, shell=True, check=True)

def process_sequences(input_file, output_file, num_threads, accession2taxid_path, taxdump_path, ref_viruses_path):
    # Define paths based on the input and output filenames
    out_dir = os.path.dirname(output_file)
    base_output = os.path.splitext(output_file)[0]

    nt_fasta = input_file
    nt_fasta_id = base_output + ".fasta.id"
    nt_fasta_id_noVirus = base_output + ".fasta.id_noVirus"
    nt_fasta_id_noVirus_accNum = base_output + ".fasta.id_noVirus_accNum"
    nt_fasta_id_noVirus_accNum_taxid = base_output + ".fasta.id_noVirus_accNum_taxid"
    nt_fasta_id_noVirus_accNum_taxid_results = base_output + ".fasta.id_noVirus_accNum_taxid_results"
    nt_noVirus_fasta = base_output + "_noVirus.fasta"
    id2_txt = base_output + "_id2.txt"
    id3_txt = base_output + "_id3.txt"
    id3_accessionID = base_output + "_id3.accessionID"
    id3_accessionID_fasta = base_output + "_id3.accessionID.fasta"
    id3_accessionID_fasta_csv = base_output + "_id3.accessionID.fasta.csv"
    id3_virus_accession = base_output + "_id3.virus.accession"
    id3_virus_accessionID = base_output + "_id3.virus.accessionID"
    id3_diff_txt = base_output + "_id3-diff.txt"
    id3_novirus_accessionID_fasta = base_output + "_id3-novirus.accessionID.fasta"
    nt_noVirus_update_fasta = base_output + "_noVirus-update.fasta"
    nt_noViruses = base_output + "_noViruses"

    # Use seqkit to extract sequence names
    run_command(f"seqkit seq -j {num_threads} -n {nt_fasta} > {nt_fasta_id}")

    # Filter out lines containing "virus"
    run_command(f"grep -v -i 'virus' {nt_fasta_id} > {nt_fasta_id_noVirus}")

    # Further filter out other virus-related keywords
    keywords = ["viruses", "riboviria", "phage", "viridae", "proviral"]
    temp_file = nt_fasta_id_noVirus + "_tmp"
    run_command(f"cp {nt_fasta_id_noVirus} {temp_file}")
    for keyword in keywords:
        run_command(f"grep -v -i '{keyword}' {temp_file} > {temp_file}_filtered")
        run_command(f"mv {temp_file}_filtered {temp_file}")
    run_command(f"mv {temp_file} {nt_fasta_id_noVirus}")

    # Extract sequence numbers and store them
    run_command(f"sed 's/ /\t/g' {nt_fasta_id_noVirus} | cut -f1 > {nt_fasta_id_noVirus_accNum}")

    # Filter using grep
    run_command(f"grep -F -f {nt_fasta_id_noVirus_accNum} -w {accession2taxid_path} > {nt_fasta_id_noVirus_accNum_taxid}")

    # Use taxonkit to get taxonomy information
    run_command(f"cut -f3 {nt_fasta_id_noVirus_accNum_taxid} | sort -u | taxonkit --data-dir {taxdump_path} lineage | awk '$2>0' | taxonkit --data-dir {taxdump_path} reformat -f '{{k}}\t{{p}}\t{{c}}\t{{o}}\t{{f}}\t{{g}}\t{{s}}' -F | cut -f1,3- > {nt_fasta_id_noVirus_accNum_taxid_results}")

    # Filter out virus-related results
    run_command(f"grep -v -i 'viruses' {nt_fasta_id_noVirus_accNum_taxid_results} | cut -f1 > {base_output}_noVirusID")
    run_command(f"grep -F -f {base_output}_noVirusID -w {nt_fasta_id_noVirus_accNum_taxid} | cut -f2 > {base_output}_noVirusAccession")

    # Extract non-virus sequences
    run_command(f"seqtk subseq {nt_fasta} {base_output}_noVirusAccession > {nt_noVirus_fasta}")
    run_command(f"cut -f2 {nt_fasta_id_noVirus_accNum_taxid} | sort | uniq > {id2_txt}")

    # Perform diff functionality
    with open(nt_fasta_id_noVirus_accNum, "r") as file1, open(id2_txt, "r") as file2:
        diff = set(file1).difference(file2)
    with open(id3_txt, "w") as output:
        for line in diff:
            output.write(line)

    # Further filter sequences and perform BLAST comparison
    run_command(f"grep -F -f {id3_txt} -w {nt_fasta_id_noVirus} > {id3_accessionID}")
    run_command(f"seqtk subseq {nt_fasta} {id3_accessionID} > {id3_accessionID_fasta}")
    run_command(f"blastn -query {id3_accessionID_fasta} -db {ref_viruses_path} -out {id3_accessionID_fasta_csv} -evalue 1E-3 -outfmt '6 qseqid sacc staxid salltitles pident evalue' -max_target_seqs 1 -num_threads {num_threads}")
    run_command(f"cut -f1 {id3_accessionID_fasta_csv} | sort | uniq > {id3_virus_accession}")
    run_command(f"grep -F -f {id3_virus_accession} -w {id3_accessionID} > {id3_virus_accessionID}")

    # Perform diff functionality again
    with open(id3_accessionID, "r") as file1, open(id3_virus_accessionID, "r") as file2:
        diff = set(file1).difference(file2)
    with open(id3_diff_txt, "w") as output:
        for line in diff:
            output.write(line)

    # Extract final non-virus sequences
    run_command(f"seqtk subseq {id3_accessionID_fasta} {id3_diff_txt} > {id3_novirus_accessionID_fasta}")

    # Merge results and create a new BLAST database
    run_command(f"cat {nt_noVirus_fasta} {id3_novirus_accessionID_fasta} > {nt_noVirus_update_fasta}")
    run_command(f"makeblastdb -in {nt_noVirus_update_fasta} -dbtype nucl -out {nt_noViruses} -parse_seqids")

    # Remove intermediate files
    intermediate_files = [
        nt_fasta_id, nt_fasta_id_noVirus, nt_fasta_id_noVirus_accNum, nt_fasta_id_noVirus_accNum_taxid,
        nt_fasta_id_noVirus_accNum_taxid_results, nt_noVirus_fasta, id2_txt, id3_txt,
        id3_accessionID, id3_accessionID_fasta, id3_accessionID_fasta_csv, id3_virus_accession,
        id3_virus_accessionID, id3_diff_txt, id3_novirus_accessionID_fasta,
        f"{base_output}_noVirusAccession", f"{base_output}_noVirusID"
    ]
    for file in intermediate_files:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process sequences and filter out viral sequences.")
    parser.add_argument("--threads", type=int, required=True, help="Number of threads to use.")
    parser.add_argument("--input", type=str, required=True, help="Input file for NT sequences.")
    parser.add_argument("--output", type=str, required=True, help="Output file for processed results.")
    parser.add_argument("--nucl_gb_accession2taxid_path", type=str, required=True, help="Path to nucl_gb.accession2taxid file.")
    parser.add_argument("--taxdump_path", type=str, required=True, help="Path to taxdump directory.")
    parser.add_argument("--ref_viruses_path", type=str, required=True, help="Path to ref_viruses_rep_genomes database.")

    args = parser.parse_args()
    process_sequences(args.input, args.output, args.threads, args.nucl_gb_accession2taxid_path, args.taxdump_path, args.ref_viruses_path)

