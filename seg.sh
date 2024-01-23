#!/bin/bash

path=/home/liuxue/data/ceshi
cd $path

source activate segment


/home/liuxue/data/ceshi/segment_find-2023-9-16.sh --indata /home/liuxue/data/ceshi/data  --taxidDB /home/liuxue/software/prot.accession2taxid --nt_noViruses /home/liuxue/database/NT-novirus/nt_noViruses-2023-5-8/nt_noViruses --nt /home/liuxue/software/nt/nt_20221015/nt  --thread 20 --datatype 2  --method salmon --preprocess true  --assemble spades  --nr /home/liuxue/database/NR/nr --only_rdrp_find 1


for file in `cat list`;
do
/home/liuxue/data/ceshi/segment_find-2023-9-16.sh --indata /home/liuxue/data/ceshi/data  --taxidDB /home/liuxue/software/prot.accession2taxid --nt_noViruses /home/liuxue/database/NT-novirus/nt_noViruses-2023-5-8/nt_noViruses --nt /home/liuxue/software/nt/nt_20221015/nt  --thread 20 --datatype 2 --cor 0.8 --library_ID $file --method salmon --nr /home/liuxue/database/NR/nr 

done
conda deactivate
