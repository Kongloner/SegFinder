## NCBI Nucleotide database (nt) wihtout viruses
The following are the steps to construct non-viral nt database.


Tools Requirements: [`BLAST+`](https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/) 

---


## Download and configure from scratch an nt database that does not contain virus sequences.


### Step 1.1 Download the pre-indexed NCBI BLAST non-viral nt database

```shell

mkdir NT
cd NT
# Eukaryota nt
wget https://ftp.ncbi.nlm.nih.gov/blast/db/nt_euk-nucl-metadata.json

# nt_euk-nucl.filesList: URL for downloading eukaryotic data
grep "ftp://ftp.ncbi.nlm.nih.gov/blast/db/nt_euk" nt_euk-nucl-metadata.json | sed 's/[[:space:]]*["|,]//g' > nt_euk-nucl.filesList

# downloading, use `aspera` tool rather than `wget` might be faster.
cat nt_euk-nucl.filesList |
while read line;
do
wget -c "$line";
wget -c "$line".md5;
done
```


```shell
# Prokaryota (bacteria and archaea) nt
wget https://ftp.ncbi.nlm.nih.gov/blast/db/nt_prok-nucl-metadata.json

# nt_prok-nucl.filesList: URL for downloading Prokaryota data
grep "ftp://ftp.ncbi.nlm.nih.gov/blast/db/nt_prok" nt_prok-nucl-metadata.json |sed 's/[[:space:]]*["|,]//g' > nt_prok-nucl.filesList

# Use `aspera` tool rather than `wget` might be faster.
cat nt_prok-nucl.filesList |
while read line;
do
wget -c "$line";
wget -c "$line".md5;
done
```


`aspera` example :
```shell
for i in {00..108};
do 
ascp -QT -i ~/.aspera/connect/etc/asperaweb_id_dsa.openssh -l 100M -k 1 -T anonftp@ftp.ncbi.nlm.nih.gov:/blast/db/nt_euk."$i".tar.gz ./
done
```
---
### Step 1.2 Check integrity


```shell
md5sum -c *.md5
```
If the all files are ok, then next step, or you need to download again.


---
### Step 1.3 Decompress


```shell
cat nt_prok-nucl.filesList nt_euk-nucl.filesList |
while read line;
do
tar -zxvf "$line";
done

```
### Step 1.4 Aggregate existing nt_prok & nt_euk database


```shell

blastdb_aliastool -dblist "nt_prok nt_euk" -dbtype nucl -out NT/nt_noViruses -title "NT database with only Eukaryota & Prokaryota (bacteria and archaea)" 

```

## Other methods to configure the non-virus NT database
We also provide nt database based taxid non-virus nt database culling script, it can get non-virus nt database relatively easily.

```shell
#download nucl_gb.accession2taxid
cd Seg_DB/accession2taxid
wget -t 0 -c https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_gb.accession2taxid.gz
gunzip -c nucl_gb.accession2taxid.gz > Seg_DB/accession2taxid/nucl_gb.accession2taxid

#download taxdump
mdkir Seg_DB/taxdump
wget -t 0 -c https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz
cd Seg_DB/taxdump
tar -zxvf taxdump.tar.gz

#download ref_viruses_rep_genomes
mkdir Seg_DB/ref_viruses_rep_genomes
cd Seg_DB/ref_viruses_rep_genomes
wget -t 0 -c https://figshare.com/ndownloader/files/46795402
tar -zxvf ref_viruses_rep_genomes.tar.gz

#Handling nt database
SegFinder/bin/nt_novirus.sh -i Seg_DB/nt -o Seg_DB/nt_novirus -t 20 -m 20 --taxonomy-dir Seg_DB/taxdump --virus-ref Seg_DB/ref_viruses_rep_genomes --acc2taxid Seg_DB/accession2taxid/nucl_gb.accession2taxid
```
