## NCBI Non-Redundant Nucleotide Database (NR)

We use BLAST for nucleotide sequence alignment.

There are two methods to construct the necessary NT database for use with BLAST.

Here, we provide two ways to download the NT database, though other methods are also available.

The files are large and download times may vary depending on your network speed.


### 1. From the sequences

  - **1.1 Download the sequence file.**
    ```shell
    mkdir -p NT && cd NT
    wget -c https://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nt.gz
  
    wget -c https://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nt.gz.md5
    ```

  - **1.2 Check for the file integrity.**
    ```shell
    md5sum -c nt.gz.md5
    ```
      If the result is ok, then next step

  - **1.3 Using makeblastdb to build the index.**
    ```shell
    makeblastdb -in nt.gz -dbtype nucl -out NT/nt
    ```

### 2. From the pre-builded BLAST index

  - **2.1 Download the index file.**

     These indexes are constructed from multiple files, currently numbered from 00 to 99, and possibly more in the future (from nt.00.tar.gz to nt.99.tar.gz).

      ```shell
      mkdir NT
      cd NT
      
      for i in $(seq -w 000 155); 
        do
          base_url="https://ftp.ncbi.nlm.nih.gov/blast/db/nt.$i"
          tar_url="$base_url.tar.gz"
          md5_url="$tar_url.md5"
      
          wget $tar_url
          wget $md5_url
        done
      ```


  - **2.2 Check for the file integrity.**
    ```shell
    for i in $(seq -w 000 155); 
     do
       md5_path="nt.$i.tar.gz.md5"
       md5sum -c "$md5_path"
    done
    ```
    If the results is ok, then next step

  - **2.3 Unzip the files.**
    ```shell
    for i in $(seq -w 000 155); 
     do
        index_path="nt.$i.tar.gz"
        tar -zxvf "$index_path" -C NT
     done
    ```



