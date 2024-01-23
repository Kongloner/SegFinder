library(tidyverse)
library(openxlsx)
#install.packages("psych")
library(getopt)
library(psych)
#######################################################################
wdir <- getwd()
args <- commandArgs(T)
setwd(args[2])
# wdir
#data1 <- read.table(paste0(args[1],"_megahit_assemble_nr.edited.tsv"),sep = "\t",quote = "")
#setwd("/raid5/glp1/lx/parasite/mosquito/data/fasta-1/fasta/shiyan5/megahit")
#data1 <- read.table("21HNQZ3SDH1119_megahit_assemble_nr.edited.tsv",sep = "\t",quote = "")
data1 <- read.table(paste0(args[1],"_megahit_assemble_nr.edited.tsv"),sep = "\t",quote = "")
data1 <- data1[,-1]
colnames(data1) <- c("Contigs","Length","Accession","Species","Similarly","aa_length","E-value","Species_annotion")

# # 如果是未知物种
# if(as.numeric(args[3]) == 0){
  # split_b<-str_split(data1$Species_annotion,"|")
  # b<-sapply(split_b,"[",2)
  # data1$Species_annotion <-b
  # #空白即未注释上的部分全部写为Viruses,以便后续运算
  # data1$Species_annotion[is.na(data1$Species_annotion)]<-"V"
  # data2 <- data1 %>% filter(Species_annotion == "V" )
# }else{
  # data2 <- data1[unique(c(grep('(?i)virus',data1$Species_annotion),grep('(?i)virus',data1$Species))),]
# }

split_b<-str_split(data1$Species_annotion,"|")
b<-sapply(split_b,"[",2)
data1$Species_annotion <-b
#空白即未注释上的部分全部写为Viruses,以便后续运算
data1$Species_annotion[is.na(data1$Species_annotion)]<-"V"
data2 <- data1 %>% filter(Species_annotion == "V" )

data_res <- data2[which(data2$Length > as.numeric(args[3])), ]


write.table(data_res,"RSEM_pre.txt",  sep="\t",  row.names=TRUE,
            col.names=TRUE, quote=TRUE)
