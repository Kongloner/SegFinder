#!/bin/bash

# Function to handle errors
 error_exit() {
    echo "$1" 1>&2
    exit 1
 }

# Function to run a command and handle errors
 run_command() {
    echo "Running command: $@"
    if ! "$@" 2>&1; then
        echo "Error running command: $@" 1>&2
        error_exit "Failed to run command: $@"
    fi
 }


# Usage function to display help message
usage(){
cat <<'EOF'
Usage
 [--stage]... specify the stage of the pipeline to run: preprocess, rdrp_find, or segment_find; default preprocess
 [-o]... the directory to output the results; default ./
 [--indata]... the location of the raw data
 [--incontig]... the contig you want to search
 [--thread]... default 10
 [--cor]... correlation coefficient; default 0.8
 [--nt_noViruses]... the location of nt_noViruses database, used to remove viral sequence contamination, optional
 [--nt]... the location of nt database
 [--nr]... the location of nr database
 [--method]... the method to quantify the transcript abundances,salmon or RSEM,default salmon
 [--datatype]... the type of input data single(input 1) or double(input 2)
 [--taxidDB]... the location of prot.accession2taxid database
 [--rm_length]... the contigs whose length less than this value will be removed; default 600
 [--min_rdrp_multi]... minimum length of rdrp and their re-assembled contigs to be retained; default 50
 [--min_nordrp_multi]... minimum length of non-rdrp and their re-assembled contigs to be retained; default 20
 [--library_ID]... the library you want to search, can input multiple IDs separated by spaces
 [--assemble]... tthe tool to assemble the raw reads, megahit or spades; default spades
 [--min_TPM]... if there exist the contig whose TPM is less than this value, the cluster it is in will be removed; default 200
 [--help]... display this help message
 [--version]... display version information
EOF
}

# Default parameters
datatype=2
thread=10
cor=0.8
rm_length=600
min_rdrp_multi=50
min_nordrp_multi=20
min_TPM=200
quantify_method="salmon"
assemble_method="spades"
# stage="preprocess"
nt_loc="Seg_DB/NT/nt"
nr_loc="Seg_DB/NR/nr"
taxidDB_loc="Seg_DB/accession2taxid/prot.accession2taxid"


# Parse command-line arguments
parameters=$(getopt -o o: --long indata:,incontig:,thread:,cor:,datatype:,nt:,nr:,method:,stage:,min_multi:,min_TPM:,assemble:,library_ID:,rm_length:,nt_noViruses:,taxidDB:,help,version -n "$0" -- "$@")
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
        --stage) stage=$2; shift 2;;
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
	# Validate stage parameter
	valid_stages=("preprocess" "rdrp_find" "segment_find")
	if [[ -z $stage || ! " ${valid_stages[@]} " =~ " ${stage} " ]]; then
    	echo "Invalid or missing stage parameter. Please use --stage with one of the following values: preprocess, rdrp_find, segment_find."
    	exit 1
	fi

    if [[ -z $rawData_loc && $stage == "preprocess" ]]; then
        echo "please input the location of the raw data!!! --indata"
        exit 1
    fi

 #   if [[ -z $datatype ]]; then
 #       echo "please input the type of input data!!! --datatype"
 #       exit 1
 #   fi

 #   if [[ $datatype -ne 1 && $datatype -ne 2 ]]; then
 #       echo 'please re_input the type of input data, 1 or 2, for 1 means single type, 2 means double'
 #       exit 1
 #   fi

    if [[ -z $library_ID && $stage == "segment_find" ]]; then
        echo "please input the library_ID!!! --library_ID"
        exit 1
    fi

 #   if [[ -z $nt_loc && ($stage == "rdrp_find" || $stage == "segment_find") ]]; then
 #       echo "please input the location of nt!!! --nt"
    #    exit 1
 #   fi

#    if [[ -z $nr_loc && $stage == "rdrp_find" ]]; then
#        echo "please input the location of nr!!! --nr"
#        exit 1
#    fi

#    if [[ -z $nt_noViruses_loc && ($stage == "rdrp_find" || $stage == "segment_find") ]]; then
#        echo "please input the location of nt_noViruses database!!! --nt_noViruses"
#        exit 1
#    fi

#    if [[ -z $taxidDB_loc && ($stage == "rdrp_find" || $stage == "segment_find") ]]; then
#        echo "please input the location of prot.accession2taxid database!!! --taxidDB"
#        exit 1
#    fi
}

# Call the validate_params function
validate_params

# Set output directories
if [ -z "$out_loc" ]; then
    out_loc=`pwd`
fi

megahit="$out_loc/megahit"
nr="$out_loc/nr"
rdrp="$out_loc/rdrp"
network="$out_loc/network"
processed_data="$out_loc/processed_data"

present_loc=`pwd`
chmod +x ${present_loc}/bin/align_and_estimate_abundance.pl
chmod +x ${present_loc}/bin/ORFfinder

#### data preprocessing ####
if [ $stage == "preprocess" ]; then
	result_files=($(ls $rawData_loc/*.fq.gz | sed -E 's/_1.fq.gz|_2.fq.gz|.fq.gz//g' | xargs -n 1 basename | sort -u))
    mkdir -p "$processed_data"
	for file in "${result_files[@]}";
	do
### qc ###
	    echo "Starting quality control and assembly process..."
		echo "----Starting quality control for $file----"
		if [ $datatype -eq 1 ]; then 
			 run_command fastp -i ${rawData_loc}/${file}.fq.gz -o ${processed_data}/${file}-fp.fq.gz -w ${thread} 
			 run_command ribodetector_cpu -l 100 -i ${processed_data}/${file}-fp.fq.gz -t ${thread} -e norrna  -o ${processed_data}/${file}.clean.fq.gz 
			 rm ${processed_data}/${file}-fp.fq.gz
			 rm $(pwd)/fastp.html $(pwd)/fastp.json
		fi
       if [ $datatype -eq 2 ]; then 
			 run_command fastp -i ${rawData_loc}/${file}_1.fq.gz -I ${rawData_loc}/${file}_2.fq.gz -o ${processed_data}/${file}_1-fp.fq.gz -O  ${processed_data}/${file}_2-fp.fq.gz -w ${thread} 
			 run_command ribodetector_cpu -l 100 -i ${processed_data}/${file}_1-fp.fq.gz ${processed_data}/${file}_2-fp.fq.gz  -t ${thread} -e norrna  -o ${processed_data}/${file}.clean_{1,2}.fq.gz 
			 rm ${processed_data}/${file}_1-fp.fq.gz ${processed_data}/${file}_2-fp.fq.gz
			 rm $(pwd)/fastp.html $(pwd)/fastp.json
		fi
		echo "----Finished quality control for $file----"
### assemble ###		
		cd ${processed_data}		
		echo "----Starting assembly of the raw reads for $file----"
		if [ $assemble_method == spades ]; then
			if [ $datatype -eq 1 ]; then 
				  run_command spades.py --meta --phred-offset 33 -s ${file}.clean.fq.gz -t ${thread} -o ${file}.assemble 
			fi
			if [ $datatype -eq 2 ]; then 
				  run_command spades.py --meta --phred-offset 33 -1 ${file}.clean_1.fq.gz -2 ${file}.clean_2.fq.gz -t ${thread} -o ${file}.assemble 
			fi
			cat ${file}.assemble/contigs.fasta | sed 's/ /_/g' | sed 's/=/_/g'| sed "s/>/>${file}_/g" > ${file}.assemble/${file}.fa_modify
			fi	
		if [ $assemble_method == megahit ] || [ ! -s ${file}.assemble/contigs.fasta ]; then rm  -rf ${file}.assemble;
			if [ $datatype -eq 2 ]; then 
				  run_command megahit -1 ${file}.clean_1.fq.gz  -2 ${file}.clean_2.fq.gz  --num-cpu-threads ${thread}  --memory 0.9  -o ${file}.assemble 
			fi
			if [ $datatype -eq 1 ]; then 
				  run_command megahit -r ${file}.clean.fq.gz --num-cpu-threads ${thread} --memory 0.9 -o ${file}.assemble 
			fi
			cat ${file}.assemble/final.contigs.fa | sed 's/ /_/g' | sed 's/=/_/g'| sed "s/>/>${file}_/g" > ${file}.assemble/${file}.fa_modify 
		fi
		cp ${file}.assemble/${file}.fa_modify ${file}.megahit.fa
		cd ${present_loc}
		echo "----Finished assembly of the raw reads for $file----"
  done
  echo "Preprocessing done. To run the next stage, use --stage rdrp_find"
fi




### Finding rna virus RdRP ###
if [ $stage == "rdrp_find" ]; then
########################part3 finding rdrp###########################
	result_files=($(ls $processed_data/*.megahit.fa | sed -E 's/.megahit.fa//g' | xargs -n 1 basename | sort -u))
	for file in "${result_files[@]}";
	do
        echo "----Starting RNA virus RdRP finding for $file----"
		run_command cd ${processed_data}
	    run_command diamond blastx \
			   -q ${file}.megahit.fa \
			   -d ${nr_loc} \
			   -o ${file}_assemble_nr \
			   -e 1E-4 \
			   -k 1 \
			   -p ${thread} \
			   -f 6 qseqid qlen sseqid stitle pident length evalue sstart send  

       cp -rf  ${present_loc}/data/sqlite_table ${processed_data} 
       cp ${file}_assemble_nr ${file}_megahit_assemble_nr
       sed -i "s/#/_/" ${file}_megahit_assemble_nr
       cat ${file}_megahit_assemble_nr | cut -f3 | sort -u | grep -v "^[0-9]" | grep -v -e '^$' > ${file}_accession_list.txt.nr
       grep -F -f ${file}_accession_list.txt.nr $taxidDB_loc > ${file}.taxid_table.txt.nr
       cat  ${file}.taxid_table.txt.nr | cut -f3 -d$'\t' | sort -u > ${file}.taxid_list.txt.nr
       python3 ${present_loc}/src/simbiont-js/tools/ncbi/ncbi.taxonomist.py --sep "|" -d < ${file}.taxid_list.txt.nr | sed "s/|/\t/" | sed "s/\t[^|]*|/\t/" > ${file}.lineage_table.txt.nr
       cat sqlite_table/sqlite_template.nr | sed "s/template/"${file}"/g" > sqlite_${file}.nr
       sqlite3 sqlite_${file}.nr.summary.sql < sqlite_${file}.nr
       mv ${file}_megahit_assemble_nr.edited ${file}_megahit_assemble_nr.edited.tsv
       rm -rf sqlite_table
       rm -rf ${file}.taxid_table.txt.nr ${file}.taxid_list.txt.nr ${file}.lineage_table.txt.nr ${file}.accession_list.txt.nr
       rm -rf sqlite_${file}.nr
       rm -rf sqlite_${file}.nr.summary.sql

	   grep -i "virus" ${file}_megahit_assemble_nr.edited.tsv > ${file}_assemble_nr.virus
	   cat ${file}_assemble_nr.virus | cut -f2 | sort -u > ${file}_assemble_nr.virus.list
	   seqtk subseq ${file}.megahit.fa ${file}_assemble_nr.virus.list > ${file}_assemble_nr.virus.match
	   run_command diamond makedb --in ${present_loc}/data/RdRP_only.fasta --db RdRP_only -p ${thread}
	   diamond  blastx \
		     --more-sensitive \
			 -q ${file}_assemble_nr.virus.match \
			 -d RdRP_only \
			 -o ${file}_assemble_nr.rdrp \
			 -e 1E-3 \
			 -k 1 \
             -p ${thread} \
             -f 6 qseqid qlen sseqid stitle pident length evalue qstart qend
	   cat ${file}_assemble_nr.rdrp | cut -f1 | sort -u > ${file}_assemble_nr.rdrp.list
	   seqtk subseq ${file}_assemble_nr.virus.match ${file}_assemble_nr.rdrp.list > ${file}.rdrp.virus.match

	cd ${present_loc}

	# If nt_noViruses_loc is provided, run the R script and generate the modify file
	if [[ -n "$nt_noViruses_loc" ]]; then
		run_command Rscript ${present_loc}/src/R/blastn_nt_novirus.R --db ${nt_noViruses_loc} --evalue 1E-10 --input ${processed_data}/${file}.rdrp.virus.match --out_fasta ${processed_data}/${file}.rdrp.virus.match.modify --out_tsv ${processed_data}/${file}.blastn.tsv --threads ${thread}
		input_fasta="${processed_data}/${file}.rdrp.virus.match.modify"  # Use modified fasta file
	else
		input_fasta="${processed_data}/${file}.rdrp.virus.match"  # Use original file
	fi

	cd ${processed_data}

	# Use the selected input_fasta for diamond analysis
	diamond  blastx \
		--more-sensitive \
		-q ${input_fasta} \
		-d  RdRP_only \
		-o ${file}.megahit.fa.rdrp \
		-e 1E-3 \
		-k 1 \
		-p ${thread} \
		-f 6 qseqid qlen sseqid stitle pident length evalue sstart send

	cat ${file}.megahit.fa.rdrp | cut -f1 | sort -u > ${file}_assemble_nr.rdrp.list

	# If nt_noViruses_loc was provided, the modify file was used
	if [[ -n "$nt_noViruses_loc" ]]; then
		seqtk subseq ${file}.rdrp.virus.match.modify ${file}_assemble_nr.rdrp.list > ${file}.megahit.fa.rdrp.fasta
	else
		seqtk subseq ${file}.rdrp.virus.match ${file}_assemble_nr.rdrp.list > ${file}.megahit.fa.rdrp.fasta
	fi

	mv ${file}_assemble_nr ${file}.megahit.fa.nr
	rm -rf ${file}.assemble ${file}_assemble_nr.rdrp.list 
	rm -rf ${file}_accession_list.txt.nr ${file}_megahit_assemble_nr ${file}_assemble_nr.rdrp.list ${file}_assemble_nr.virus.list
	cd ${present_loc}
	echo "----Finished RNA virus RdRP finding for $file----"

	done;
	echo "RdRP finding done. To run the next stage, use --stage segment_find"
fi


if [ $stage == "segment_find" ]; then
	########################part3 finding segmented rna virus###########################

#	if [ $library_ID_flag -eq 0 ];
#	then
#		mkdir -p ${rdrp}/total.rdrp.megahit.fa_contigs
#		for file in "${result_files[@]}";
#		do
#		if [ $datatype -eq 1 ]; then perl bin/align_and_estimate_abundance.pl --transcripts ${rdrp}/total.rdrp.virus --seqType fq --single ${processed_data}/${file}.clean.fq.gz --est_method $quantify_method --aln_method bowtie2  --output_dir ${rdrp}/${file}_RSEM-gai-total --thread_count ${thread} --prep_reference; fi
#		if [ $datatype -eq 2 ]; then perl bin/align_and_estimate_abundance.pl --transcripts ${rdrp}/total.rdrp.virus --seqType fq --left ${processed_data}/${file}.clean_1.fq.gz --right ${processed_data}/${file}.clean_2.fq.gz --est_method $quantify_method --aln_method bowtie2  --output_dir ${rdrp}/${file}_RSEM-gai-total --thread_count ${thread} --prep_reference; fi
#
#		if [ $quantify_method == RSEM ]; then mv ${rdrp}/${file}_RSEM-gai-total/RSEM.genes.results ${rdrp}/${file}_RSEM-gai-total/${file}_RSEM.genes.results; fi
#		if [ $quantify_method == salmon ]; then mv ${rdrp}/${file}_RSEM-gai-total/quant.sf ${rdrp}/${file}_RSEM-gai-total/${file}_RSEM.genes.results; fi
#
#		cp ${rdrp}/${file}_RSEM-gai-total/${file}_RSEM.genes.results ${rdrp}/total.rdrp.megahit.fa_contigs
#		done;
#	
#		Rscript src/R/TPM-combine.R ${rdrp}
#		mkdir library_ID
#		# key in the contigs name you are concerned about
#		Rscript src/R/libraryID_search.R ${rdrp} $contig
#
#		# get the library_ID
#		cd library_ID
#		library_ID=$(ls)
#		cd ..
#		rm -rf library_ID
#		# screnn repetitive and similar contigs
#	fi
	result_files=($(ls $processed_data/*.megahit.fa | sed -E 's/.megahit.fa//g' | xargs -n 1 basename | sort -u))
	library_IDs=($library_ID)

	for library_ID in "${library_IDs[@]}";
	 do
	    echo "----Starting Segmented RNA virus finding for library: $library_ID----"
	 	mkdir -p "$megahit" "$nr" "$rdrp" "$network" 

		run_command cp ${processed_data}/${library_ID}.megahit.fa  ${megahit}/${library_ID}.megahit.fa
		run_command cp ${processed_data}/${library_ID}.megahit.fa.rdrp.fasta  ${rdrp}/${library_ID}.megahit.fa.megahit.rdrp.virus.match
	 	run_command cp -rf  ${present_loc}/data/sqlite_table $nr
		run_command cp ${processed_data}/${library_ID}.megahit.fa.nr $nr/${library_ID}_megahit_assemble_nr

		cd ${nr}
	    cat ${library_ID}_megahit_assemble_nr | cut -f3 | sort -u | grep -v "^[0-9]" | grep -v -e '^$' > ${library_ID}_accession_list.txt.nr
		grep -F -f ${library_ID}_accession_list.txt.nr $taxidDB_loc > ${library_ID}.taxid_table.txt.nr
		cat  ${library_ID}.taxid_table.txt.nr | cut -f3 -d$'\t' | sort -u > ${library_ID}.taxid_list.txt.nr
		python3 ${present_loc}/src/simbiont-js/tools/ncbi/ncbi.taxonomist.py --sep "|" -d < ${library_ID}.taxid_list.txt.nr | sed "s/|/\t/" | sed "s/\t[^|]*|/\t/" > ${library_ID}.lineage_table.txt.nr
		cat sqlite_table/sqlite_template.nr | sed "s/template/"${library_ID}"/g" > sqlite_${library_ID}.nr
		sqlite3 sqlite_${library_ID}.nr.summary.sql < sqlite_${library_ID}.nr
		mv ${library_ID}_megahit_assemble_nr.edited ${library_ID}_megahit_assemble_nr.edited.tsv
		cp ${library_ID}_megahit_assemble_nr.edited.tsv $megahit/${library_ID}_megahit_assemble_nr.edited.tsv
		rm -rf sqlite_${library_ID}.nr
		rm -rf sqlite_${library_ID}.nr.summary.sql
		rm -rf ${library_ID}.taxid_table.txt.nr $/nr/${library_ID}.taxid_list.txt.nr ${library_ID}.lineage_table.txt.nr ${library_ID}.accession_list.txt.nr
		
		sed -i "s/\#/_/g" ${library_ID}_megahit_assemble_nr.edited.tsv
		cp ${library_ID}_megahit_assemble_nr.edited.tsv $megahit/${library_ID}_megahit_assemble_nr.edited.tsv
		run_command Rscript ${present_loc}/src/R/coefficient-matrix_pre.R ${library_ID} $megahit $rm_length 

##########################################################
		cd ${megahit}
		cat RSEM_pre.txt | cut -f2 | sed "s/\"//g" > RSEM_pre.txt.list
		sort -n RSEM_pre.txt.list | uniq > RSEM_pre.txt1.list
		seqtk subseq ${processed_data}/${library_ID}.megahit.fa RSEM_pre.txt1.list > ${library_ID}.megahit.fas-1
	    grep ">" ${processed_data}/${library_ID}.megahit.fa > ${library_ID}.megahit.list
	    sed -i "s/>//" ${library_ID}.megahit.list
	    awk -F " " '{print $1}' $nr/${library_ID}_megahit_assemble_nr > ${library_ID}.megahit_nr.list
		megahit_list_len=$(wc -l < ${library_ID}.megahit.list)
		megahit_nr_list_len=$(wc -l < ${library_ID}.megahit_nr.list)
		if [ "$megahit_nr_list_len" -ge "$megahit_list_len" ]
		then
			grep -Fxvf ${library_ID}.megahit.list ${library_ID}.megahit_nr.list > output.txt
	    else
			grep -Fxvf ${library_ID}.megahit_nr.list ${library_ID}.megahit.list > output.txt
		fi
	    seqtk subseq ${library_ID}.megahit.fa output.txt > ${library_ID}.megahit.fas-2
	 	awk -v RS='>' -v ORS='' 'length($2) >= '"$rm_length"' {print ">"$0}' ${library_ID}.megahit.fas-2 > ${library_ID}.megahit.fas-3
	 	awk '/^>/{p=!d[$1]}p' ${library_ID}.megahit.fas-1 ${library_ID}.megahit.fas-3 > ${library_ID}.megahit.fas
	 	grep ">" ${library_ID}.megahit.fas > ${library_ID}.megahit.list
	    sed -i "s/>//" ${library_ID}.megahit.list
		rm -rf   ${library_ID}.megahit_nr.list ${library_ID}.megahit.fas-1 ${library_ID}.megahit.fas-2 ${library_ID}.megahit.fas-3

		run_command cd-hit-est -d 100 -M 0 -T ${thread} -i ${library_ID}.megahit.fas -o ${library_ID}.megahit.fa-cd-hit -c 0.8

		sed  "s/>${library_ID}_/>/g" ${library_ID}.megahit.fa-cd-hit > ${library_ID}.megahit.fa-cd-hit-gai
		${present_loc}/bin/ORFfinder -in ${library_ID}.megahit.fa-cd-hit-gai -ml 30 -out ${library_ID}.megahit.fa-cd-hit.prot.fasta -s 2

		run_command cd-hit -d 100 -M 0 -T ${thread} -i ${library_ID}.megahit.fa-cd-hit.prot.fasta -o ${library_ID}.megahit.prot.fasta-cd-hit -c 0.8

		grep -oP '(?<=_)[^:]+(?=:)' ${library_ID}.megahit.prot.fasta-cd-hit | uniq > ${library_ID}_ID.txt

		sed  "s/^/>${library_ID}_/g" ${library_ID}_ID.txt > ${library_ID}.list

		rm -rf ${library_ID}.megahit.prot.fasta-cd-hit ${library_ID}_ID.txt ${library_ID}.megahit.fa-cd-hit.prot.fasta ${library_ID}.megahit.fa-cd-hit  ${library_ID}.megahit.prot.fasta-cd-hit.clstr ${library_ID}.megahit.fa-cd-hit.clstr

	sed  "s/>//g" ${library_ID}.list > ${library_ID}.list.tsv
	seqtk subseq ${library_ID}.megahit.fa ${library_ID}.list.tsv > ${library_ID}.re.fasta

	cd ${present_loc}

	# If nt_noViruses_loc is provided, run the R script to generate the modify file
	if [[ -n "$nt_noViruses_loc" ]]; then
		run_command Rscript ${present_loc}/src/R/blastn_nt_novirus.R --evalue 1E-3 --db ${nt_noViruses_loc} --input ${megahit}/${library_ID}.re.fasta --out_fasta ${megahit}/${library_ID}.re.fasta.modify --out_tsv ${megahit}/${library_ID}.re.blastn.tsv --threads ${thread}
		input_fasta="${megahit}/${library_ID}.re.fasta.modify"
		input_blastn="${megahit}/${library_ID}.re.blastn.tsv"
	else
		input_fasta="${megahit}/${library_ID}.re.fasta"
		input_blastn=""  # No blastn results if nt_noViruses_loc is not provided
	fi

	cd ${megahit}

	# Proceed with blastn processing only if nt_noViruses_loc is provided
	if [[ -n "$input_blastn" ]]; then
		awk -F " " '{print $1}' ${input_blastn} | uniq > ${library_ID}.re.blastn.txt

		grep ">" ${input_fasta} > ${library_ID}.re.fasta.modify.list
		sed -i "s/>//" ${library_ID}.re.fasta.modify.list

		grep -vFf ${library_ID}.re.fasta.modify.list ${library_ID}.re.blastn.txt > ${library_ID}.re.fasta.modify.list_del
		grep -Ff ${library_ID}.re.fasta.modify.list_del ${library_ID}_megahit_assemble_nr.edited.tsv > ${library_ID}_megahit_assemble_nr.edited.tsv_del
		grep -i -E 'virus|viruses' ${library_ID}_megahit_assemble_nr.edited.tsv_del > ${library_ID}_megahit_assemble_nr.edited.tsv_del_re
		awk -F " " '{print $2}' ${library_ID}_megahit_assemble_nr.edited.tsv_del_re > ${library_ID}_megahit_assemble_nr.edited.tsv_del_re.txt
		seqtk subseq ${library_ID}.re.fasta ${library_ID}_megahit_assemble_nr.edited.tsv_del_re.txt > ${library_ID}.re.fasta_del
		awk '/^>/{p=!d[$1]}p' ${input_fasta} ${library_ID}.re.fasta_del > ${library_ID}.re.fasta-1
		#mv ${library_ID}.re.fasta-1 ${library_ID}.re.fasta
                seqkit rmdup -n ${library_ID}.re.fasta-1 > ${library_ID}.re.fasta
		# Cleanup temporary files
		rm ${input_blastn} ${library_ID}.re.blastn.txt ${library_ID}.re.fasta.modify.list ${library_ID}.re.fasta.modify.list_del ${library_ID}_megahit_assemble_nr.edited.tsv_del
		rm ${library_ID}_megahit_assemble_nr.edited.tsv_del_re.txt ${library_ID}.re.fasta_del
	fi

	########## RdRP #############################################################

	cd ${rdrp}
	mv ${library_ID}.megahit.fa.megahit.rdrp.virus.match ${library_ID}.rdrp.virus.match

	run_command cd-hit-est -M 0 -T ${thread} -i ${library_ID}.rdrp.virus.match -o ${library_ID}.rdrp.virus.match-cd-hit -c 0.999

	sed "s/>${library_ID}_/>/g" ${library_ID}.rdrp.virus.match-cd-hit > ${library_ID}.rdrp.virus.match-cd-hit-gai
	${present_loc}/bin/ORFfinder -in ${library_ID}.rdrp.virus.match-cd-hit-gai -ml 30 -out ${library_ID}.rdrp.virus.match-cd-hit.prot.fasta -s 2

	run_command cd-hit -M 0 -T ${thread} -i ${library_ID}.rdrp.virus.match-cd-hit.prot.fasta -o ${library_ID}.rdrp.virus.match-cd-hit.prot.fasta-cd-hit -c 0.999

	grep -oP '(?<=_)[^:]+(?=:)' ${library_ID}.rdrp.virus.match-cd-hit.prot.fasta-cd-hit | uniq > ${library_ID}-rdrp_ID.txt
	sed "s/^/>${library_ID}_/g" ${library_ID}-rdrp_ID.txt > ${library_ID}.rdrp.list-1

	sed "s/>//g" ${library_ID}.rdrp.list-1 > ${library_ID}.rdrp.list
	seqtk subseq ${library_ID}.rdrp.virus.match ${library_ID}.rdrp.list > ${library_ID}.rdrp.fasta

	grep ">" ${library_ID}.rdrp.fasta > ${library_ID}.rdrp.list
	sed "s/>//g" ${library_ID}.rdrp.list > ${library_ID}.rdrp.list.tsv

	# Clean up temporary files
	rm -rf ${library_ID}.megahit.fa.megahit.rdrp.virus.match-cd-hit ${library_ID}.megahit.fa.megahit.rdrp.virus.match-cd-hit.clstr ${library_ID}.megahit.fa.megahit.rdrp.virus.match-cd-hit.prot.fasta-cd-hit.clstr ${library_ID}.megahit.fa.megahit.rdrp.virus.match-cd-hit.prot.fasta ${library_ID}.rdrp.blastn.tsv

	mkdir -p $megahit/total.nr.rdrp.megahit.fa_contigs

	for file in "${result_files[@]}"; do
		if [ $datatype -eq 1 ]; then
			run_command perl ${present_loc}/bin/align_and_estimate_abundance.pl --transcripts $megahit/${library_ID}.re.fasta --seqType fq --single $processed_data/${file}.clean.fq.gz --est_method $quantify_method --aln_method bowtie2 --output_dir $megahit/${file}_RSEM-gai-total --thread_count ${thread} --prep_reference
		fi

		if [ $datatype -eq 2 ]; then
			run_command perl ${present_loc}/bin/align_and_estimate_abundance.pl --transcripts $megahit/${library_ID}.re.fasta --seqType fq --left $processed_data/${file}.clean_1.fq.gz --right $processed_data/${file}.clean_2.fq.gz --est_method $quantify_method --aln_method bowtie2 --output_dir $megahit/${file}_RSEM-gai-total --thread_count ${thread} --prep_reference
		fi

		if [ $quantify_method == RSEM ]; then
			mv $megahit/${file}_RSEM-gai-total/RSEM.genes.results $megahit/${file}_RSEM-gai-total/${file}_RSEM.genes.results
		fi

		if [ $quantify_method == salmon ]; then
			mv $megahit/${file}_RSEM-gai-total/quant.sf $megahit/${file}_RSEM-gai-total/${file}_RSEM.genes.results
		fi

		cp $megahit/${file}_RSEM-gai-total/${file}_RSEM.genes.results $megahit/total.nr.rdrp.megahit.fa_contigs
	done

	for file in $megahit/total.nr.rdrp.megahit.fa_contigs/*.results; do
		mv ${file} "${file%.results}.result.tsv"
	done

	### Coefficient-matrix
	cp $nr/${library_ID}_megahit_assemble_nr.edited.tsv $megahit
	sed -i "s/#/_/" $megahit/${library_ID}_megahit_assemble_nr.edited.tsv
	cp $rdrp/${library_ID}.rdrp.list.tsv $megahit
	run_command Rscript ${present_loc}/src/R/coefficient-matrix.R ${library_ID} $megahit

	blastn -query $megahit/"${library_ID}".re.fasta -db $nt_loc -out $megahit/"${library_ID}"_megahit_assemble_re_nt.tsv -evalue 1E-3 -outfmt "6 qseqid qlen sacc salltitles pident length evalue sstart send" -max_target_seqs 5 -num_threads ${thread}

	run_command diamond makedb --in ${present_loc}/data/RdRP_only.fasta --db $megahit/RdRP_only -p ${thread}
	diamond blastx -q $rdrp/${library_ID}.rdrp.fasta -d $megahit/RdRP_only -o $megahit/${library_ID}.megahit.fa.rdrp.tsv --more-sensitive -e 1E-3 -k 5 -p ${thread} -f 6 qseqid qlen sseqid stitle pident length evalue sstart send

	cp $nr/${library_ID}_megahit_assemble_nr $megahit/${library_ID}_megahit_assemble_nr.tsv
	sed -i "s/#/_/" $megahit/"${library_ID}"_megahit_assemble_re_nt.tsv

	awk '/^>/ {printf("%s\t", substr($0,2)); getline; print length($0)}' $megahit/"${library_ID}".re.fasta | awk '{match($0, /len.*[0-9]*/); str=substr($0, RSTART, RLENGTH); match(str, /[0-9]+/); a=substr(str, RSTART, RLENGTH);if (a == $2) print $0"\tfalse"; else print $0"\ttrue"}' > $megahit/re.fasta_length.txt

	cd $megahit
	run_command Rscript ${present_loc}/src/R/Cor_contigs_extract.R ${cor} ${library_ID} ${min_TPM} ${min_rdrp_multi} ${min_nordrp_multi}

	cd ${present_loc}
	cp $megahit/${library_ID}.network_group_fr.pdf $network
	cp $megahit/${library_ID}.final.confidence_table.xlsx $network
	cp $megahit/${library_ID}.pre.confidence_table.xlsx $network

	# Clean up
	rm -rf $megahit/*RSEM-gai-total
	rm -rf $megahit/total.nr.rdrp.megahit.fa_contigs
	rm -rf $megahit/*.fa
	rm -rf $nr
	rm -rf $rdrp/*rdrp.virus.match
	rm -rf $rdrp/*_RSEM-gai-total
	rm -rf $megahit/*.re.fasta.salmon_quasi.idx
	rm -rf $megahit/cor.p.csv
	rm -rf $megahit/cor.r.csv
	rm -rf $megahit/RdRP_only.dmnd
	rm -rf $rdrp/2.out
	rm -rf $rdrp/3.out
	cd ${present_loc}
	mkdir -p $out_loc/${library_ID}
	mv $megahit $network $rdrp $out_loc/${library_ID}
	echo "----Finished Segmented RNA virus finding for library: $library_ID----"

	done;	
fi





