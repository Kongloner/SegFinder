#!/bin/bash

# Set strict mode
set -e
set -o pipefail

# Error handling
trap 'echo "Error: Script failed at line $LINENO"; exit 1' ERR

# Function to display help information
show_help() {
    cat << EOF
Usage: $(basename $0) [OPTIONS]

Pipeline script for building a non-virus NT database.

Options:
    -h, --help              Display this help message
    -i, --input PATH        Specify the NT database path (required)
    -o, --output PATH       Specify the output directory (required)
    -t, --threads INT       Set the number of threads [Default: 40]
    -m, --max-memory STR    Set the maximum memory usage [Default: 32G]
    --taxonomy-dir PATH     Specify the taxonomy data directory (required)
    --acc2taxid PATH        Specify the accession-to-taxid mapping file path (required)
    --virus-ref PATH        Specify the virus reference database path
    --keep-temp             Retain temporary files
    --debug                 Enable debug mode
EOF
}

# Check if a file exists and is readable
check_file() {
    local file="$1"
    if [ ! -f "$file" ]; then
        echo "Error: File does not exist: $file"
        return 1
    fi
    if [ ! -r "$file" ]; then
        echo "Error: File is not readable: $file"
        return 1
    fi
    return 0
}

# Check if a directory exists and is writable
check_directory() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        echo "Error: Directory does not exist: $dir"
        return 1
    fi
    if [ ! -w "$dir" ]; then
        echo "Error: Directory is not writable: $dir"
        return 1
    fi
    return 0
}

# Parameter validation and initialization function
init() {
    # Set default values
    THREADS=40
    MAX_MEMORY="32G"
    KEEP_TEMP=false
    
    # Validate required parameters
    if [ -z "${NT_DB}" ] || [ -z "${OUTPUT_DIR}" ] || [ -z "${TAXONOMY_DIR}" ] || [ -z "${ACC2TAXID}" ]; then
        echo "Error: Missing required parameters"
        show_help
        exit 1
    fi

    # Check files and directories
    check_file "${NT_DB}" || exit 1
    check_file "${ACC2TAXID}" || exit 1
    check_directory "${TAXONOMY_DIR}" || exit 1
    
    # Create output directory
    mkdir -p "${OUTPUT_DIR}/logs" || {
        echo "Error: Unable to create output directory"
        exit 1
    }
    
    # Set log file
    LOG_FILE="${OUTPUT_DIR}/logs/pipeline_$(date +%Y%m%d_%H%M%S).log"
    exec 1> >(tee "${LOG_FILE}")
    exec 2>&1

    echo "Starting non-virus NT database construction pipeline - $(date)"
    echo "Parameter details:"
    echo "- Input database: ${NT_DB}"
    echo "- Output directory: ${OUTPUT_DIR}"
    echo "- Threads: ${THREADS}"
    echo "- Taxonomy directory: ${TAXONOMY_DIR}"
    echo "- ACC2TAXID file: ${ACC2TAXID}"
    if [ -n "${VIRUS_REF_DB}" ]; then
        echo "- Virus reference database: ${VIRUS_REF_DB}"
    fi
}

# Extract sequence IDs and perform preliminary filtering
extract_and_filter_sequences() {
    echo "Step 1: Extract sequence IDs and perform preliminary filtering"
    cd "${OUTPUT_DIR}" || exit 1
    
    echo "Extracting sequence IDs..."
    seqkit seq -j "${THREADS}" -n "${NT_DB}" > nt.fasta.id || {
        echo "Error: Failed to extract sequence IDs"
        exit 1
    }
    
    echo "Filtering virus-related sequences..."
    grep -v -i -e "virus" -e "viruses" -e "riboviria" -e "phage" -e "viridae" -e "proviral" \
        nt.fasta.id > nt.fasta.id_noVirus || {
        echo "Error: Failed to filter virus sequences"
        exit 1
    }
        
    echo "Extracting accession numbers..."
    sed 's/ /\t/g' ./nt.fasta.id_noVirus | cut -f1 > nt.fasta.id_noVirus_accNum || {
        echo "Error: Failed to extract accession numbers"
        exit 1
    }
}

# Process taxonomy information
process_taxonomy() {
    echo "Step 2: Process taxonomy information"
    
    echo "Retrieving taxid from accession..."
    # Process large files in chunks
    split -l 1000000 nt.fasta.id_noVirus_accNum acc_chunk_
    
    for chunk in acc_chunk_*; do
        grep -F -f "$chunk" -w "${ACC2TAXID}" >> nt.fasta.id_noVirus_accNum_taxid || true
    done
    
    if [ ! -s nt.fasta.id_noVirus_accNum_taxid ]; then
        echo "Error: Failed to retrieve taxid"
        exit 1
    fi
    
    echo "Annotating taxonomy using taxonkit..."
    cut -f3 nt.fasta.id_noVirus_accNum_taxid | sort -u | \
        taxonkit --data-dir "${TAXONOMY_DIR}" lineage | \
        awk '$2>0' | \
        taxonkit --data-dir "${TAXONOMY_DIR}" reformat \
            -f "{k}\t{p}\t{c}\t{o}\t{f}\t{g}\t{s}" -F | \
        cut -f1,3- > nt.fasta.id_noVirus_accNum_taxid_results || {
        echo "Error: Taxonomy annotation failed"
        exit 1
    }
}

# Merge and create the final database
create_final_database() {
    echo "Step 3: Merge and create the final database"
    
    # Ensure output directory exists
    mkdir -p "${OUTPUT_DIR}"
    
    echo "Creating non-virus database..."
    seqtk subseq "${NT_DB}" nt.fasta.id_noVirus_accNum > "${OUTPUT_DIR}/nt_noVirus.fasta" || {
        echo "Error: Failed to create non-virus database"
        exit 1
    }
    
    echo "Creating BLAST database..."
    makeblastdb -in "${OUTPUT_DIR}/nt_noVirus.fasta" \
        -dbtype nucl \
        -out "${OUTPUT_DIR}/nt_noViruses" \
        -parse_seqids || {
        echo "Error: Failed to create BLAST database"
        exit 1
    }
}

# Clean up temporary files
cleanup() {
    if [ "${KEEP_TEMP}" = false ]; then
        echo "Cleaning up temporary files..."
        rm -f nt.fasta.id* acc_chunk_*
    fi
}

# Main function
main() {
    # Parse command-line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help) show_help; exit 0 ;;
            -i|--input) NT_DB="$2"; shift 2 ;;
            -o|--output) OUTPUT_DIR="$2"; shift 2 ;;
            -t|--threads) THREADS="$2"; shift 2 ;;
            -m|--max-memory) MAX_MEMORY="$2"; shift 2 ;;
            --taxonomy-dir) TAXONOMY_DIR="$2"; shift 2 ;;
            --acc2taxid) ACC2TAXID="$2"; shift 2 ;;
            --virus-ref) VIRUS_REF_DB="$2"; shift 2 ;;
            --keep-temp) KEEP_TEMP=true; shift ;;
            --debug) set -x; shift ;;
            *) echo "Error: Unknown option $1"; show_help; exit 1 ;;
        esac
    done
    
    # Initialize
    init
    
    # Execute main steps
    extract_and_filter_sequences
    process_taxonomy
    create_final_database
    
    # Clean up
    cleanup
    
    echo "Pipeline completed - $(date)"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
