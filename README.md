# SegFinder   
**SegFinder** is a correlation-based approach that enhances abundance similarity and co-occurrence methods to **detect new genomic segments of RNA viruses** by analyzing abundance patterns and their correlations across samples.

## 1. segmented virus finder workflow  

<center>
<img alt="SegFinder" src="./flow/workflow.png"/>
SegFinder detection pipeline. a, Schematic overview of the discovery of RdRP for RNA viruses. The inputs are fastq files for multiple meta-transcriptome libraries. rRNA, ribosomal RNA; NR, Non-Redundant Protein Sequence Database; NT, Nucleotide Sequence Database. b, The processing pipeline of correlation calculation. L, library; C, contig; c, Schematic illustration of filtering of segmented RNA virus clusters. Cor, correlation; TPM, Transcripts Per Kilobase of exon model per Million mapped reads.



## 2. Environment Installation

Our recommendation is for users to clone our stable `main` branch directly and designate `SegFinder` as the working directory. The setup for SegFinder can be done as follows.

### step1: Update git and clone repository
#### 1) centos
```shell
sudo yum update
sudo yum install sqlite sqlite-devel git-all
```
#### 2) ubuntu
```shell
sudo apt-get update
sudo apt install sqlite3 libsqlite3-dev git-all 
```
#### 3) Clone repository to the current directory
```shell
git clone https://github.com/Kongloner/SegFinder.git
chmod +x SegFinder/SegFinder.sh
```
### step2: Install conda and necessary tools
#### 1) Download anaconda3
```shell
wget https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh
```
#### 2) Install conda
```shell
sh Anaconda3-2022.05-Linux-x86_64.sh
##### Notice: Select Yes to update ~/.bashrc
```
```shell
source ~/.bashrc
# conda config --add channels conda-forge
# conda config --add channels bioconda
# conda config --add channels defaults
```
#### 3) Create a virtual environment: python=3.9.13
```shell
conda create -n SegFinder python=3.9.13
```

#### 4) Activate SegFinder and install necessary tools 
```shell
conda activate SegFinder   
conda install -c bioconda fastp blast seqkit seqtk megahit cd-hit ribodetector salmon spades bowtie2
conda install -c bioconda diamond==2.1.8
``` 

### step3: Install R and R package  
- R>=4.2

The first step is to install [**R software**](https://www.r-project.org/). Once this is done, several packages  have to be installed too. To do so start a R session and type :
```shell
# Some users can accelerate by mirror
# options(BioC_mirror="https://mirrors.tuna.tsinghua.edu.cn/bioconductor/")
# options("repos" = c(CRAN="http://mirrors.cloud.tencent.com/CRAN/"))
```
```shell
# install packages from CRAN
cran.packages <- c("BiocManager", "abind", "argparse", "openxlsx", "data.table", "doParallel", "dplyr", "foreach", "magrittr", "stringr", "tidyr", "Matrix", "igraph")

for (pkg in cran.packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, ask = F, update = F)
  }
}
```
```shell
# install packages from Bioconductor
bioconductor.packages <- c("GenomeInfoDbData", "Biostrings")

for (pkg in bioconductor.packages) {
    if (!requireNamespace(pkg, quietly = TRUE)) {
        BiocManager::install(pkg, ask = F, update = F)
    }
}
```

### step4: Download and configure the database
The databases require substantial disk space, so please ensure sufficient storage is available before proceeding. If you already have these databases, you may skip the download step and proceed directly to configuration. For those who need to download the databases, note that the speed will depend on your internet connection. To enhance efficiency, you may also consider using alternative methods, such as the Aspera (ascp) protocol.

```shell
# Create a folder named `Seg_DB` in the working directory to store these databases
mkdir -p Seg_DB
cd Seg_DB
```

#### 1) accession2taxid
```shell
#Download the `prot.accession2taxid.gz` file
wget -c https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/prot.accession2taxid.gz
wget -c https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/prot.accession2taxid.gz.md5

#Check for the file integrity
md5sum -c prot.accession2taxid.gz.md5

#Unzip the files
gunzip -c prot.accession2taxid.gz > accession2taxid/prot.accession2taxid
```
#### 2) [NCBI Non-Redundant Protein Database (NR)](./flow/db_NR.md)
#### 3) [NCBI Non-Redundant Nucleotide Database (NT)](./flow/db_NT.md)
#### 4) [Virus-free Non-Redundant Nucleotide Database (Virus-free NT)](./flow/db_nt_noViruses.md)
Note: If you need to remove contamination from viral sequences, you can download this non-viral database to align and filter out the contaminating sequences. Use the `--nt_noViruses` parameter to specify the path to this database. This database is optional and does not need to be used unless contamination removal is required.

### Using    

```./SegFinder.sh --help``` for **help**

Assuming all databases are stored in the `SegDB` folder in the current working directory. Of course, you can input the actual paths of these databases according to your specific situation.
#### Step 1: Raw reads Quality Control and Assembly  
```shell
./SegFinder.sh --indata testdata \
               --stage preprocess 
```

#### Step 2: Discovery of RdRP for RNA viruses        
```shell
./SegFinder.sh  --stage rdrp_find
```

#### Step 3: Segmented RNA virus finder        
```shell
./SegFinder.sh --stage segment_find \
               --library_ID SRR7102799 
```
Required arguments:     
 
 `--indata`: the location of the raw data (in 'fastq' format).   

 `--stage`: specify the stage of the pipeline to run: preprocess, rdrp_find, or segment_find. 

 `--library_ID`: the library you want to search for segmented viruses, can input multiple IDs separated by spaces.  
 
 More optional arguments: 

 `--datatype`: specifies the type of input sequencing data, either single-end (1) or paired-end (2) reads (default: 2).

 `-o`: the directory to output the results (default: current directory). 
 
 `--thread`: the number of threads (default: 10). 
 
 `--cor`: correlation coefficient (default: 0.8).  
 
 `--nt_noViruses`: the location of nt_noViruses database, used to remove viral sequence contamination, optional.  
 
 `--nt`: the location of nt database.(Use the absolute path to specify the location of the database (default: Seg_DB/NT/nt).
 
 `--nr`: the location of nr database.(Use the absolute path to specify the location of the database (default: Seg_DB/NR/nr). 
 
 `--method`: the method to quantify the transcript abundances,salmon or RSEM (default salmon).    
 
 `--taxidDB`: the location of prot.accession2taxid database.(Use the absolute path to specify the location of the database (default: Seg_DB/accession2taxid/prot.accession2taxid).  
 
 `--rm_length`: the contigs whose length less than this value will be removed (default 600). 
 
 `--min_rdrp_multi`: minimum length of rdrp and their re-assembled contigs to be retained (default 100). 
 
 `--min_nordrp_multi`: minimum length of non-rdrp and their re-assembled contigs to be retained (default 20).  
 
 `--assemble`: the tool to assemble the raw reads, megahit or spades (default spades).  
 
 `--min_TPM`: if there exist the contig whose TPM is less than this value, the cluster it is in will be removed (default 200).  
 
## Cite this article
Xue Liu#, Jianbin Kong#, Yongtao Shan, Ziyue Yang, Jiafan Miao1,2,3, Yuanfei Pan4, Tianyang Luo1,2,3, Zhan Xu1,2,3, Zhiyuan Shi1,2,3, Yingmei Wang1,2,3, Qinyu Gou1,2,3, Chunhui Yang1,2,3, Chunmei Li1,2,3, Shaochuan Li5, Xu Zhang5, Yanni Sun6, Edward C. Holmes7,8, Deyin Guo*,9,10, Mang Shi*,1,2,3,11. SegFinder: an automated tool for identifying RNA virus genome segments through co-occurrence in multiple sequenced samples. ----------; doi: -------------------  
\# equally contributed    

  
