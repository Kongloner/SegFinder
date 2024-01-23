usage(){
cat <<'EOF'
Usage
 [-o]... the directory to output the results; default ./
 [--indata]... the location of the raw data
 [--incontig]... the contig you want to search
 [--thread]... default 10
 [--cor]... correlation coefficient;default 0.8
 [--nt_noViruses]... the location of nt_noViruses database
 [--nt]... the location of nt database
 [--nr]... the location of nr database
 [--method]... the method to quantify the transcript abundances,salmon or RSEM,default salmon
 [--datatype]... the type of input data single(input 1) or double(input 2)
 [--taxidDB]... the location of prot.accession2taxid database
 [--rm_length]... the contigs whose length less than this value will be removed,default 600
 [--min_rdrp_multi]... if the length of the rdrp and their re_assembled cotigs are all less than this value, the clusters they are in will be removed,default 100
 [--min_nordrp_multi]... if the length of the non_rdrp and their re_assembled cotigs are all less than this value, the clusters they are in will be removed,default 20
 [--library_ID]... the library you want to search,default the library in which the abundance of the contig you input is max 
 [--preprocess]... whether to preprocess the raw fq data,you can input 'true' or 'false',default false
 [--assemble]... the tool you choose to assemble the raw reads,megahit or spades,default spades
 [--only_rdrp_find]...1 or 0, 1 means only find rna virus RdRPs without any other analysis, default 0
 [--min_TPM]...if there exist the contig whose TPM is less than this value, the cluster it is in will be removed,default 200
 [--help]...
 [--version]...
EOF
}

parameters=`getopt  -o o: --long indata:,incontig:,thread:,cor:,datatype:,nt:,nr:,method:,only_rdrp_find:,min_multi:,min_TPM:,assemble:,preprocess:,library_ID:,rm_length:,nt_noViruses:,taxidDB:,help,version -n "$0" -- "$@"`
[ $? -ne 0 ] && { echo "Try '$0 --help' for more information."; exit 1; }
 
eval set -- "$parameters"
out_loc_flag=0
indata_flag=0
incontig_flag=0
datatype_flag=0
nt_flag=0
nr_flag=0
nt_noViruses_flag=0
taxidDB_flag=0
thread=10
cor=0.8
rm_length=600
min_rdrp_multi=100
min_nordrp_multi=20
min_TPM=200
library_ID_flag=0
quantify_method=salmon
preprocess=false
assemble_method=spades
only_rdrp_find=0

while true;do
    case "$1" in
        --indata)  indata_flag=1; rawData_loc=$2;  shift 2;;
        --incontig) incontig_flag=1; contig=$2; shift 2 ;;
        --thread) thread=$2; shift 2 ;;
        --cor) cor=$2; shift 2 ;;
		--rm_length) rm_length=$2; shift 2 ;;
		--min_rdrp_multi) min_rdrp_multi=$2; shift 2 ;;
		--min_nordrp_multi) min_nordrp_multi=$2; shift 2 ;;
		--min_TPM) min_TPM=$2; shift 2 ;;
        --nt)  nt_flag=1; nt_loc=$2;  shift 2;;
		--nr)  nr_flag=1; nr_loc=$2;  shift 2;;
        --nt_noViruses)  nt_noViruses_flag=1; nt_noViruses_loc=$2;  shift 2;;
		--library_ID)  library_ID_flag=1; library_ID=$2;  shift 2;;
		--datatype)  datatype_flag=1; datatype=$2;  shift 2;;
		--method)   quantify_method=$2;  shift 2;;
		--assemble)   assemble_method=$2;  shift 2;;
		--only_rdrp_find)   only_rdrp_find=$2;  shift 2;;
		--preprocess)   preprocess=$2;  shift 2;;
        --taxidDB)  taxidDB_flag=1; taxidDB_loc=$2;  shift 2;;
        -o) out_loc_flag=1; out_loc=$2; shift 2 ;;
        --version) echo "$0 version V1.0"; exit ;;
        --help) usage;exit ;;
        --)
            shift
			if [[ $preprocess != true && $preprocess != false ]]; then echo "please input true or false!!! --preprocess";  exit 1; fi;
			if [[ $sensitive -ne 0 && $sensitive -ne 1 ]]; then echo "please input 0 or 1!!! --sensitive";  exit 1; fi;
            if [ $indata_flag -eq 0 ]; then echo "please input the location of the raw data!!! --indata"; exit 1; fi; 
            if [[ $incontig_flag -eq 0 && $library_ID_flag -eq 0 && $only_rdrp_find -eq 0 ]]; then echo "please input a contig name or a library_ID!!! --incontig or --library_ID";  exit 1; fi; 
			if [[ $nt_flag -eq 0 && $only_rdrp_find -eq 0 ]]; then echo "please input the location of nt!!! --nt";  exit 1; fi;
			if [[ $nr_flag -eq 0 && $preprocess == true ]]; then echo "please input the location of nr!!! --nr";  exit 1; fi;
			if [[ $nt_noViruses_flag -eq 0 && $only_rdrp_find -eq 0 ]]; then echo "please input the location of nt_noViruses database!!! --nt_noViruses";  exit 1; fi;
			if [ $datatype_flag -eq 0 ]; then echo "please input the type of input data!!! --datatype";  exit 1; fi;
			if [ $taxidDB_flag -eq 0 ]; then echo "please input the location of prot.accession2taxid database!!! --taxidDB";  exit 1; fi;
            if [ $out_loc_flag -eq 0 ]; then echo "the output files are all in the current directory"; fi
            break ;;
        *) usage;exit 1;;
    esac
done  
if [[ $datatype -ne 1 && $datatype -ne 2 ]]; then echo 'please re_input the type of input data, 1 or 2,for 1 means single type,2 means double';  exit 1; fi
if [ $out_loc_flag -eq 0 ]; then megahit=megahit;  nr=nr; rdrp=rdrp; network=network; fi
if [ $out_loc_flag -eq 1 ]; then megahit=$out_loc/megahit; nr=$out_loc/nr; rdrp=$out_loc/rdrp; network=$out_loc/network; fi

chmod +x align_and_estimate_abundance.pl
chmod +x ORFfinder
#################################
present_loc=`pwd`
megahit_loc=$present_loc/$megahit
path=$rawData_loc

#########################part1#####data preprocessing###############################
if [ $preprocess == true ];then
	for file in `cat ${present_loc}/file_list.txt`;
	do
#########################assemble###################################################
		if [ $datatype -eq 1 ]; then 
			fastp -i $rawData_loc/"$file".fq.gz -o $rawData_loc/"$file"-fp.fq.gz -w ${thread}
			ribodetector_cpu -l 100 -i $rawData_loc/"$file"-fp.fq.gz -t ${thread} -e norrna  -o $rawData_loc/"$file".clean.fq.gz
		fi
        if [ $datatype -eq 2 ]; then 
			fastp -i $rawData_loc/"$file"_1.fq.gz -I $rawData_loc/"$file"_2.fq.gz -o $rawData_loc/"$file"_1-fp.fq.gz -O  $rawData_loc/"$file"_2-fp.fq.gz -w ${thread}
			ribodetector_cpu -l 100 -i $rawData_loc/"$file"_1-fp.fq.gz $rawData_loc/"$file"_2-fp.fq.gz  -t ${thread} -e norrna  -o $rawData_loc/"$file".clean_{1,2}.fq.gz
			cd $rawData_loc
			rm -rf $rawData_loc/"$file"_1-fp.fq.gz $rawData_loc/"$file"_2-fp.fq.gz
			rm -rf ${present_loc}/fastp.html ${present_loc}/fastp.json
		fi
				
		if [ $assemble_method == spades ]; then
			if [ $datatype -eq 1 ]; then spades.py --meta --phred-offset 33 -s $rawData_loc/"$file".clean.fq.gz -t ${thread} -o $rawData_loc/"$file".assemble; fi
			if [ $datatype -eq 2 ]; then spades.py --meta --phred-offset 33 -1 $rawData_loc/"$file".clean_1.fq.gz -2 $rawData_loc/"$file".clean_2.fq.gz -t ${thread} -o $rawData_loc/"$file".assemble; fi
			cat $rawData_loc/"$file".assemble/contigs.fasta |sed 's/ /_/g' | sed 's/=/_/g'| sed "s/>/>"$file"_/g" >$rawData_loc/"$file".assemble/"$file".fa_modify
		fi
###################################################################################		
	if [ $assemble_method == megahit ] || [ ! -s $rawData_loc/"$file".assemble/contigs.fasta ]; then rm -rf $rawData_loc/"$file".assemble;
		if [ $datatype -eq 2 ]; then megahit -1 $rawData_loc/"$file".clean_1.fq.gz  -2 $rawData_loc/"$file".clean_2.fq.gz  --num-cpu-threads ${thread}  --memory 0.9  -o $rawData_loc/"$file".assemble; fi
		if [ $datatype -eq 1 ]; then megahit -r $rawData_loc/"$file".clean.fq.gz --num-cpu-threads ${thread} --memory 0.9 -o $rawData_loc/"$file".assemble; fi
		cat $rawData_loc/"$file".assemble/final.contigs.fa |sed 's/ /_/g' | sed 's/=/_/g'| sed "s/>/>"$file"_/g" >$rawData_loc/"$file".assemble/"$file".fa_modify
	  fi
	  cp $rawData_loc/"$file".assemble/"$file".fa_modify $rawData_loc/"$file".megahit.fa
#########################Finding rna virus RdRP######################################
	  diamond blastx \
			   -q $rawData_loc/"$file".megahit.fa \
			   -d ${nr_loc} \
			   -o $rawData_loc/"$file"_assemble_nr \
			   -e 1E-4 \
			   -k 1 \
			  -p ${thread} \
			  -f 6 qseqid qlen sseqid stitle pident length evalue sstart send   
	   cd $rawData_loc
       cp -rf  ${present_loc}/sqlite_table $rawData_loc
       cp $rawData_loc/"$file"_assemble_nr $rawData_loc/"$file"_megahit_assemble_nr
       sed -i "s/#/_/" $rawData_loc/"$file"_megahit_assemble_nr
       cat $rawData_loc/"$file"_megahit_assemble_nr | cut -f3 | sort -u | grep -v "^[0-9]" | grep -v -e '^$' > $rawData_loc/"$file"_accession_list.txt.nr
       grep -F -f $rawData_loc/"$file"_accession_list.txt.nr $taxidDB_loc/prot.accession2taxid > $rawData_loc/"$file".taxid_table.txt.nr
       cat  $rawData_loc/"$file".taxid_table.txt.nr | cut -f3 -d$'\t' | sort -u > $rawData_loc/"$file".taxid_list.txt.nr
       python3 $present_loc/ncbi.taxonomist.py --sep "|" -d < $rawData_loc/"$file".taxid_list.txt.nr | sed "s/|/\t/" | sed "s/\t[^|]*|/\t/" > $rawData_loc/"$file".lineage_table.txt.nr
       cat $rawData_loc/sqlite_table/sqlite_template.nr | sed "s/template/""$file""/g" > $rawData_loc/sqlite_"$file".nr
       sqlite3 sqlite_"$file".nr.summary.sql < sqlite_"$file".nr
       mv $rawData_loc/"$file"_megahit_assemble_nr.edited $rawData_loc/"$file"_megahit_assemble_nr.edited.tsv
       rm -rf $rawData_loc/sqlite_table
       rm -rf $rawData_loc/"$file".taxid_table.txt.nr $rawData_loc/"$file".taxid_list.txt.nr $rawData_loc/"$file".lineage_table.txt.nr $rawData_loc/"$file".accession_list.txt.nr
       rm -rf $rawData_loc/sqlite_"$file".nr
       rm -rf $rawData_loc/sqlite_"$file".nr.summary.sql

	cd $present_loc
	grep -i "virus" $rawData_loc/"$file"_megahit_assemble_nr.edited.tsv > $rawData_loc/"$file"_assemble_nr.virus
	cat $rawData_loc/"$file"_assemble_nr.virus | cut -f2 | sort -u >$rawData_loc/"$file"_assemble_nr.virus.list
	seqtk subseq $rawData_loc/"$file".megahit.fa $rawData_loc/"$file"_assemble_nr.virus.list >$rawData_loc/"$file"_assemble_nr.virus.match
        diamond makedb --in ${present_loc}/RdRP_230330-only.fasta --db $rawData_loc/RdRP_230330-only -p ${thread}
	diamond  blastx \
		         --more-sensitive \
			 -q $rawData_loc/"$file"_assemble_nr.virus.match \
			 -d $rawData_loc/RdRP_230330-only \
			 -o $rawData_loc/"$file"_assemble_nr.rdrp \
			 -e 1E-3 \
			 -k 1 \
             -p  ${thread} \
             -f 6 qseqid qlen sseqid stitle pident length evalue qstart qend

	  cat $rawData_loc/"$file"_assemble_nr.rdrp| cut -f1 | sort -u >$rawData_loc/"$file"_assemble_nr.rdrp.list
	  seqtk subseq $rawData_loc/"$file"_assemble_nr.virus.match $rawData_loc/"$file"_assemble_nr.rdrp.list>$rawData_loc/"$file".rdrp.virus.match
	  python $present_loc/blastn_nt_novirus.py --db ${nt_noViruses_loc} -evalue 1E-10 --input $rawData_loc/"$file".rdrp.virus.match --out_fasta $rawData_loc/"$file".rdrp.virus.match.modify --out_tsv $rawData_loc/"$file".blastn.tsv --threads ${thread}
	
	  diamond  blastx \
                         --more-sensitive \
                         -q $rawData_loc/"$file".rdrp.virus.match.modify \
                         -d $rawData_loc/RdRP_230330-only \
                         -o $rawData_loc/"$file".megahit.fa.rdrp \
                         -e 1E-3 \
                         -k 1 \
             -p  ${thread} \
             -f 6 qseqid qlen sseqid stitle pident length evalue sstart send
         cat $rawData_loc/"$file".megahit.fa.rdrp| cut -f1 | sort -u >$rawData_loc/"$file"_assemble_nr.rdrp.list
          seqtk subseq $rawData_loc/"$file".rdrp.virus.match.modify $rawData_loc/"$file"_assemble_nr.rdrp.list>$rawData_loc/"$file".megahit.fa.rdrp.fasta
	  mv $rawData_loc/"$file"_assemble_nr $rawData_loc/"$file".megahit.fa.nr
	  rm -rf $rawData_loc/"$file".assemble $rawData_loc/"$file"_assemble_nr.rdrp.list 
	  rm -rf  $rawData_loc/"$file"_accession_list.txt.nr $rawData_loc/"$file"_megahit_assemble_nr $rawData_loc/"$file"_assemble_nr.rdrp.list $rawData_loc/"$file"_assemble_nr.virus.list
	  
  done
fi

if [ $only_rdrp_find -eq 0 ];then
	########################part2 finding segmented rna virus###########################
	mkdir $megahit
	mkdir $nr
	mkdir $rdrp
	mkdir $network
	for file in `cat ${present_loc}/file_list.txt`;
	do
	cp $rawData_loc/"$file".megahit.fa.rdrp.fasta  rdrp/"$file".megahit.fa.megahit.rdrp.virus.match
	cp $rawData_loc/"$file".megahit.fa  megahit/"$file".megahit.fa
	cp $rawData_loc/"$file".megahit.fa.nr  nr/"$file".megahit.fa.nr
	awk '{print $0}' $rdrp/"$file".megahit.fa.megahit.rdrp.virus.match  >> $rdrp/total.rdrp.virus
	done;
        cd $present_loc
		############################################################################
	if [ $library_ID_flag -eq 0 ];
	then
		mkdir $rdrp/total.rdrp.megahit.fa_contigs
		for file in `cat ${present_loc}/file_list.txt`;
		do
		if [ $datatype -eq 1 ]; then perl align_and_estimate_abundance.pl --transcripts $rdrp/total.rdrp.virus --seqType fq --single $rawData_loc/"$file".clean.fq.gz --est_method $quantify_method --aln_method bowtie2  --output_dir $rdrp/"$file"_RSEM-gai-total --thread_count ${thread} --prep_reference; fi
		if [ $datatype -eq 2 ]; then perl align_and_estimate_abundance.pl --transcripts $rdrp/total.rdrp.virus --seqType fq --left $rawData_loc/"$file".clean_1.fq.gz --right $rawData_loc/"$file".clean_2.fq.gz --est_method $quantify_method --aln_method bowtie2  --output_dir $rdrp/"$file"_RSEM-gai-total --thread_count ${thread} --prep_reference; fi

		if [ $quantify_method == RSEM ]; then mv $rdrp/"$file"_RSEM-gai-total/RSEM.genes.results $rdrp/"$file"_RSEM-gai-total/"$file"_RSEM.genes.results; fi
		if [ $quantify_method == salmon ]; then mv $rdrp/"$file"_RSEM-gai-total/quant.sf $rdrp/"$file"_RSEM-gai-total/"$file"_RSEM.genes.results; fi

		cp $rdrp/"$file"_RSEM-gai-total/"$file"_RSEM.genes.results $rdrp/total.rdrp.megahit.fa_contigs
		done;
	#############################part2########################################

		Rscript 2.TPM-combine.R $rdrp
		cp $rdrp/RSEM.csv ./
		mkdir library_ID
		# key in the contigs name you are concerned about
		Rscript libraryID_search.R $contig

		# get the library_ID
		cd library_ID
		library_ID=$(ls)
		cd ..
		rm -rf library_ID
		# screnn repetitive and similar contigs

		cd ${present_loc}/$nr
	fi
	#########################################################################
	files=(
        ${library_ID}
        )

	for files in "${files[@]}";
	 do
		 cd ${present_loc}/nr
		   cp -rf  ${present_loc}/sqlite_table ${present_loc}/nr
		   mv ${present_loc}/nr/"$files".megahit.fa.nr ${present_loc}/nr/"$files"_megahit_assemble_nr
		   cat ${present_loc}/nr/"$files"_megahit_assemble_nr | cut -f3 | sort -u | grep -v "^[0-9]" | grep -v -e '^$' > ${present_loc}/nr/"$files"_accession_list.txt.nr
		   grep -F -f ${present_loc}/nr/"$files"_accession_list.txt.nr $taxidDB_loc/prot.accession2taxid > ${present_loc}/nr/"$files".taxid_table.txt.nr
		   cat  ${present_loc}/nr/"$files".taxid_table.txt.nr | cut -f3 -d$'\t' | sort -u > ${present_loc}/nr/"$files".taxid_list.txt.nr
		   python3 ${present_loc}/ncbi.taxonomist.py --sep "|" -d < ${present_loc}/nr/"$files".taxid_list.txt.nr | sed "s/|/\t/" | sed "s/\t[^|]*|/\t/" > ${present_loc}/nr/"$files".lineage_table.txt.nr
		   cat sqlite_table/sqlite_template.nr | sed "s/template/""$files""/g" > sqlite_"$files".nr
		   sqlite3 sqlite_"$files".nr.summary.sql < sqlite_"$files".nr
		   mv ${present_loc}/nr/"$files"_megahit_assemble_nr.edited ${present_loc}/nr/"$files"_megahit_assemble_nr.edited.tsv
		   cp ${present_loc}/nr/"$files"_megahit_assemble_nr.edited.tsv ${present_loc}/megahit/"$files"_megahit_assemble_nr.edited.tsv
		   rm -rf sqlite_"$files".nr
		   rm -rf sqlite_"$files".nr.summary.sql
		   rm -rf ${present_loc}/nr/"$files".taxid_table.txt.nr ${present_loc}/nr/"$files".taxid_list.txt.nr ${present_loc}/nr/"$files".lineage_table.txt.nr ${present_loc}/nr/"$files".accession_list.txt.nr
	done;
	########################################################################
	cp ${present_loc}/3.1coefficient-matrix.R ${present_loc}/megahit/3.1coefficient-matrix.R
	sed -i "s/\#/_/g" ${library_ID}_megahit_assemble_nr.edited.tsv
	cp ${present_loc}/nr/${library_ID}_megahit_assemble_nr.edited.tsv ${present_loc}/megahit/${library_ID}_megahit_assemble_nr.edited.tsv
	cd ${present_loc}/megahit
	sed -i "s/\#/_/g" ${library_ID}_megahit_assemble_nr.edited.tsv
	Rscript 3.1coefficient-matrix.R ${library_ID} $megahit_loc  $rm_length 
	cd ${present_loc}/megahit
	cat RSEM_pre.txt|cut -f2 |sed "s/\"//g" > RSEM_pre.txt.list
	sort -n RSEM_pre.txt.list | uniq > RSEM_pre.txt1.list
	seqtk subseq ${present_loc}/megahit/${library_ID}.megahit.fa RSEM_pre.txt1.list > ${present_loc}/megahit/${library_ID}.megahit.fas-1
    grep ">" ${present_loc}/megahit/${library_ID}.megahit.fa > ${present_loc}/megahit/${library_ID}.megahit.list
    sed -i "s/>//" ${present_loc}/megahit/${library_ID}.megahit.list
    awk -F " " '{print $1}' ${present_loc}/nr/${library_ID}_megahit_assemble_nr > ${present_loc}/megahit/${library_ID}.megahit_nr.list
	megahit_list_len=$(wc -l < ${present_loc}/megahit/${library_ID}.megahit.list)
	megahit_nr_list_len=$(wc -l < ${present_loc}/megahit/${library_ID}.megahit_nr.list)
	if [ "$megahit_nr_list_len" -ge "$megahit_list_len" ]
	then
		grep -Fxvf ${present_loc}/megahit/${library_ID}.megahit.list ${present_loc}/megahit/${library_ID}.megahit_nr.list > output.txt
    else
		grep -Fxvf ${present_loc}/megahit/${library_ID}.megahit_nr.list ${present_loc}/megahit/${library_ID}.megahit.list > output.txt
	fi
    seqtk subseq ${present_loc}/megahit/${library_ID}.megahit.fa output.txt > ${present_loc}/megahit/${library_ID}.megahit.fas-2
 	awk -v RS='>' -v ORS='' 'length($2) >= '"$rm_length"' {print ">"$0}' ${present_loc}/megahit/${library_ID}.megahit.fas-2 > ${present_loc}/megahit/${library_ID}.megahit.fas-3
 	awk '/^>/{p=!d[$1]}p' ${present_loc}/megahit/${library_ID}.megahit.fas-1 ${present_loc}/megahit/${library_ID}.megahit.fas-3 > ${present_loc}/megahit/${library_ID}.megahit.fas
 	grep ">" ${present_loc}/megahit/${library_ID}.megahit.fas > ${present_loc}/megahit/${library_ID}.megahit.list
        sed -i "s/>//" ${present_loc}/megahit/${library_ID}.megahit.list
	rm -rf   ${present_loc}/megahit/${library_ID}.megahit_nr.list ${present_loc}/megahit/${library_ID}.megahit.fas-1 ${present_loc}/megahit/${library_ID}.megahit.fas-2 ${present_loc}/megahit/${library_ID}.megahit.fas-3
 	cd ${present_loc}/megahit

	cd-hit-est -d 100 -M 0 -T ${thread} -i ${present_loc}/megahit/${library_ID}.megahit.fas -o ${present_loc}/megahit/${library_ID}.megahit.fa-cd-hit -c 0.8

	sed  "s/>${library_ID}_/>/g" ${library_ID}.megahit.fa-cd-hit > ${library_ID}.megahit.fa-cd-hit-gai
	${present_loc}/ORFfinder -in ${present_loc}/megahit/${library_ID}.megahit.fa-cd-hit-gai -ml 30 -out ${present_loc}/megahit/${library_ID}.megahit.fa-cd-hit.prot.fasta -s 2

	cd-hit -d 100 -M 0 -T ${thread} -i ${present_loc}/megahit/${library_ID}.megahit.fa-cd-hit.prot.fasta -o ${present_loc}/megahit/${library_ID}.megahit.prot.fasta-cd-hit -c 0.8

	grep -oP '(?<=_)[^:]+(?=:)' ${present_loc}/megahit/${library_ID}.megahit.prot.fasta-cd-hit | uniq > ${library_ID}_ID.txt

	sed  "s/^/>${library_ID}_/g" ${library_ID}_ID.txt > ${present_loc}/megahit/${library_ID}.list

	rm -rf ${present_loc}/megahit/${library_ID}.megahit.prot.fasta-cd-hit ${library_ID}_ID.txt ${present_loc}/megahit/${library_ID}.megahit.fa-cd-hit.prot.fasta ${present_loc}/megahit/${library_ID}.megahit.fa-cd-hit  ${present_loc}/megahit/${library_ID}.megahit.prot.fasta-cd-hit.clstr ${present_loc}/megahit/${library_ID}.megahit.fa-cd-hit.clstr

	sed  "s/>//g" ${present_loc}/megahit/${library_ID}.list > ${present_loc}/megahit/${library_ID}.list.tsv
	seqtk subseq ${present_loc}/megahit/${library_ID}.megahit.fa  ${present_loc}/megahit/${library_ID}.list.tsv > ${present_loc}/megahit/${library_ID}.re.fasta
    #######################################################################
        
	python $present_loc/blastn_nt_novirus.py --evalue 1E-3 --db ${nt_noViruses_loc} --input ${present_loc}/megahit/${library_ID}.re.fasta --out_fasta ${present_loc}/megahit/${library_ID}.re.fasta.modify --out_tsv ${present_loc}/megahit/${library_ID}.re.blastn.tsv --threads ${thread}
    awk -F " " '{print $1}' ${present_loc}/megahit/${library_ID}.re.blastn.tsv|uniq > ${present_loc}/megahit/${library_ID}.re.blastn.txt
    
    grep ">" ${present_loc}/megahit/${library_ID}.re.fasta.modify > ${present_loc}/megahit/${library_ID}.re.fasta.modify.list
    sed -i "s/>//" ${present_loc}/megahit/${library_ID}.re.fasta.modify.list
   
    grep -vFf ${present_loc}/megahit/${library_ID}.re.fasta.modify.list ${present_loc}/megahit/${library_ID}.re.blastn.txt > ${present_loc}/megahit/${library_ID}.re.fasta.modify.list_del
    grep -Ff ${present_loc}/megahit/${library_ID}.re.fasta.modify.list_del ${library_ID}_megahit_assemble_nr.edited.tsv > ${library_ID}_megahit_assemble_nr.edited.tsv_del
    grep -i -E 'virus|viruses' ${library_ID}_megahit_assemble_nr.edited.tsv_del > ${library_ID}_megahit_assemble_nr.edited.tsv_del_re
    awk -F " " '{print $2}' ${library_ID}_megahit_assemble_nr.edited.tsv_del_re >${library_ID}_megahit_assemble_nr.edited.tsv_del_re.txt
    seqtk subseq ${present_loc}/megahit/${library_ID}.re.fasta ${library_ID}_megahit_assemble_nr.edited.tsv_del_re.txt > ${present_loc}/megahit/${library_ID}.re.fasta_del
    awk '/^>/{p=!d[$1]}p' ${present_loc}/megahit/${library_ID}.re.fasta.modify ${present_loc}/megahit/${library_ID}.re.fasta_del > ${present_loc}/megahit/${library_ID}.re.fasta-1
    mv ${present_loc}/megahit/${library_ID}.re.fasta-1 ${present_loc}/megahit/${library_ID}.re.fasta
   
    ##########again########################################################
        rm ${present_loc}/megahit/${library_ID}.re.blastn.tsv ${present_loc}/megahit/${library_ID}.re.blastn.txt ${present_loc}/megahit/${library_ID}.re.fasta.modify.list ${present_loc}/megahit/${library_ID}.re.fasta.modify.list_del ${library_ID}_megahit_assemble_nr.edited.tsv_del
        rm ${library_ID}_megahit_assemble_nr.edited.tsv_del_re.txt ${present_loc}/megahit/${library_ID}.re.fasta_del
    #####RdRP#############################################################
	cd ${present_loc}/rdrp
	mv ${library_ID}.megahit.fa.megahit.rdrp.virus.match ${library_ID}.rdrp.virus.match

	cd-hit-est -M 0 -T ${thread} -i ${library_ID}.rdrp.virus.match -o ${library_ID}.rdrp.virus.match-cd-hit -c 0.999

	sed  "s/>${library_ID}_/>/g" ${library_ID}.rdrp.virus.match-cd-hit > ${library_ID}.rdrp.virus.match-cd-hit-gai
	${present_loc}/ORFfinder  -in ${present_loc}/rdrp/${library_ID}.rdrp.virus.match-cd-hit-gai -ml 30 -out ${present_loc}/rdrp/${library_ID}.rdrp.virus.match-cd-hit.prot.fasta -s 2

	cd-hit -M 0 -T ${thread} -i ${present_loc}/rdrp/${library_ID}.rdrp.virus.match-cd-hit.prot.fasta -o ${present_loc}/rdrp/${library_ID}.rdrp.virus.match-cd-hit.prot.fasta-cd-hit -c 0.999
	grep -oP '(?<=_)[^:]+(?=:)' ${present_loc}/rdrp/${library_ID}.rdrp.virus.match-cd-hit.prot.fasta-cd-hit | uniq > ${library_ID}-rdrp_ID.txt
	sed  "s/^/>${library_ID}_/g" ${library_ID}-rdrp_ID.txt > ${present_loc}/rdrp/${library_ID}.rdrp.list-1

	sed  "s/>//g" ${present_loc}/rdrp/${library_ID}.rdrp.list-1 > ${present_loc}/rdrp/${library_ID}.rdrp.list
	seqtk subseq ${library_ID}.rdrp.virus.match ${library_ID}.rdrp.list > ${library_ID}.rdrp.fasta
	######################################################################
        grep ">" ${library_ID}.rdrp.fasta > ${present_loc}/rdrp/${library_ID}.rdrp.list
        sed  "s/>//g" ${present_loc}/rdrp/${library_ID}.rdrp.list > ${present_loc}/rdrp/${library_ID}.rdrp.list.tsv
        rm -rf ${present_loc}/rdrp/${library_ID}.megahit.fa.megahit.rdrp.virus.match-cd-hit ${present_loc}/rdrp/${library_ID}.megahit.fa.megahit.rdrp.virus.match-cd-hit.clstr ${present_loc}/rdrp/${library_ID}.megahit.fa.megahit.rdrp.virus.match-cd-hit.prot.fasta-cd-hit.clstr ${present_loc}/rdrp/${library_ID}.megahit.fa.megahit.rdrp.virus.match-cd-hit.prot.fasta ${library_ID}.rdrp.blastn.tsv
	#########################################################################
	cd ${present_loc}

	mkdir $present_loc/megahit/total.nr.rdrp.megahit.fa_contigs
	for file in `cat ${present_loc}/file_list.txt`;
	do
	if [ $datatype -eq 1 ]; then perl $present_loc/align_and_estimate_abundance.pl --transcripts $present_loc/megahit/${library_ID}.re.fasta --seqType fq --single $rawData_loc/"$file".clean.fq.gz --est_method $quantify_method --aln_method bowtie2  --output_dir $present_loc/megahit/"$file"_RSEM-gai-total --thread_count ${thread} --prep_reference; fi
	if [ $datatype -eq 2 ]; then perl $present_loc/align_and_estimate_abundance.pl --transcripts $present_loc/megahit/${library_ID}.re.fasta --seqType fq --left $rawData_loc/"$file".clean_1.fq.gz --right $rawData_loc/"$file".clean_2.fq.gz --est_method $quantify_method --aln_method bowtie2  --output_dir $present_loc/megahit/"$file"_RSEM-gai-total --thread_count ${thread} --prep_reference; fi

	cd $present_loc/megahit/"$file"_RSEM-gai-total
	if [ $quantify_method == RSEM ]; then mv RSEM.genes.results "$file"_RSEM.genes.results; fi
	if [ $quantify_method == salmon ]; then mv quant.sf "$file"_RSEM.genes.results; fi
	 cd ..
	 cp "$file"_RSEM-gai-total/"$file"_RSEM.genes.results $present_loc/megahit/total.nr.rdrp.megahit.fa_contigs
	done;

	 cd total.nr.rdrp.megahit.fa_contigs
	 rename 's/.results/.result.tsv/'  *
	 cd ..
	#######################################################################
	cd ${present_loc}
	### coefficient-matrix
	cp  ${present_loc}/nr/${library_ID}_megahit_assemble_nr.edited.tsv ${present_loc}/megahit
	sed -i "s/#/_/" ${present_loc}/megahit/${library_ID}_megahit_assemble_nr.edited.tsv
	cp ${present_loc}/rdrp/${library_ID}.rdrp.list.tsv  ${present_loc}/megahit
	cd ${present_loc}/megahit
	cp ${present_loc}/3.coefficient-matrix.R ${present_loc}/megahit/3.coefficient-matrix.R
	Rscript 3.coefficient-matrix.R ${library_ID} $megahit_loc  
	cd ${present_loc}
	#######################################################################
	blastn -query ${present_loc}/megahit/"${library_ID}".re.fasta -db $nt_loc -out ${present_loc}/megahit/"${library_ID}"_megahit_assemble_re_nt.tsv -evalue 1E-3 -outfmt "6 qseqid qlen sacc salltitles pident length evalue sstart send" -max_target_seqs 5 -num_threads ${thread}
	######################################################################
	diamond makedb --in ${present_loc}/RdRP_230330-only.fasta --db ${present_loc}/megahit/RdRP_230330-only -p ${thread}
	diamond  blastx -q ${present_loc}/rdrp/${library_ID}.rdrp.fasta -d ${present_loc}/megahit/RdRP_230330-only -o ${present_loc}/megahit/${library_ID}.megahit.fa.rdrp.tsv --more-sensitive -e 1E-3 -k 5 -p ${thread} -f 6 qseqid qlen sseqid stitle pident length evalue sstart send
	cp $nr/${library_ID}_megahit_assemble_nr $megahit/${library_ID}_megahit_assemble_nr.tsv
	sed -i "s/#/_/" ${present_loc}/megahit/"${library_ID}"_megahit_assemble_re_nt.tsv
	cp Cor_contigs_extract.R $megahit/
	cd $megahit
	awk '/^>/ {printf("%s\t", substr($0,2)); getline; print length($0)}' "${library_ID}".re.fasta  | awk '{match($0, /len.*[0-9]*/); str=substr($0, RSTART, RLENGTH); match(str, /[0-9]+/); a=substr(str, RSTART, RLENGTH);if (a == $2) print $0"\tfalse"; else print $0"\ttrue"}' > re.fasta_length.txt
	Rscript Cor_contigs_extract.R  ${cor} ${library_ID}  ${min_TPM} ${min_rdrp_multi} ${min_nordrp_multi}
	
	cd ${present_loc}

	cp ${present_loc}/megahit/${library_ID}.network_group_fr.pdf ${present_loc}/network/
	cp ${present_loc}/megahit/${library_ID}.final.confidence_table.xlsx ${present_loc}/network/
	cp ${present_loc}/megahit/${library_ID}.pre.confidence_table.xlsx ${present_loc}/network/

	rm -rf megahit/*RSEM-gai-total
	rm -rf megahit/total.nr.rdrp.megahit.fa_contigs
	rm -rf megahit/*.fa
	rm -rf nr
	rm -rf rdrp/*rdrp.virus.match
	rm -rf rdrp/*_RSEM-gai-total
	rm -rf $megahit/*.re.fasta.salmon_quasi.idx
	rm -rf $megahit/cor.p.csv
	rm -rf $megahit/cor.r.csv
	rm -rf $megahit/RdRP_230330-only.dmnd
	rm -rf $rdrp/2.out
	rm -rf $rdrp/3.out
	cd ${present_loc}
	mkdir ${library_ID}
	mv megahit  network rdrp ${library_ID}
fi





