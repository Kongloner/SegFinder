rm(list = ls())

cat("Loading of the libraries.... \n")
suppressMessages(library(openxlsx))
suppressMessages(library(dplyr))
suppressMessages(library(tidyr))
suppressMessages(library(data.table))
suppressMessages(library(igraph))
cat("... done ! \n")

#### Abundance correlation clustering result filtering ####
args <- commandArgs(T)
# args[1] <- 0.79  # cor
# args[2] <- 'SRR7102799'
# args[3] <- 0   # TPM
# args[4] <- 50  # rdrp_multi
# args[5] <- 20  # non_rdrp_multi

if (length(args) == 3) {
  args[4] <- 50  # rdrp_multi
  args[5] <- 20  # non_rdrp_multi
} 

p_data <- fread('cor.p.1.csv',header = F,data.table = FALSE)
colnames(p_data) <- p_data[1,]
rownames(p_data) <- p_data[,1]
p_data <- p_data[-1][-1,]

r_data <- fread('cor.r.1.csv',header = F,data.table = FALSE)
colnames(r_data) <- r_data[1,]
rownames(r_data) <- r_data[,1]
r_data <- r_data[-1][-1,]

contigs <- colnames(p_data)
p_data <- as.data.frame(lapply(p_data, as.numeric))
r_data <- as.data.frame(lapply(r_data, as.numeric))
p_data <- ifelse(p_data < 0.05,1,0)
r_data <- ifelse(r_data > as.numeric(args[1]),1,0)

data <- p_data*r_data
data <- apply(data,2,sum)
index <- which(data >= 1)

if(length(index) > 1){
  rsem <- fread('RSEM_rdrp.csv',header = F,data.table = FALSE)
  colnames(rsem) <- rsem[1,]
  rsem <- rsem[-1,]
  colnames(rsem)[1] <- 'Name'
  # length(unique(rsem$transcript_id.s.)) == nrow(rsem)
  cor_contigs_TPM <- as.data.frame(t(rsem[which(rsem$Name %in% contigs[index]),]))
  colname <- as.data.frame(t(cor_contigs_TPM))$Name
  colnames(cor_contigs_TPM) <- colname
  cor_contigs_TPM <- cor_contigs_TPM[-1,]
  # str(cor_contigs_TPM[1,1])
  cor_contigs_TPM <- as.data.frame(lapply(cor_contigs_TPM,as.numeric))
  cor_contigs_TPM <- ifelse(cor_contigs_TPM > 0,1,0)
  confidence <- as.data.frame(colSums(cor_contigs_TPM))
  colnames(confidence) <- 'Frequency'
  rownames(confidence) <- colname
  
  
  ### add sequences length and is it cutted (true or false)
  seq_length <- fread('re.fasta_length.txt',sep = '\t')
  seq_length <- seq_length[which(seq_length$V1 %in% rownames(confidence)),]
  seq_length <- seq_length[!duplicated(seq_length$V1),]
  # all(seq_length$V1 == rownames(confidence))
  confidence[['real_length']] <- seq_length$V2
  confidence[['cutted']] <- seq_length$V3
  
  
  ### add RdRp(yes/no)
  RdRp_blastx <- fread(paste0(args[2],".megahit.fa.rdrp.tsv"),sep = '\t',header = F,data.table = FALSE)
  RdRp_blastx <- RdRp_blastx[which(RdRp_blastx$V1 %in% rownames(confidence)),]
  RdRp_blastx <- RdRp_blastx[!duplicated(RdRp_blastx$V1),]
  confidence[['RdRp(yes/no)']] <- 'no'
  confidence[RdRp_blastx$V1,]$`RdRp(yes/no)` <- 'yes'
  
  ### add RdRp_blastx
  RdRp_contig_Ordered <- rownames(confidence)[which(confidence$`RdRp(yes/no)` == 'yes')]
  RdRp_blastx$V1 <- factor(RdRp_blastx$V1,levels = RdRp_contig_Ordered)
  RdRp_blastx <- RdRp_blastx[order(RdRp_blastx$V1),]
  # all(RdRp_blastx$V1 == RdRp_contig_Ordered)
  
  confidence$RdRp_blastx <- ''
  confidence[RdRp_contig_Ordered,]$RdRp_blastx <- RdRp_blastx$V3
  confidence$RdRp_identity <- ''
  confidence[RdRp_contig_Ordered,]$RdRp_identity <- RdRp_blastx$V5
  
  ### add NR_blastx
  # NR_blastx <- read.table(paste0(args[2],"_megahit_assemble_nr.tsv"),header = F,sep = "\t",quote = '')
  NR_blastx <- fread(paste0(args[2],"_megahit_assemble_nr.tsv"),sep = '\t',header = F,data.table = FALSE)
  NR_blastx$V4 <- apply(NR_blastx,1,function(x,c1,c2){ gsub(paste0(x[c1],' '),'',x[c2],fixed = TRUE) },"V3",'V4')
  NR_blastx <- NR_blastx[which(NR_blastx$V1 %in% rownames(confidence)),]
  NR_blastx <- NR_blastx[!duplicated(NR_blastx$V1),]
  
  NR_contig_Ordered <- rownames(confidence)[which(rownames(confidence) %in% NR_blastx$V1)]
  NR_blastx$V1 <- factor(NR_blastx$V1,levels = NR_contig_Ordered)
  NR_blastx <- NR_blastx[order(NR_blastx$V1),]
  confidence$NR_blastx <- ''
  confidence[NR_contig_Ordered,]$NR_blastx <- NR_blastx$V4
  confidence$NR_identity <- ''
  confidence[NR_contig_Ordered,]$NR_identity <- NR_blastx$V5
  confidence$NR_sstart <- ''
  confidence[NR_contig_Ordered,]$NR_sstart <- NR_blastx[,ncol(NR_blastx)-1]
  confidence$NR_send <- ''
  confidence[NR_contig_Ordered,]$NR_send <- NR_blastx[,ncol(NR_blastx)]
  
  
  ### add nt_blast
  # NT_blast <- read.table(paste0(args[2],"_megahit_assemble_re_nt.tsv"),header = F,sep = "\t",quote = "")
  NT_blast <- fread(paste0(args[2],"_megahit_assemble_re_nt.tsv"),sep = '\t',header = F,data.table = FALSE)
  # NT_blastx$V4 <- apply(NT_blastx,1,function(x,c1,c2){ gsub(paste0(x[c1],' '),'',x[c2]) },"V3",'V4')
  NT_blast <- NT_blast[which(NT_blast$V1 %in% rownames(confidence)),]
  NT_blast <- NT_blast[!duplicated(NT_blast$V1),]
  
  NT_contig_Ordered <- rownames(confidence)[which(rownames(confidence) %in% NT_blast$V1)]
  NT_blast$V1 <- factor(NT_blast$V1,levels = NT_contig_Ordered)
  NT_blast <- NT_blast[order(NT_blast$V1),]
  confidence$NT_blast <- ''
  confidence[NT_contig_Ordered,]$NT_blast <- NT_blast$V4
  confidence$NT_identity <- ''
  confidence[NT_contig_Ordered,]$NT_identity <- NT_blast$V5
  confidence$NT_sstart <- ''
  confidence[NT_contig_Ordered,]$NT_sstart <- NT_blast[,ncol(NT_blast)-1]
  confidence$NT_send <- ''
  confidence[NT_contig_Ordered,]$NT_send <- NT_blast[,ncol(NT_blast)]
  
  
  ### add TPM
  TPM <- fread('RSEM_rdrp.csv',header = F,data.table = FALSE)
  colnames(TPM) <- TPM[1,]
  TPM <- TPM[-1,]
  TPM <- TPM[which(TPM$Name %in% rownames(confidence)),]
  
  TPM_contigs_ordered <- rownames(confidence)
  TPM[1] <- factor(TPM[,1],levels = TPM_contigs_ordered)
  TPM <- TPM[order(TPM[,1]),]
  confidence$TPM <- TPM[[args[2]]]
  
  ### add cluster
  cluster <- fread('cor.r.1.csv',header = F,data.table = FALSE)
  # cluster <- read.csv('cor.r.1.csv',header = F)
  cluster[1,1] <- 'contig'
  colnames(cluster) <- cluster[1,]
  cluster <- cluster[-1,]
  rownames(cluster) <- cluster[,1]
  cluster <- cluster[-1]
  cluster <- cluster[which(rownames(cluster) %in% rownames(confidence)),]
  cluster <- cluster[which(colnames(cluster) %in% rownames(confidence))]
  cluster1 <- cluster
  
  cluster$node1 = rownames(cluster)
  cluster <- pivot_longer(cluster, cols = -node1, names_to = "node2", values_to = "value")
  cluster$value <- abs(as.numeric(cluster$value))
  cluster <- cluster %>%
    filter(value >= as.numeric(args[1]),node1 != node2)
  
  # rdrp_contigs <- unique(cluster$node1)
  rdrp_contigs <- rownames(cluster1)
  data <- cluster1[rdrp_contigs,][rdrp_contigs]
  row_names <- rownames(data)
  col_names <- colnames(data) 
  data <- data.frame(apply(data, 2, as.numeric))
  rownames(data) <- row_names
  colnames(data) <- col_names
  rdrp_cluster <- list()
  for(i in 1:length(rdrp_contigs)){
    rdrp_cluster[[i]] <- unique(c(rdrp_contigs[i],rdrp_contigs[which(data[rdrp_contigs[i],] > as.numeric(args[1]))]))
  }
  
  result <- list()
  
  # Iterate through each vector in rdrp_cluster
  while(length(rdrp_cluster) > 0) {
    # Extract the first vector from rdrp_cluster
    currentVector <- unlist(rdrp_cluster[1])
    # Remove the first vector from rdrp_cluster
    rdrp_cluster <- rdrp_cluster[-1]
    # Check if currentVector overlaps with any vector in result
    overlap <- sapply(result, function(x) any(x %in% currentVector))
    #print(overlap)
    # If there is overlap, merge the vectors
    if (any(overlap)) {
      currentVector <- unique(c(currentVector, unlist(result[overlap])))
      result <- result[!overlap]
    }
    # Add the merged vector to result
    result <- c(result, list(currentVector))
  }
  
  
  confidence <- confidence[unique(c(cluster$node1,cluster$node2)),]
  cluster.label <- rownames(confidence)
  
  for (i in seq_along(result)) {
    # Mark all nodes in the current cluster as belonging to the current cluster
    cluster_nodes <- unique(c(result[[i]], cluster[which(cluster$node1 %in% result[[i]]),]$node2))
    cluster.label[cluster.label %in% cluster_nodes] <- paste0('cluster', i)
  }
  
  label <- unique(cluster.label)
  for(i in 1:length(label)){
    cluster.label <- gsub(paste0("^",label[i],"$"), paste0('cluster_',i), cluster.label)
  }
  confidence$cluster <- cluster.label
  confidence <- confidence[order(confidence$cluster),]
  
  
  # # remove the cluster with only 1 contig
  # clusters_contigs_num <-  aggregate(confidence$cluster,by = list(cluster = confidence$cluster),length)
  # retain_contigs <- clusters_contigs_num[which(clusters_contigs_num$x > 1),]$cluster
  # confidence <- confidence[which(confidence$cluster %in% retain_contigs),]
  
  
  confidence1 <- confidence[confidence$`RdRp(yes/no)` == 'yes',]
  confidence1$`RdRp(yes/no)` <- paste0(confidence1$`RdRp(yes/no)`,'_',confidence1$cluster)
  confidence1 <- confidence1[!duplicated(confidence1$`RdRp(yes/no)`),]
  cor <- fread('cor.r.1.csv',header = F,data.table = FALSE)
  cor[1,1] <- 'contig'
  colnames(cor) <- cor[1,]
  cor <- cor[-1,]
  rownames(cor) <- cor[,1]
  cor <- cor[-1]
  
  confidence$cor <- ''
  confidence[rownames(confidence1),]$cor <- '*'
  
  for (i in seq_len(nrow(confidence1))) {
    idx <- which(confidence$cluster == confidence1$cluster[i] & !rownames(confidence) %in% rownames(confidence1)[i])
    confidence[idx, 'cor'] <- unlist(cor[rownames(confidence1)[i], rownames(confidence[idx,])])
  }
  
  ### search clusters without RdRp
  confidence1 <- confidence[which(confidence$`RdRp(yes/no)` == 'yes'),]
  rdrp_cluster <- unique(confidence1$cluster)
  to_remove_clusters <- setdiff(unique(confidence$cluster),rdrp_cluster)
  if(length(to_remove_clusters) > 0)
  {
    confidence <- confidence[-which(confidence$cluster %in% to_remove_clusters),]
  }else{
    confidence <- confidence
  }
  confidence1 <- confidence
  colnames(confidence1) <-   c('Frequency', 'Contig_length', 'cutted', 'RdRP',
                              'RdRP_blastx_hits', 'RdRP_identity', 'nr_blastx_hits', 'nr_identity', 'NR_sstart',
                              'NR_send', 'nt_blast_hits', 'nt_identity', 'NT_sstart', 'NT_send', 'TPM',
                              'Cluster', 'Correlation')
  write.xlsx(confidence1,file = paste0(args[2],'.pre.confidence_table.xlsx'),rowNames = T)
  
  if(nrow(confidence) > 0)
  {
    ### search clusters with more than 1 non_virus(NR_identity > 30%)
    confidence1 <- confidence
    virus_to_remove <- 'Virus|virus|Viruses|viruses|Phage|phage|Riboviria'
    confidence_to_removeCluster <- confidence1[confidence1$NR_blastx != '',]
    confidence_to_removeCluster$NR_identity <- as.numeric(confidence_to_removeCluster$NR_identity)
    confidence_to_removeCluster <- confidence_to_removeCluster[confidence_to_removeCluster$NR_identity > 30,]
    if(nrow(confidence_to_removeCluster) > 0){
      confidence_to_removeCluster <- confidence_to_removeCluster[!grepl(virus_to_remove,confidence_to_removeCluster$NR_blastx),]
      if(nrow(confidence_to_removeCluster) > 0){
        confidence_to_removeCluster <- aggregate(confidence_to_removeCluster$cluster,by = list(cluster = confidence_to_removeCluster$cluster),length)
        confidence_to_removeCluster <- confidence_to_removeCluster[which(confidence_to_removeCluster$x >= 1),]
        to_remove_clusters <- confidence_to_removeCluster$cluster
        if(length(to_remove_clusters) > 0){
          confidence <- confidence[-which(confidence$cluster %in% to_remove_clusters),]
        }
      }
    }
  }
  
  confidence1 <- confidence
  if(nrow(confidence1) > 0){
    ### ### search clusters with  more than 2 different RdRps
    confidence1 <- confidence1[which(confidence1$`RdRp(yes/no)` == 'yes'),]
    if(nrow(confidence1) > 0){
      confidence1$NR_blastx <- paste0(confidence1$NR_blastx,'_',confidence1$NR_identity)
      cluster_RdRp_num <- aggregate(confidence1$cluster,by = list(cluster = confidence1$cluster),length)
      cluster_RdRp_num <- cluster_RdRp_num[which(cluster_RdRp_num$x > 1),] # choose cluster with more than 1 rdrp_contigs
      if(nrow(cluster_RdRp_num) > 0){
        confidence1 <- confidence1[which(confidence1$cluster %in% cluster_RdRp_num$cluster),]
        confidence1$NR_blastx <- paste0(confidence1$NR_blastx,'_',confidence1$cluster)
        confidence1 <- confidence1[!duplicated(confidence1$NR_blastx),]
        cluster <- aggregate(confidence1$cluster,by = list(cluster = confidence1$cluster),length)
        cluster <- cluster[which(cluster$x > 1),]
        if(nrow(cluster) > 0){
          to_remove_clusters <- cluster$cluster
          confidence <- confidence[-which(confidence$cluster %in% to_remove_clusters),]
        }
      }
    }
  }
  
  if(nrow(confidence) > 0){
    #### remove the cluster whose contigs  are all rdrps
    to_remove_clusters <- vector()
    confidence1 <- confidence
    confidence1$`RdRp(yes/no)` <- paste0(confidence1$`RdRp(yes/no)`,'_',confidence1$cluster)
    confidence1 <- confidence1[!duplicated(confidence1$`RdRp(yes/no)`),]
    cluster <- aggregate(confidence1$cluster,by = list(cluster = confidence1$cluster),length)
    cluster <- cluster[which(cluster$x == 1),] # choose the cluster whose contigs are all rdrps(or no_rdrps)
    if(nrow(cluster) > 0){
      confidence1 <- confidence[which(confidence$cluster %in% cluster$cluster),]
      confidence1 <- confidence1[which(confidence1$`RdRp(yes/no)` == 'yes'),] # choose the cluster whose contigs are all rdrps
      if(nrow(confidence1) > 0){
        to_remove_clusters <- unique(confidence1$cluster)
        confidence <- confidence[-which(confidence$cluster %in% to_remove_clusters),]
      }
    }
    
    if(nrow(confidence) > 0){
      ### remove the clusters which exists the contigs that they and their re_assemble contigs all meet the condition(multi < threshold value)
      contigs_name <- rownames(confidence)
      rdrp <- which(confidence$`RdRp(yes/no)` == 'yes')
      non_rdrp <- setdiff(1:length(contigs_name),rdrp)
      contigs_name <- as.numeric(gsub(".*(cov|multi)_([0-9.]+).*", "\\2", contigs_name))
      
      # contigs_name <- ifelse(contigs_name > as.numeric(args[3]),1,0)
      contigs_name[rdrp] <- ifelse(contigs_name[rdrp] > as.numeric(args[4]),1,0)
      contigs_name[non_rdrp] <- ifelse(contigs_name[non_rdrp] > as.numeric(args[5]),1,0)
      multi_row <- which(contigs_name == 0)
      to_remove_clusters <- unique(confidence[multi_row,]$cluster)
      if(length(to_remove_clusters) > 0)
      {
        confidence <- confidence[-which(confidence$cluster %in% to_remove_clusters),]
      }
    }
  }
  
  if(nrow(confidence) > 0){
    confidence1 <- confidence[confidence$`RdRp(yes/no)` == 'yes',]
    confidence1$`RdRp(yes/no)` <- paste0(confidence1$`RdRp(yes/no)`,'_',confidence1$cluster)
    confidence1 <- confidence1[!duplicated(confidence1$`RdRp(yes/no)`),]
    cor <- fread('cor.r.1.csv',header = F,data.table = FALSE)
    cor[1,1] <- 'contig'
    colnames(cor) <- cor[1,]
    cor <- cor[-1,]
    rownames(cor) <- cor[,1]
    cor <- cor[-1]
    
    confidence$cor <- ''
    confidence[rownames(confidence1),]$cor <- '*'
    
    for (i in seq_len(nrow(confidence1))) {
      idx <- which(confidence$cluster == confidence1$cluster[i] & !rownames(confidence) %in% rownames(confidence1)[i])
      confidence[idx, 'cor'] <- unlist(cor[rownames(confidence1)[i], rownames(confidence[idx,])])
    }
  }
  
  ### remove the cluster which has contigs whose TPM < threshold 
  if(nrow(confidence) > 0){
    confidence1 <- confidence
    confidence1$TPM <- as.numeric(confidence1$TPM)
    confidence1 <- confidence1[confidence1$TPM < as.numeric(args[3]),] 
    if(nrow(confidence1) > 0){
      remove_clusters <- unique(confidence1$cluster)
      confidence <- confidence[!confidence$cluster %in% remove_clusters,]
    }
  }
  
  ### remove the cluster which has contigs whose Frequency < 3
  if(nrow(confidence) > 0){
    confidence1 <- confidence
    confidence1$Frequency <- as.numeric(confidence1$Frequency)
    confidence1 <- confidence1[confidence1$Frequency < 3,]
    if(nrow(confidence1) > 0){
      remove_clusters <- unique(confidence1$cluster)
      confidence <- confidence[!confidence$cluster %in% remove_clusters,]
    }
  }
  colnames(confidence) <-   c('Frequency', 'Contig_length', 'cutted', 'RdRP',
                               'RdRP_blastx_hits', 'RdRP_identity', 'nr_blastx_hits', 'nr_identity', 'NR_sstart',
                               'NR_send', 'nt_blast_hits', 'nt_identity', 'NT_sstart', 'NT_send', 'TPM',
                               'Cluster', 'Correlation')
  write.xlsx(confidence,file = paste0(args[2],'.final.confidence_table.xlsx'),rowNames = T)
  write.table(rownames(confidence),file = "Cor_contigs.txt",row.names = F,col.names = F,quote = F,sep = ',')
  
 #### draw a correlation clustering network graph.  
  # cor.r <- read.table("cor.r.1.csv",sep = ",",header=T,row.names = 1,check.names = F)
  cor.r <- fread('cor.r.1.csv',header=T,data.table = FALSE)
  rownames(cor.r) <- cor.r[,1]
  cor.r <- cor.r[-1]
  
  # cor.p <- read.table("cor.p.1.csv",sep = ",",header=T,row.names = 1,check.names = F)
  cor.p <- fread('cor.p.1.csv',header=T,data.table = FALSE)
  rownames(cor.p) <- cor.p[,1]
  cor.p <- cor.p[-1]
  
  cor.r$node1 = rownames(cor.r) 
  cor.p$node1 = rownames(cor.p)
  # Convert data to long format for filtering. Node and link data needed for drawing network graphs can be formatted at this step
  r = cor.r %>% 
    gather(key = "node2", value = "r", -node1) %>%
    data.frame()
  p = cor.p %>% 
    gather(key = "node2", value = "p", -node1) %>%
    data.frame()
  
  # Merge r and p values into one data table
  cor.data <- merge(r,p,by=c("node1","node2"))
  # cor.data
  # Retain relationships between variables with p <= 0.05 and abs(r) >= args[1], and add network attributes
  cor.data <- cor.data %>%
    filter(abs(r) >= as.numeric(args[1]), p <= 0.05, node1 != node2) %>%
    mutate(
      linetype = ifelse(r > 0,"positive","negative"), # Set link line properties, can be used to set line type and color
      linesize = abs(r) # Set link line width.
    ) # This output still has duplicate links, further removal is needed later
  #head(cor.data)
  
  # select the contigs which appear in the final.confidence_table
  cor.data <- cor.data[which(cor.data$node1 %in% rownames(confidence)),]
  cor.data <- cor.data[which(cor.data$node2 %in% rownames(confidence)),]
  
  if(nrow(cor.data) > 0){
    c(as.character(cor.data$node1),as.character(cor.data$node2)) %>%
      as_tibble() %>%
      group_by(value) %>%
      summarize(n=n()) -> vertices
      colnames(vertices) <- c("node", "n")
    
    # Construct graph structure data
    g <- graph_from_data_frame(cor.data, vertices = vertices, directed = FALSE )
    #g
    
   # is.simple(g) # Not a simple graph, link count will be high, so need to convert to a simple graph
    E(g)$weight <- 1
    g <- igraph::simplify(g,
                          remove.multiple = TRUE,
                          remove.loops = TRUE,
                          edge.attr.comb = "first")
    
    #g
    #g <- delete.vertices(g,which(degree(g) == 0)) # Remove isolated points
    E(g)$weight <- 1
    
    # Calculate node link count
    V(g)$degree <- degree(g)
    
    # write.graph(g,file = "all.gml",format="gml") 
    net.data  <- igraph::as_data_frame(g, what = "both")$edges # Extract link properties
    # write.csv(net.data,"net.data.csv",quote = FALSE,col.names = NA,row.names = FALSE) 
    head(net.data)
    vertices  <- igraph::as_data_frame(g, what = "both")$vertices # Extract node properties
    # write.csv(vertices,"vertices.csv",quote = FALSE,col.names = NA,row.names = FALSE)
 
    # Prepare network graph layout data
    layout1 <- layout_in_circle(g) # Radial layout is suitable for data with fewer nodes.
    layout2 <- layout_with_fr(g) # fr layout.
    layout3 <- layout_on_grid(g)  # grid layout.
    #head(layout1)
    
    # Set drawing colors
    # Set node and group background colors
    degree_levels <- unique(V(g)$degree)
    color <- colorRampPalette(c("red", "yellow", "green"))(length(degree_levels))
    names(color) <- degree_levels
    V(g)$point.col <- color[match(V(g)$degree, names(color))]
    
    E(g)$color <- ifelse(E(g)$linetype == "positive","red",rgb(0,147,0,maxColorValue = 255))
    ceb <- cluster_edge_betweenness(g)
    
    ### Draw fr layout network graph - without adding background color
    pdf(paste0(args[2],".network_group_fr.pdf"),family = "Times",width = 10,height = 12)
    par(mar=c(5,2,1,2))
    plot(ceb, g, layout=layout2,
         vertex.color=V(g)$point.col,
         vertex.frame.color ="black",
         vertex.label=g$name,
         vertex.label.cex=0.8,
         vertex.label.col="black",
         edge.arrow.size=0.5,
         edge.width=abs(E(g)$r)*2,
         edge.curved = TRUE
    )
    
    # Add the first legend for the edge width representing |r-value|
    legend(
      title = "|r-value|",
      x = min(layout2[,1])+0.4,  # Adjust the x-position
      y = min(layout2[,2])-0.17, # Adjust the y-position
      legend = c(as.numeric(args[1]), 1.0),
      col = "black",
      lty = 1,
      lwd = c(as.numeric(args[1]), 1.0)*2
    )
    
    # Add the second legend for Correlation type
    # legend(
    #   title = "Correlation (??)",
    #   list(x = min(layout2[,1])+0.8,  # Adjust the x-position
    #   y = min(layout2[,2])-0.17), # Adjust the y-position
    #   legend = c("Positive", "Negative"),  # Add appropriate labels
    #   col = c("red", rgb(0,147,0,maxColorValue = 255)), # Colors for positive and negative correlations
    #   lty = 1,
    #   lwd = 1
    # )
    dev.off()
    
  }else{
    cat('cannot create network plot!')
  }
}else{
  cat('cannot find any other contigs correlated to the contig that you have inputted!\n')
}

 
