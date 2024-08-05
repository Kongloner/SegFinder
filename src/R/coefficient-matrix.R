rm(list = ls())

cat("Loading of the libraries.... ")
suppressMessages(library(dplyr))
suppressMessages(library(data.table))
suppressMessages(library(foreach))
suppressMessages(library(doParallel))
suppressMessages(library(abind))
suppressMessages(library(stringr))
cat("... done ! ")

options(future.globals.maxSize = 100000 * 1024^2)

#### Calculate the Spearman correlation between RdRp and other contigs ####

args <- commandArgs(T)
setwd(args[2])
# args[1] <- 'S17WDBatR03'
# data1 <- read.table(paste0(args[1],"_megahit_assemble_nr.edited.tsv"),sep = "\t",quote = "")

filelist <- list.files("total.nr.rdrp.megahit.fa_contigs/")
files <- paste("total.nr.rdrp.megahit.fa_contigs/",filelist,sep="")
data <- list()
train <- list()

finalData <- fread(files[1], header = TRUE, sep = "\t",data.table = F)
finalData <- finalData[,c(1, which(colnames(finalData) %in% 'TPM'))]
TPMtoName <- strsplit(filelist[1], split = '_', fixed = TRUE)[[1]][1]
colnames(finalData)[2] <- TPMtoName
finalData <- finalData[!duplicated(finalData$Name),]
by_name <- colnames(finalData)[1]
contigs_order <- finalData[[`by_name`]]


process_file <- function(file) {
  data <- fread(paste("total.nr.rdrp.megahit.fa_contigs/",file,sep=""), header = TRUE, sep = "\t",data.table = F)
  data <- data[, c(1, which(colnames(data) %in% 'TPM'))]
  TPMtoName <- strsplit(file, split = '_', fixed = TRUE)[[1]][1]
  colnames(data)[2] <- TPMtoName
  data <- data[!duplicated(data$Name),]
  data[[`by_name`]] <- factor(data[[`by_name`]],levels = contigs_order)
  data <- data[-1]
  return(data)
}

data_list <- lapply(filelist[-1], function(file) {
  process_file(file)
})

# Combine all data frames in data_list into one large data frame
combined_data <- bind_cols(data_list)
finalData <- cbind(finalData,combined_data)

fwrite(finalData, file = 'RSEM_rdrp.csv', quote = FALSE)

data_res <- fread(paste0(args[1],'.megahit.list'),sep = '\t',data.table = F,header = F)
colnames(data_res) <- 'Contigs'
finalData <- finalData[finalData[[`by_name`]] %in% data_res$Contigs,]
rownames(finalData) <- finalData[[`by_name`]]
finalData <- finalData[-1]

list <- fread(paste0(args[1],".rdrp.list.tsv"),sep = '\t',data.table = F,header = F)
colnames(list) <- c("Contigs")

rowname <- rownames(finalData)
colname <- colnames(finalData)
finalData <- as.data.frame(lapply(finalData,as.numeric))
rownames(finalData) <- rowname
colnames(finalData) <- colname
finalData <- finalData[which(rowSums(finalData) > 0),]
finalData <- finalData[,which(colSums(finalData) > 0)]
# write.csv(finalData,file = paste0(args[1],'_RSEM.csv'))
fwrite(finalData, file = paste0(args[1],'_RSEM.csv'), quote = FALSE)

data_t <- as.data.frame(t(finalData))

# The number of CPU cores to use
# This function defaults to using ‘holm’ for p-value adjustment
rdrp_contigs <- list$Contigs
cor_construct <- function(data,rdrp_contigs,threads){
  data1 <- apply(data,2,rank)
  rdrp_contigs_cols <- which(colnames(data1) %in% rdrp_contigs[rdrp_contigs %in% colnames(data1)])
  if(length(rdrp_contigs_cols) > 0){
    data2 <- data1[,rdrp_contigs_cols,drop = FALSE]
    r <- function(rx,ry){
      n <- length(rx)
      lxy <- sum((rx-mean(rx))*(ry-mean(ry)))
      lxx <- sum((rx-mean(rx))^2)
      lyy <- sum((ry-mean(ry))^2)
      r <- lxy/sqrt(lxx*lyy)
      t <- (r * sqrt(n - 2))/sqrt(1 - r^2)
      p <- -2 * expm1(pt(abs(t), (n - 2), log.p = TRUE))
      return(c(r,p))
    }
    arraybind <- function(...){
      abind(...,along = 3,force.array=TRUE)
    }
    nc <- ncol(data)
    registerDoParallel(cores = threads)
    corr <- foreach (i = 1:length(rdrp_contigs_cols),.combine = "arraybind") %dopar%{
      corr1 <- matrix(rep(0,2*nc),nrow = 2,ncol=nc)
      for(j in 1:nc) {
        corr1[,j] <- r(data2[,i],data1[,j])
      }
      corr <- corr1
    }
    if(length(rdrp_contigs_cols) == 1){
      rr <- corr[1,,drop = FALSE]
    }else{
      rr <- corr[1,,]
      rr <- t(rr)
    }
    if(length(rdrp_contigs_cols) == 1){
      pp <- corr[2,,drop = FALSE]
      lp <- lower.tri(pp)
      pa <- pp[lp]
      pa <- p.adjust(pa, "holm")
      pp[lower.tri(pp, diag = FALSE)] <- pa
    }else{
      pp <- corr[2,,]
      lp <- lower.tri(pp)
      pa <- pp[lp]
      pa <- p.adjust(pa, "holm")
      pp[lower.tri(pp, diag = FALSE)] <- pa
      pp <- t(pp)
    }
    rownames(pp) <- rdrp_contigs[rdrp_contigs %in% colnames(data1)]
    colnames(pp) <- colnames(data)
    rownames(rr) <- rdrp_contigs[rdrp_contigs %in% colnames(data1)]
    colnames(rr) <- colnames(data)
    return(list(r = rr,p = pp))
  }else{
    return (NULL)
  }
}

cor <- cor_construct(data_t,rdrp_contigs,20)
cor.r <- as.data.frame(cor$r)
cor.p <- as.data.frame(cor$p)

write.csv(cor.r,paste0("cor.r.1.csv"),quote = FALSE,col.names = TRUE,row.names = TRUE)
write.csv(cor.p,paste0("cor.p.1.csv"),quote = FALSE,col.names = TRUE,row.names = TRUE) 

