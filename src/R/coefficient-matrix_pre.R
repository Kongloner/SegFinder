rm(list = ls())

cat("Loading of the libraries.... ")
suppressMessages(library(stringr))
suppressMessages(library(dplyr))
cat("... done ! ")

#### Replace all sections with empty annotation information with ‘Viruses’ to facilitate subsequent calculations ####
args <- commandArgs(T)
setwd(args[2])

data1 <- read.table(paste0(args[1],"_megahit_assemble_nr.edited.tsv"),sep = "\t",quote = "")
data1 <- data1[,-1]
colnames(data1) <- c("Contigs","Length","Accession","Species","Similarly","aa_length","E-value","Species_annotion")

split_b<-str_split(data1$Species_annotion,"|")
b<-sapply(split_b,"[",2)
data1$Species_annotion <-b
data1$Species_annotion[is.na(data1$Species_annotion)]<-"V"
data2 <- data1 %>% filter(Species_annotion == "V" )

data_res <- data2[which(data2$Length > as.numeric(args[3])), ]

write.table(data_res,"RSEM_pre.txt",  sep="\t",  row.names=TRUE,
            col.names=TRUE, quote=TRUE)
