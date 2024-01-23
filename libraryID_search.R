rm(list=ls())

#install.packages("psych")
library(openxlsx)
library(tidyverse)
library(psych)
###################################
wdir <- getwd()
args <- commandArgs(T)

data <- read.table("RSEM.csv",sep = ",",header=F,row.names = 1)
colnames(data) <- data[1,]
data <- data[-1,]
rowname <- rownames(data)
colname <- colnames(data)
data <- as.data.frame(lapply(data,as.numeric))
rownames(data) <- rowname
colnames(data) <- colname
data <- data[which(rowSums(data) > 0),]
data <- data[,which(colSums(data) > 0)]

input_contigs <- args[1]

library_ID <- colname[which.max(c(t(data[input_contigs,])))]
save(library_ID,file = paste0('library_ID/',library_ID))
