import os
import sys
import pandas as pd
from Bio import SeqIO


def extract_nucleotides():
    print("🧬 Extracting nucleotide sequences for top candidates...")

    # Define exact input files based on your directory
    csv_file = "official_top10_table_PUBLICATION_READY.csv"
    fasta_db = "genes_nucleotide.fasta"  # FASTA file in your directory
    output_fasta = "top_candidates_nucleotide.fasta"

    # 1. Verify CSV exists
    if not os.path.exists(csv_file):
        print(f"❌ ERROR: Candidate CSV file '{csv_file}' not found!")
        sys.exit(1)

    # 2. Read candidate Accession/Gene IDs from CSV
    try:
        df = pd.read_csv(csv_file)
        # Try common column names for target sequence/gene IDs
        id_col = None
        for col in [
            "Accession",
            "Target_ID",
            "Gene_ID",
            "transcript_id",
            "Sequence_ID",
            "Target",
        ]:
            if col in df.columns:
                id_col = col
                break

        if not id_col:
            # Default to the first column if specific name not found
            id_col = df.columns[0]

        target_ids = set(df[id_col].dropna().astype(str).str.strip())
        print(
            f"[i] Found {len(target_ids)} target IDs in column '{id_col}'."
        )

    except Exception as e:
        print(f"❌ ERROR reading CSV: {e}")
        sys.exit(1)

    # 3. Extract sequences from the local FASTA file
    if not os.path.exists(fasta_db):
        print(
            f"❌ ERROR: Sequence database '{fasta_db}' not found in folder!"
        )
        sys.exit(1)

    extracted_records = []
    print(f"[⚙] Searching '{fasta_db}' for candidates...")

    for record in SeqIO.parse(fasta_db, "fasta"):
        # Match transcript ID against header ID or accession
        if any(tid in record.id for tid in target_ids):
            extracted_records.append(record)

    if not extracted_records:
        print("❌ ERROR: No matching sequences were found in FASTA!")
        sys.exit(1)

    # 4. Save to top_candidates_nucleotide.fasta
    SeqIO.write(extracted_records, output_fasta, "fasta")
    print(
        f"✔ Successfully wrote {len(extracted_records)} candidate sequences to '{output_fasta}'"
    )


if __name__ == "__main__":
    extract_nucleotides()