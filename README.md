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
```
#### 3) Create a virtual environment: python=3.9.13
```shell
conda create -n SegFinder python=3.9.13
```

#### 4) Activate SegFinder and install necessary tools 
```shell
conda activate SegFinder   
conda install -c bioconda fastp blast seqkit seqtk megahit cd-hit ribodetector salmon spades bowtie2
conda install diamond==2.1.8
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


### Using    

```./SegFinder.sh --help``` for **help**

Assuming all databases are stored in the SegDB folder in the current working directory. Of course, you can input the actual paths of these three databases (NR, NT, and non-viral NT) according to your specific situation; the paths provided here are just for example.
#### Step 1: Raw reads Quality Control and Assembly  
```shell
./SegFinder.sh --indata testdata \
               --stage preprocess \
               ---datatype 2  \
               --assemble megahit \
               --thread 20 \
```

#### Step 2: Discovery of RdRP for RNA viruses        
```shell
./SegFinder.sh --taxidDB Seg_DB/accession2taxid/prot.accession2taxid \
               --nt_noViruses Seg_DB/NT/nt_noViruses \
               --nt Seg_DB/NT/nt  \
               --nr /shilab6/home/public/database/nr/nr \
               --thread 20 \
               --datatype 2 \
               --stage rdrp_find
```

#### Step 3: segmented RNA virus finder        
```shell
./SegFinder.sh --taxidDB /shilab6/home/public/database/others/prot.accession2taxid  --nt_noViruses SegDB/nt_noViruses/nt_noViruses --nt /shilab6/home/public/database/nt/nt --thread 200 --datatype 2 --method salmon --stage segment_find -—library_ID SRR7102799
./SegFinder.sh --taxidDB Seg_DB/accession2taxid/prot.accession2taxid \
               --nt_noViruses Seg_DB/NT/nt_noViruses \
               --nt Seg_DB/NT/nt  \
               --thread 20 \
               --rm_length 600 \
               --datatype 2 \
               --cor 0.8 \
               --method salmon  \
               --stage segment_find \
               --library_ID SRR7102799 \
``` 

## Cite this article
Xue Liu#, Jianbin Kong#, Yongtao Shan, Ziyue Yang, Jiafan Miao1,2,3, Yuanfei Pan4, Tianyang Luo1,2,3, Zhan Xu1,2,3, Zhiyuan Shi1,2,3, Yingmei Wang1,2,3, Qinyu Gou1,2,3, Chunhui Yang1,2,3, Chunmei Li1,2,3, Shaochuan Li5, Xu Zhang5, Yanni Sun6, Edward C. Holmes7,8, Deyin Guo*,9,10, Mang Shi*,1,2,3,11. SegFinder: Segment RNA virus discovery based on correlation in multiple libraries. ----------; doi: -------------------  
\# equally contributed    

  
