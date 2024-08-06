rm(list = ls())

cat("Loading of the libraries.... \n")
suppressMessages(library(dplyr))
cat("... done ! \n")
#### merge the TPM of all contigs from all libraries and generates a CSV output.

args <- commandArgs(T)

filelist <- list.files(paste0(args[1],"/total.rdrp.megahit.fa_contigs/"))
files <- paste(paste0(args[1],"/total.rdrp.megahit.fa_contigs/"),filelist,sep="") 
data <- list()

finalData <- read.table(files[1], header=T, sep="\t")
# all(finalData$gene_id == finalData$Name)
finalData <- finalData[c(1,which(colnames(finalData) %in% 'TPM' ))] 
TPMtoName <- strsplit(filelist[1],split = '_',fixed = T)[[1]][1]
colnames(finalData)[2] <- TPMtoName
by_name <- colnames(finalData)[1]
finalData <- finalData[!duplicated(finalData[,1]),]

for (i in 2:(length(files))){
  data <- read.table(files[i], header=T, sep="\t")
  data <- data[c(1,which(colnames(data) %in% 'TPM' ))] 
  TPMtoName <- strsplit(filelist[i],split = '_',fixed = T)[[1]][1]
  colnames(data)[2] <- TPMtoName
  data <- data[!duplicated(data[,1]),]
  finalData <- full_join(finalData,data,by = by_name)
}

write.csv(finalData,file = paste0(args[1],'/RSEM.csv'),row.names = F)
