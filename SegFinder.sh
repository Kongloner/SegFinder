#!/bin/bash

# Usage function to display help message
usage(){
cat <<'EOF'
Usage
 [-o]... the directory to output the results; default ./
 [--indata]... the location of the raw data
 [--incontig]... the contig you want to search
 [--thread]... default 10
 [--cor]... correlation coefficient; default 0.8
 [--nt_noViruses]... the location of nt_noViruses database
 [--nt]... the location of nt database
 [--nr]... the location of nr database
 [--method]... the method to quantify the transcript abundances,salmon or RSEM,default salmon
 [--datatype]... the type of input data single(input 1) or double(input 2)
 [--taxidDB]... the location of prot.accession2taxid database
 [--rm_length]... the contigs whose length less than this value will be removed; default 600
 [--min_rdrp_multi]... minimum length of rdrp and their re-assembled contigs to be retained; default 100
 [--min_nordrp_multi]... minimum length of non-rdrp and their re-assembled contigs to be retained; default 20
 [--library_ID]... the library you want to search, can input multiple IDs separated by spaces
 [--preprocess]... whether to preprocess the raw fq data, 'true' or 'false'; default false
 [--assemble]... tthe tool to assemble the raw reads, megahit or spades; default spades
 [--only_rdrp_find]... 1 or 0, 1 means only find RNA virus RdRPs without any other analysis; default 0
 [--min_TPM]... if there exist the contig whose TPM is less than this value, the cluster it is in will be removed; default 200
 [--help]... display this help message
 [--version]... display version information
EOF
}

# Default parameters
thread=10
cor=0.8
rm_length=600
min_rdrp_multi=100
min_nordrp_multi=20
min_TPM=200
quantify_method="salmon"
preprocess="false"
assemble_method="spades"
only_rdrp_find=0
library_ID=""

# Parse command-line arguments
parameters=$(getopt -o o: --long indata:,incontig:,thread:,cor:,datatype:,nt:,nr:,method:,only_rdrp_find:,min_multi:,min_TPM:,assemble:,preprocess:,library_ID:,rm_length:,nt_noViruses:,taxidDB:,help,version -n "$0" -- "$@")
if [ $? -ne 0 ]; then echo "Try '$0 --help' for more information."; exit 1; fi

eval set -- "$parameters"

while true; do
    case "$1" in
        --indata) rawData_loc=$2; shift 2;;
        --incontig) contig=$2; shift 2;;
        --thread) thread=$2; shift 2;;
        --cor) cor=$2; shift 2;;
        --rm_length) rm_length=$2; shift 2;;
        --min_rdrp_multi) min_rdrp_multi=$2; shift 2;;
        --min_nordrp_multi) min_nordrp_multi=$2; shift 2;;
        --min_TPM) min_TPM=$2; shift 2;;
        --nt) nt_loc=$2; shift 2;;
        --nr) nr_loc=$2; shift 2;;
        --nt_noViruses) nt_noViruses_loc=$2; shift 2;;
        --library_ID) library_ID=$2; shift 2;;
        --datatype) datatype=$2; shift 2;;
        --method) quantify_method=$2; shift 2;;
        --assemble) assemble_method=$2; shift 2;;
        --only_rdrp_find) only_rdrp_find=$2; shift 2;;
        --preprocess) preprocess=$2; shift 2;;
        --taxidDB) taxidDB_loc=$2; shift 2;;
        -o) out_loc=$2; shift 2;;
        --version) echo "$0 version V1.0"; exit;;
        --help) usage; exit;;
        --) shift; break;;
        *) usage; exit 1;;
    esac
done

# Function to validate input parameters
validate_params() {
    if [[ $preprocess != "true" && $preprocess != "false" ]]; then
        echo "please input true or false!!! --preprocess"
        exit 1
    fi

    if [[ -z $rawData_loc ]]; then
        echo "please input the location of the raw data!!! --indata"
        exit 1
    fi

    if [[ -z $contig && -z $library_ID && $only_rdrp_find -eq 0 ]]; then
        echo "please input a contig name or a library_ID!!! --incontig or --library_ID"
        exit 1
    fi

    if [[ -z $nt_loc && $only_rdrp_find -eq 0 ]]; then
        echo "please input the location of nt!!! --nt"
        exit 1
    fi

    if [[ -z $nr_loc && $preprocess == "true" ]]; then
        echo "please input the location of nr!!! --nr"
        exit 1
    fi

    if [[ -z $nt_noViruses_loc && $only_rdrp_find -eq 0 ]]; then
        echo "please input the location of nt_noViruses database!!! --nt_noViruses"
        exit 1
    fi

    if [[ -z $datatype ]]; then
        echo "please input the type of input data!!! --datatype"
        exit 1
    fi

    if [[ -z $taxidDB_loc ]]; then
        echo "please input the location of prot.accession2taxid database!!! --taxidDB"
        exit 1
    fi

    if [[ $datatype -ne 1 && $datatype -ne 2 ]]; then
        echo 'please re_input the type of input data, 1 or 2, for 1 means single type, 2 means double'
        exit 1
    fi
}

# Call the validate_params function
validate_params

# Set output directories
if [ -z $out_loc ]; then
    out_loc="./"
fi
megahit=$out_loc/megahit
nr=$out_loc/nr
rdrp=$out_loc/rdrp
network=$out_loc/network
processed_data=$out_loc/processed_data

# Create output directories
mkdir -p "$megahit" "$nr" "$rdrp" "$network" "$processed_data"

chmod +x ./bin/align_and_estimate_abundance.pl
chmod +x ./bin/ORFfinder

#################################
present_loc=`pwd`
result_files=($(ls $rawData_loc/*.fq.gz | sed -E 's/_1.fq.gz|_2.fq.gz|.fq.gz//g' | xargs -n 1 basename | sort -u))

#########################part1#####data preprocessing###############################
if [ $preprocess == true ];then
	for file in "${result_files[@]}";
	do
#########################assemble###################################################
		if [ $datatype -eq 1 ]; then 
			fastp -i $rawData_loc/"$file".fq.gz -o $processed_data/"$file"-fp.fq.gz -w ${thread}
			ribodetector_cpu -l 100 -i $processed_data/"$file"-fp.fq.gz -t ${thread} -e norrna  -o $processed_data/"$file".clean.fq.gz
			rm $$processed_data/"$file"-fp.fq.gz
			rm $rawData_loc/fastp.html $rawData_loc/fastp.json
		fi
       if [ $datatype -eq 2 ]; then 
			fastp -i $rawData_loc/"$file"_1.fq.gz -I $rawData_loc/"$file"_2.fq.gz -o $processed_data/"$file"_1-fp.fq.gz -O  $processed_data/"$file"_2-fp.fq.gz -w ${thread}
			ribodetector_cpu -l 100 -i $processed_data/"$file"_1-fp.fq.gz $processed_data/"$file"_2-fp.fq.gz  -t ${thread} -e norrna  -o $processed_data/"$file".clean_{1,2}.fq.gz
			rm $processed_data/"$file"_1-fp.fq.gz $processed_data/"$file"_2-fp.fq.gz
			rm $rawData_loc/fastp.html $rawData_loc/fastp.json
		fi
				
		if [ $assemble_method == spades ]; then
			if [ $datatype -eq 1 ]; then spades.py --meta --phred-offset 33 -s $processed_data/"$file".clean.fq.gz -t ${thread} -o $processed_data/"$file".assemble; fi
			if [ $datatype -eq 2 ]; then spades.py --meta --phred-offset 33 -1 $processed_data/"$file".clean_1.fq.gz -2 $processed_data/"$file".clean_2.fq.gz -t ${thread} -o $processed_data/"$file".assemble; fi
			cat $processed_data/"$file".assemble/contigs.fasta | sed 's/ /_/g' | sed 's/=/_/g'| sed "s/>/>"$file"_/g" > $processed_data/"$file".assemble/"$file".fa_modify
		fi
###################################################################################		
	if [ $assemble_method == megahit ] || [ ! -s $processed_data/"$file".assemble/contigs.fasta ]; then rm  -rf $processed_data/"$file".assemble;
		if [ $datatype -eq 2 ]; then megahit -1 $processed_data/"$file".clean_1.fq.gz  -2 $processed_data/"$file".clean_2.fq.gz  --num-cpu-threads ${thread}  --memory 0.9  -o $processed_data/"$file".assemble; fi
		if [ $datatype -eq 1 ]; then megahit -r $processed_data/"$file".clean.fq.gz --num-cpu-threads ${thread} --memory 0.9 -o $processed_data/"$file".assemble; fi
		cat $processed_data/"$file".assemble/final.contigs.fa | sed 's/ /_/g' | sed 's/=/_/g'| sed "s/>/>"$file"_/g" > $processed_data/"$file".assemble/"$file".fa_modify
	  fi
	  cp $processed_data/"$file".assemble/"$file".fa_modify $processed_data/"$file".megahit.fa
#########################Finding rna virus RdRP######################################
	  diamond blastx \
			   -q $processed_data/"$file".megahit.fa \
			   -d ${nr_loc} \
			   -o $processed_data/"$file"_assemble_nr \
			   -e 1E-4 \
			   -k 1 \
			   -p ${thread} \
			   -f 6 qseqid qlen sseqid stitle pident length evalue sstart send   
       cp $processed_data/"$file"_assemble_nr $processed_data/"$file"_megahit_assemble_nr
       sed -i "s/#/_/" $processed_data/"$file"_megahit_assemble_nr
       cat $processed_data/"$file"_megahit_assemble_nr | cut -f3 | sort -u | grep -v "^[0-9]" | grep -v -e '^$' > $processed_data/"$file"_accession_list.txt.nr
       grep -F -f $processed_data/"$file"_accession_list.txt.nr $taxidDB_loc/prot.accession2taxid > $processed_data/"$file".taxid_table.txt.nr
       cat  $processed_data/"$file".taxid_table.txt.nr | cut -f3 -d$'\t' | sort -u > $processed_data/"$file".taxid_list.txt.nr
       python3 simbiont-js/tools/ncbi/ncbi.taxonomist.py --sep "|" -d < $processed_data/"$file".taxid_list.txt.nr | sed "s/|/\t/" | sed "s/\t[^|]*|/\t/" > $processed_data/"$file".lineage_table.txt.nr
       cat sqlite_table/sqlite_template.nr | sed "s/template/""$file""/g" > $processed_data/sqlite_"$file".nr
       sqlite3 $processed_data/sqlite_"$file".nr.summary.sql < $processed_data/sqlite_"$file".nr
       mv $processed_data/"$file"_megahit_assemble_nr.edited $processed_data/"$file"_megahit_assemble_nr.edited.tsv
       rm -rf $processed_data/"$file".taxid_table.txt.nr $processed_data/"$file".taxid_list.txt.nr $processed_data/"$file".lineage_table.txt.nr $processed_data/"$file".accession_list.txt.nr
       rm -rf $processed_data/sqlite_"$file".nr
       rm -rf $processed_data/sqlite_"$file".nr.summary.sql

	   grep -i "virus" $processed_data/"$file"_megahit_assemble_nr.edited.tsv > $processed_data/"$file"_assemble_nr.virus
	   cat $processed_data/"$file"_assemble_nr.virus | cut -f2 | sort -u > $processed_data/"$file"_assemble_nr.virus.list
	   seqtk subseq $processed_data/"$file".megahit.fa $processed_data/"$file"_assemble_nr.virus.list > $processed_data/"$file"_assemble_nr.virus.match
	   diamond makedb --in data/RdRP_only.fasta --db $processed_data/RdRP_only -p ${thread}
	   diamond  blastx \
		     --more-sensitive \
			 -q $processed_data/"$file"_assemble_nr.virus.match \
			 -d $processed_data/RdRP_only \
			 -o $processed_data/"$file"_assemble_nr.rdrp \
			 -e 1E-3 \
			 -k 1 \
             -p ${thread} \
             -f 6 qseqid qlen sseqid stitle pident length evalue qstart qend
	   cat $processed_data/"$file"_assemble_nr.rdrp | cut -f1 | sort -u > $processed_data/"$file"_assemble_nr.rdrp.list
	   seqtk subseq $processed_data/"$file"_assemble_nr.virus.match $processed_data/"$file"_assemble_nr.rdrp.list > $processed_data/"$file".rdrp.virus.match
	   Rscript src/R/blastn_nt_novirus.R --db ${nt_noViruses_loc} --evalue 1E-10 --input $processed_data/"$file".rdrp.virus.match --out_fasta $processed_data/"$file".rdrp.virus.match.modify --out_tsv $processed_data/"$file".blastn.tsv --threads ${thread}
	
	   diamond  blastx \
                --more-sensitive \
                -q $processed_data/"$file".rdrp.virus.match.modify \
                -d  $processed_data/RdRP_only \
                -o $processed_data/"$file".megahit.fa.rdrp \
                -e 1E-3 \
                -k 1 \
                -p ${thread} \
                -f 6 qseqid qlen sseqid stitle pident length evalue sstart send
        cat $processed_data/"$file".megahit.fa.rdrp | cut -f1 | sort -u > $processed_data/"$file"_assemble_nr.rdrp.list
        seqtk subseq $processed_data/"$file".rdrp.virus.match.modify $processed_data/"$file"_assemble_nr.rdrp.list > $processed_data/"$file".megahit.fa.rdrp.fasta
	    mv $processed_data/"$file"_assemble_nr $processed_data/"$file".megahit.fa.nr
	    rm -rf $processed_data/"$file".assemble $processed_data/"$file"_assemble_nr.rdrp.list 
	    rm -rf $processed_data/"$file"_accession_list.txt.nr $processed_data/"$file"_megahit_assemble_nr $processed_data/"$file"_assemble_nr.rdrp.list $processed_data/"$file"_assemble_nr.virus.list

	    mv $processed_data/"$file".megahit.fa.rdrp.fasta  $rdrp/"$file".megahit.fa.megahit.rdrp.virus.match
		mv $processed_data/"$file".megahit.fa  $megahit/"$file".megahit.fa
		mv $processed_data/"$file".megahit.fa.nr  $nr/"$file".megahit.fa.nr
		awk '{print $0}' $rdrp/"$file".megahit.fa.megahit.rdrp.virus.match >> $rdrp/total.rdrp.virus
	  
  done
fi

if [ $only_rdrp_find -eq 0 ];then
	########################part2 finding segmented rna virus###########################
	if [ $library_ID_flag -eq 0 ];
	then
		mkdir -p $rdrp/total.rdrp.megahit.fa_contigs
		for file in `cat ${present_loc}/file_list.txt`;
		do
		if [ $datatype -eq 1 ]; then perl bin/align_and_estimate_abundance.pl --transcripts $rdrp/total.rdrp.virus --seqType fq --single $processed_data/"$file".clean.fq.gz --est_method $quantify_method --aln_method bowtie2  --output_dir $rdrp/"$file"_RSEM-gai-total --thread_count ${thread} --prep_reference; fi
		if [ $datatype -eq 2 ]; then perl bin/align_and_estimate_abundance.pl --transcripts $rdrp/total.rdrp.virus --seqType fq --left $processed_data/"$file".clean_1.fq.gz --right $processed_data/"$file".clean_2.fq.gz --est_method $quantify_method --aln_method bowtie2  --output_dir $rdrp/"$file"_RSEM-gai-total --thread_count ${thread} --prep_reference; fi

		if [ $quantify_method == RSEM ]; then mv $rdrp/"$file"_RSEM-gai-total/RSEM.genes.results $rdrp/"$file"_RSEM-gai-total/"$file"_RSEM.genes.results; fi
		if [ $quantify_method == salmon ]; then mv $rdrp/"$file"_RSEM-gai-total/quant.sf $rdrp/"$file"_RSEM-gai-total/"$file"_RSEM.genes.results; fi

		cp $rdrp/"$file"_RSEM-gai-total/"$file"_RSEM.genes.results $rdrp/total.rdrp.megahit.fa_contigs
		done;
	
		Rscript src/R/TPM-combine.R $rdrp
		mkdir library_ID
		# key in the contigs name you are concerned about
		Rscript src/R/libraryID_search.R $rdrp $contig

		# get the library_ID
		cd library_ID
		library_ID=$(ls)
		cd ..
		rm -rf library_ID
		# screnn repetitive and similar contigs

	fi
	
	library_IDs=($library_ID)

	for library_ID in "${library_IDs[@]}";
	 do
		 mv $nr/${library_ID}.megahit.fa.nr $nr/${library_ID}_megahit_assemble_nr
	     cat $nr/${library_ID}_megahit_assemble_nr | cut -f3 | sort -u | grep -v "^[0-9]" | grep -v -e '^$' > $nr/${library_ID}_accession_list.txt.nr
		 grep -F -f $nr/${library_ID}_accession_list.txt.nr $taxidDB_loc/prot.accession2taxid > $nr/${library_ID}.taxid_table.txt.nr
		 cat  $nr/${library_ID}.taxid_table.txt.nr | cut -f3 -d$'\t' | sort -u > $nr/${library_ID}.taxid_list.txt.nr
		 python3 src/simbiont-js/tools/ncbi/ncbi.taxonomist.py --sep "|" -d < $nr/${library_ID}.taxid_list.txt.nr | sed "s/|/\t/" | sed "s/\t[^|]*|/\t/" > $nr/${library_ID}.lineage_table.txt.nr
		 cat sqlite_table/sqlite_template.nr | sed "s/template/"${library_ID}"/g" > $nr/sqlite_${library_ID}.nr
		 sqlite3 $nr/sqlite_${library_ID}.nr.summary.sql < $nr/sqlite_${library_ID}.nr
		 mv $nr/${library_ID}_megahit_assemble_nr.edited $nr/${library_ID}_megahit_assemble_nr.edited.tsv
		 cp $nr/${library_ID}_megahit_assemble_nr.edited.tsv $megahit/${library_ID}_megahit_assemble_nr.edited.tsv
		 rm -rf $nr/sqlite_${library_ID}.nr
		 rm -rf $nr/sqlite_${library_ID}.nr.summary.sql
		 rm -rf $nr/${library_ID}.taxid_table.txt.nr $/nr/${library_ID}.taxid_list.txt.nr $nr/${library_ID}.lineage_table.txt.nr $nr/${library_ID}.accession_list.txt.nr
		 ########################################################################
		
		sed -i "s/\#/_/g" $nr/${library_ID}_megahit_assemble_nr.edited.tsv
		cp $nr/${library_ID}_megahit_assemble_nr.edited.tsv $megahit/${library_ID}_megahit_assemble_nr.edited.tsv
		Rscript src/R/coefficient-matrix_pre.R ${library_ID} $megahit  $rm_length 
		cat $megahit/RSEM_pre.txt | cut -f2 | sed "s/\"//g" > $megahit/RSEM_pre.txt.list
		sort -n $megahit/RSEM_pre.txt.list | uniq > $megahit/RSEM_pre.txt1.list
		seqtk subseq $megahit/${library_ID}.megahit.fa $megahit/RSEM_pre.txt1.list > $megahit/${library_ID}.megahit.fas-1
	    grep ">" $megahit/${library_ID}.megahit.fa > $megahit/${library_ID}.megahit.list
	    sed -i "s/>//" $megahit/${library_ID}.megahit.list
	    awk -F " " '{print $1}' $nr/${library_ID}_megahit_assemble_nr > $megahit/${library_ID}.megahit_nr.list
		megahit_list_len=$(wc -l < $megahit/${library_ID}.megahit.list)
		megahit_nr_list_len=$(wc -l < $megahit/${library_ID}.megahit_nr.list)
		if [ "$megahit_nr_list_len" -ge "$megahit_list_len" ]
		then
			grep -Fxvf $megahit/${library_ID}.megahit.list $megahit/${library_ID}.megahit_nr.list > output.txt
	    else
			grep -Fxvf $megahit/${library_ID}.megahit_nr.list $megahit/${library_ID}.megahit.list > output.txt
		fi
	    seqtk subseq $megahit/${library_ID}.megahit.fa output.txt > $megahit/${library_ID}.megahit.fas-2
	 	awk -v RS='>' -v ORS='' 'length($2) >= '"$rm_length"' {print ">"$0}' $megahit/${library_ID}.megahit.fas-2 > $megahit/${library_ID}.megahit.fas-3
	 	awk '/^>/{p=!d[$1]}p' $megahit/${library_ID}.megahit.fas-1 $megahit/${library_ID}.megahit.fas-3 > $megahit/${library_ID}.megahit.fas
	 	grep ">" $megahit/${library_ID}.megahit.fas > $megahit/${library_ID}.megahit.list
	    sed -i "s/>//" $megahit/${library_ID}.megahit.list
		rm -rf   $megahit/${library_ID}.megahit_nr.list $megahit/${library_ID}.megahit.fas-1 $megahit/${library_ID}.megahit.fas-2 $megahit/${library_ID}.megahit.fas-3

		cd-hit-est -d 100 -M 0 -T ${thread} -i $megahit/${library_ID}.megahit.fas -o $megahit/${library_ID}.megahit.fa-cd-hit -c 0.8

		sed  "s/>${library_ID}_/>/g" $megahit/${library_ID}.megahit.fa-cd-hit > $megahit/${library_ID}.megahit.fa-cd-hit-gai
		./bin/ORFfinder -in $megahit/${library_ID}.megahit.fa-cd-hit-gai -ml 30 -out $megahit/${library_ID}.megahit.fa-cd-hit.prot.fasta -s 2

		cd-hit -d 100 -M 0 -T ${thread} -i $megahit/${library_ID}.megahit.fa-cd-hit.prot.fasta -o $megahit/${library_ID}.megahit.prot.fasta-cd-hit -c 0.8

		grep -oP '(?<=_)[^:]+(?=:)' $megahit/${library_ID}.megahit.prot.fasta-cd-hit | uniq > ${library_ID}_ID.txt

		sed  "s/^/>${library_ID}_/g" ${library_ID}_ID.txt > $megahit/${library_ID}.list

		rm -rf $megahit/${library_ID}.megahit.prot.fasta-cd-hit ${library_ID}_ID.txt $megahit/${library_ID}.megahit.fa-cd-hit.prot.fasta $megahit/${library_ID}.megahit.fa-cd-hit  $megahit/${library_ID}.megahit.prot.fasta-cd-hit.clstr $megahit/${library_ID}.megahit.fa-cd-hit.clstr

		sed  "s/>//g" $megahit/${library_ID}.list > $megahit/${library_ID}.list.tsv
		seqtk subseq $megahit/${library_ID}.megahit.fa  $megahit/${library_ID}.list.tsv > $megahit/${library_ID}.re.fasta
	    #######################################################################
	        
		Rscript src/R/blastn_nt_novirus.R --evalue 1E-3 --db ${nt_noViruses_loc} --input $megahit/${library_ID}.re.fasta --out_fasta $megahit/${library_ID}.re.fasta.modify --out_tsv $megahit/${library_ID}.re.blastn.tsv --threads ${thread}
	    awk -F " " '{print $1}' $megahit/${library_ID}.re.blastn.tsv | uniq > $megahit/${library_ID}.re.blastn.txt
	    
	    grep ">" $megahit/${library_ID}.re.fasta.modify > $megahit/${library_ID}.re.fasta.modify.list
	    sed -i "s/>//" $megahit/${library_ID}.re.fasta.modify.list
	   
	    grep -vFf $megahit/${library_ID}.re.fasta.modify.list $megahit/${library_ID}.re.blastn.txt > $megahit/${library_ID}.re.fasta.modify.list_del
	    grep -Ff $megahit/${library_ID}.re.fasta.modify.list_del $megahit/${library_ID}_megahit_assemble_nr.edited.tsv > $megahit/${library_ID}_megahit_assemble_nr.edited.tsv_del
	    grep -i -E 'virus|viruses' $megahit/${library_ID}_megahit_assemble_nr.edited.tsv_del > $megahit/${library_ID}_megahit_assemble_nr.edited.tsv_del_re
	    awk -F " " '{print $2}' $megahit/${library_ID}_megahit_assemble_nr.edited.tsv_del_re > $megahit/${library_ID}_megahit_assemble_nr.edited.tsv_del_re.txt
	    seqtk subseq $megahit/${library_ID}.re.fasta $megahit/${library_ID}_megahit_assemble_nr.edited.tsv_del_re.txt > $megahit/${library_ID}.re.fasta_del
	    awk '/^>/{p=!d[$1]}p' $megahit/${library_ID}.re.fasta.modify $megahit/${library_ID}.re.fasta_del > $megahit/${library_ID}.re.fasta-1
	    mv $megahit/${library_ID}.re.fasta-1 $megahit/${library_ID}.re.fasta
	   
	    ##########again########################################################
	    rm $megahit/${library_ID}.re.blastn.tsv $megahit/${library_ID}.re.blastn.txt $megahit/${library_ID}.re.fasta.modify.list $megahit/${library_ID}.re.fasta.modify.list_del $megahit/${library_ID}_megahit_assemble_nr.edited.tsv_del
	    rm $megahit/${library_ID}_megahit_assemble_nr.edited.tsv_del_re.txt $megahit/${library_ID}.re.fasta_del
	   
	    #####RdRP#############################################################
		mv $rdrp/${library_ID}.megahit.fa.megahit.rdrp.virus.match $rdrp/${library_ID}.rdrp.virus.match

		cd-hit-est -M 0 -T ${thread} -i $rdrp/${library_ID}.rdrp.virus.match -o $rdrp/${library_ID}.rdrp.virus.match-cd-hit -c 0.999

		sed  "s/>${library_ID}_/>/g" $rdrp/${library_ID}.rdrp.virus.match-cd-hit > $rdrp/${library_ID}.rdrp.virus.match-cd-hit-gai
		./bin/ORFfinder  -in $rdrp/${library_ID}.rdrp.virus.match-cd-hit-gai -ml 30 -out $rdrp/${library_ID}.rdrp.virus.match-cd-hit.prot.fasta -s 2

		cd-hit -M 0 -T ${thread} -i $rdrp/${library_ID}.rdrp.virus.match-cd-hit.prot.fasta -o $rdrp/${library_ID}.rdrp.virus.match-cd-hit.prot.fasta-cd-hit -c 0.999
		grep -oP '(?<=_)[^:]+(?=:)' $rdrp/${library_ID}.rdrp.virus.match-cd-hit.prot.fasta-cd-hit | uniq > $rdrp/${library_ID}-rdrp_ID.txt
		sed  "s/^/>${library_ID}_/g" $rdrp/${library_ID}-rdrp_ID.txt > $rdrp/${library_ID}.rdrp.list-1

		sed  "s/>//g" $rdrp/${library_ID}.rdrp.list-1 > $rdrp/${library_ID}.rdrp.list
		seqtk subseq $rdrp/${library_ID}.rdrp.virus.match $rdrp/${library_ID}.rdrp.list > $rdrp/${library_ID}.rdrp.fasta
		######################################################################
	    grep ">" $rdrp/${library_ID}.rdrp.fasta > $rdrp/${library_ID}.rdrp.list
	    sed  "s/>//g" $rdrp/${library_ID}.rdrp.list > $rdrp/${library_ID}.rdrp.list.tsv
	    rm -rf $rdrp/${library_ID}.megahit.fa.megahit.rdrp.virus.match-cd-hit $rdrp/${library_ID}.megahit.fa.megahit.rdrp.virus.match-cd-hit.clstr $rdrp/${library_ID}.megahit.fa.megahit.rdrp.virus.match-cd-hit.prot.fasta-cd-hit.clstr $rdrp/${library_ID}.megahit.fa.megahit.rdrp.virus.match-cd-hit.prot.fasta $rdrp/${library_ID}.rdrp.blastn.tsv
		#########################################################################
		mkdir -p $megahit/total.nr.rdrp.megahit.fa_contigs
		for file in "${result_files[@]}";
		do
		if [ $datatype -eq 1 ]; then perl ./bin/align_and_estimate_abundance.pl --transcripts $megahit/${library_ID}.re.fasta --seqType fq --single $processed_data/"$file".clean.fq.gz --est_method $quantify_method --aln_method bowtie2  --output_dir $megahit/"$file"_RSEM-gai-total --thread_count ${thread} --prep_reference; fi
		if [ $datatype -eq 2 ]; then perl ./bin/align_and_estimate_abundance.pl --transcripts $megahit/${library_ID}.re.fasta --seqType fq --left $processed_data/"$file".clean_1.fq.gz --right $processed_data/"$file".clean_2.fq.gz --est_method $quantify_method --aln_method bowtie2  --output_dir $megahit/"$file"_RSEM-gai-total --thread_count ${thread} --prep_reference; fi

		if [ $quantify_method == RSEM ]; then mv $megahit/"$file"_RSEM-gai-total/RSEM.genes.results $megahit/"$file"_RSEM-gai-total/"$file"_RSEM.genes.results; fi
		if [ $quantify_method == salmon ]; then mv $megahit/"$file"_RSEM-gai-total/quant.sf $megahit/"$file"_RSEM-gai-total/"$file"_RSEM.genes.results; fi
		cp $megahit/"$file"_RSEM-gai-total/"$file"_RSEM.genes.results $megahit/total.nr.rdrp.megahit.fa_contigs
		done;

		for file in $megahit/total.nr.rdrp.megahit.fa_contigs/*.results; do mv "$file" "${file%.results}.result.tsv"; done

		#######################################################################
		### coefficient-matrix
		cp  $nr/${library_ID}_megahit_assemble_nr.edited.tsv $megahit
		sed -i "s/#/_/" $megahit/${library_ID}_megahit_assemble_nr.edited.tsv
		cp $rdrp/${library_ID}.rdrp.list.tsv  $megahit
		Rscript src/R/coefficient-matrix.R ${library_ID} $megahit  
		#######################################################################
		blastn -query $megahit/"${library_ID}".re.fasta -db $nt_loc -out $megahit/"${library_ID}"_megahit_assemble_re_nt.tsv -evalue 1E-3 -outfmt "6 qseqid qlen sacc salltitles pident length evalue sstart send" -max_target_seqs 5 -num_threads ${thread}
		######################################################################
		diamond  blastx -q ${present_loc}/rdrp/${library_ID}.rdrp.fasta -d Seg_DB/RdRP/RdRP_only -o $megahit/${library_ID}.megahit.fa.rdrp.tsv --more-sensitive -e 1E-3 -k 5 -p ${thread} -f 6 qseqid qlen sseqid stitle pident length evalue sstart send
		cp $nr/${library_ID}_megahit_assemble_nr $megahit/${library_ID}_megahit_assemble_nr.tsv
		sed -i "s/#/_/" $megahit/"${library_ID}"_megahit_assemble_re_nt.tsv
		cd $megahit
		awk '/^>/ {printf("%s\t", substr($0,2)); getline; print length($0)}' "${library_ID}".re.fasta  | awk '{match($0, /len.*[0-9]*/); str=substr($0, RSTART, RLENGTH); match(str, /[0-9]+/); a=substr(str, RSTART, RLENGTH);if (a == $2) print $0"\tfalse"; else print $0"\ttrue"}' > re.fasta_length.txt
		Rscript src/R/Cor_contigs_extract.R  ${cor} ${library_ID}  ${min_TPM} ${min_rdrp_multi} ${min_nordrp_multi}	
		cd ${present_loc}

		cp $megahit/${library_ID}.network_group_fr.pdf $network
		cp $megahit/${library_ID}.final.confidence_table.xlsx $network
		cp $megahit/${library_ID}.pre.confidence_table.xlsx $network

		rm -rf $megahit/*RSEM-gai-total
		rm -rf $megahit/total.nr.rdrp.megahit.fa_contigs
		rm -rf $megahit/*.fa
		rm -rf $nr
		rm -rf $rdrp/*rdrp.virus.match
		rm -rf $rdrp/*_RSEM-gai-total
		rm -rf $megahit/*.re.fasta.salmon_quasi.idx
		rm -rf $megahit/cor.p.csv
		rm -rf $megahit/cor.r.csv
		rm -rf $rdrp/2.out
		rm -rf $rdrp/3.out
		mkdir -p $out_loc/${library_ID}
		mv $megahit  $network $rdrp $out_loc/${library_ID}
	done;
	
fi





