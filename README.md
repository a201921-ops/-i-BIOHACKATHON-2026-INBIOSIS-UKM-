# PLANTASTIC - Metisa plana Target Mining Pipeline 
> An integrated bioinformatic pipeline for target gene selection, dsRNA construct engineering, host off-target ecotoxicity screening (*Elaeis guineensis*), and qPCR primer design.

1. INSTALLATION & ENVIRONMENT SETUP
--------------------------------------------------------------------------------
Clone or download this repository, navigate to the notebook folder, and 
initialize the Conda environment:

# Navigate to the workspace directory
cd PLANTASTIC/notebook

# Create the Conda environment from environment.yml
conda env create -f environment.yml

# Activate the environment
conda activate metisa_rnai_pipeline


2. PREREQUISITES & DATA SETUP
--------------------------------------------------------------------------------
Due to file size limits, large input FASTA datasets (.fasta) and local database 
files are excluded from the main repository. Before executing the pipeline, 
place your sequence files into the following directories:

* Proteome Dataset (Phase 1):
  Place 'proteins_longest_isoform.fasta' into the 'pipelineA/' directory.

* Transcriptome Assembly (Phase 2):
  Place 'genes_nucleotide.fasta' into the 'pipelineB/' directory.

* Reference Databases:
  Run the built-in database fetch scripts if you need to download remote assemblies:

  # Retrieve reference target databases
  python pipelineA/download_databases.py

  # Fetch and index the Elaeis guineensis genome assembly
  python pipelineB/download_oil_palm_db.py


3. PIPELINE EXECUTION
--------------------------------------------------------------------------------
Once all input FASTA files are placed in their respective directories, execute 
the master pipeline end-to-end:

python run_complete_pipeline.py


4. REPOSITORY STRUCTURE
--------------------------------------------------------------------------------
notebook/
|-- run_complete_pipeline.py              # Master script (Executes Phase 1 -> Bridges data -> Phase 2)
|
|-- pipelineA/                            # Phase 1: Target Mining & Candidate Ranking
|   |-- diamond.exe                       # Local DIAMOND alignment tool
|   |-- proteins_longest_isoform.fasta    # Input translated proteome dataset (Add manually)
|   |-- download_databases.py             # Script to fetch reference DBs
|   |-- target_families.py                # Curation of IRAC-aligned lethal gene families
|   |-- qc_phase2.py                      # Structural integrity & quality control audit
|   |-- screen_contaminants.py            # Contamination & host/microbial filtering
|   |-- phase3_mine_targets.py            # DIAMOND / BLASTp orthology searching
|   |-- phase3_refine_subfamilies.py      # Subfamily refinement & catalytic domain checks
|   |-- build_official_top10_table.py     # Filters & formats top 10 prioritized targets
|   |-- run_pipelineA.py                  # Module execution wrapper for Phase 1
|   `-- results/                          # Phase 1 output directory
|
`-- pipelineB/                            # Phase 2: Construct Design & Host Ecotoxicity Check
    |-- genes_nucleotide.fasta            # Input nucleotide transcriptome assembly (Add manually)
    |-- download_oil_palm_db.py           # Fetches & builds E. guineensis BLAST database
    |-- extract_candidate_nucleotides.py  # Pulls mature CDS for candidate genes
    |-- design_rnai_constructs.py         # Engineers 200-500 bp dsRNA region triggers
    |-- run_offtarget_check.py            # Local BLASTn ecotoxicity check (0 continuous 19-bp matches)
    |-- design_qpcr_primers.py            # Generates verification qPCR primer sets
    |-- build_final_master_table.py       # Merges Phase 1 & 2 into final publication data
    |-- run_pipelineB.py                  # Module execution wrapper for Phase 2
    |-- oil_palm_db/                      # BLAST Index Files (.nhr, .nin, .nsq)
    `-- RNAi & Primer Results/            # Final publication outputs (FINAL_MASTER_PUBLICATION_TABLE)