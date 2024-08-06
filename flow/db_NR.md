## NCBI Non-Redundant Protein Database (NR)

We use diamond for protein sequence alignment.

There are two methods to construct the necessary NR database for use with DIAMOND.

Here, we provide two ways to download the NR database, though other methods are also available.

The files are large and download times may vary depending on your network speed.


### 1. From the sequences

  - **1.1 Download the sequence file.**
    ```shell
      mkdir NR
      cd NR
      wget -c https://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nr.gz

      wget -c https://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nr.gz.md5
    ```

  - **1.2 Check for the file integrity.**
    ```shell
      md5sum -c nr.gz.md5
    ```
      If the result is ok, then next step

  - **1.3 Using ***[diamond](https://github.com/bbuchfink/diamond)*** to build the index.**
    ```shell
      diamond makedb --in nr.gz -d NR/nr
    ```

### 2. From the pre-builded BLAST index

  - **2.1 Download the index file.**

     These indexes are constructed from multiple files, currently numbered from 00 to 97, and possibly more in the future.(from `nr.00.tar.gz` to `nr.97.tar.gz`)

      ```shell
      mkdir NR
      cd NR

      for i in {00..99}; 
        do
          base_url="https://ftp.ncbi.nlm.nih.gov/blast/db/nr.$i"
          tar_url="$base_url.tar.gz"
          md5_url="$tar_url.md5"

          wget $tar_url
          wget $md5_url
        done

      ```


  - **2.2 Check for the file integrity.**
    ```shell
    for i in {00..99}; 
      do
        md5_path="nr.$i.tar.gz.md5"
        md5sum -c "$md5_path"
      done
    ```
    If the results is ok, then next step

  - **2.3 Unzip the files.**
    ```shell
    for i in {00..99}; 
      do
        index_path="nr.$i.tar.gz"
        tar -zxvf "$index_path" -C NR
      done
    ```

  - **2.4 Rebuild the indexes.**
    
    **Note:**
  To use the ***prepdb*** command, you need to install [diamond](https://github.com/bbuchfink/diamond/releases) from its GitHub repository instead of using the Conda installation.
      
      ```shell
      diamond prepdb -d NR/nr
      ```


