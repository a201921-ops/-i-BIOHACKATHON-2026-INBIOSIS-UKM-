#!/usr/bin/env python3
"""
screen_contaminants.py - Phase 2 Step 4: Non-Arthropod Contamination Screening
i-Biohackathon 2026 - Track 2 (Metisa plana)
"""

import sys
from pathlib import Path
import pandas as pd


# Keywords used to categorize taxonomy from species names / titles
TAXA_KEYWORDS = {
    "Arthropoda": [
        "arthropoda", "insecta", "drosophila", "bombyx", "tribolium", 
        "plutella", "apis", "acyrthosiphon", "locusta", "spodoptera", 
        "manduca", "nilaparvata", "helicoverpa", "ceratitis"
    ],
    "Bacteria": ["bacteria", "bacterium", "bacillus", "escherichia", "wolbachia", "pseudomonas", "streptomyces"],
    "Fungi": ["fungi", "fungus", "saccharomyces", "aspergillus", "candida", "neurospora", "metarhizium", "beauveria"],
    "Viruses": ["virus", "phage", "viridae", "nucleopolyhedrovirus"],
    "Viridiplantae (Plants)": ["viridiplantae", "arabidopsis", "oryza", "zea", "triticum", "nicotiana"],
}


def classify_hit(sciname: str, title: str) -> str:
    """Assigns high-level taxonomic category based on scientific name & title."""
    text = f"{str(sciname)} {str(title)}".lower()

    # Check Arthropoda first
    for kw in TAXA_KEYWORDS["Arthropoda"]:
        if kw in text:
            return "Arthropoda"

    # Check non-arthropod contaminant groups
    for group in ["Bacteria", "Fungi", "Viruses", "Viridiplantae (Plants)"]:
        for kw in TAXA_KEYWORDS[group]:
            if kw in text:
                return group

    # Non-arthropod Metazoa vs Other
    if "metazoa" in text or "chordata" in text or "nematoda" in text:
        return "Non-Arthropod Metazoa"
    
    return "Other / Unclassified Eukaryote"


def parse_diamond_hits(hits_tsv: Path) -> pd.DataFrame:
    """Reads DIAMOND output and assigns top hit taxonomy per protein query."""
    cols = ["qseqid", "sseqid", "pident", "length", "evalue", "bitscore", "stitle", "staxids", "sscinames"]
    df = pd.read_csv(hits_tsv, sep="\t", names=cols, comment="#")

    # Drop duplicate queries (keep best bitscore hit)
    df_top = df.sort_values("bitscore", ascending=False).drop_duplicates(subset=["qseqid"]).copy()

    # Classify kingdom
    df_top["tax_group"] = df_top.apply(
        lambda row: classify_hit(row["sscinames"], row["stitle"]), axis=1
    )
    df_top["is_contaminant"] = df_top["tax_group"].isin(["Bacteria", "Fungi", "Viruses", "Viridiplantae (Plants)"])
    
    return df_top


def filter_fasta(input_fasta: Path, output_filtered_fasta: Path, allowed_ids: set):
    """Writes a new FASTA containing ONLY approved (arthropod/unflagged) gene models."""
    kept, skipped = 0, 0
    with open(input_fasta, "r") as in_f, open(output_filtered_fasta, "w") as out_f:
        header, seq = None, []
        for line in in_f:
            line = line.strip()
            if line.startswith(">"):
                if header:
                    seq_id = header.split()[0][1:]
                    if seq_id in allowed_ids:
                        out_f.write(f"{header}\n{''.join(seq)}\n")
                        kept += 1
                    else:
                        skipped += 1
                header = line
                seq = []
            else:
                seq.append(line)
        if header:
            seq_id = header.split()[0][1:]
            if seq_id in allowed_ids:
                out_f.write(f"{header}\n{''.join(seq)}\n")
                kept += 1
            else:
                skipped += 1
                
    print(f"[FASTA Filter] Saved {kept:,} valid models to '{output_filtered_fasta}'. Filtered out {skipped:,} models.")


def main():
    hits_tsv = Path("results/diamond_sprot_hits.tsv")
    clean_fasta = Path("proteins_clean.fasta")
    filtered_fasta = Path("proteins_arthropod_only.fasta")
    summary_csv = Path("results/contamination_screening_summary.csv")

    if not hits_tsv.exists():
        print(f"[Error] DIAMOND results file '{hits_tsv}' not found. Run DIAMOND first!")
        sys.exit(1)

    print(f"Parsing DIAMOND hits from: {hits_tsv}")
    df_hits = parse_diamond_hits(hits_tsv)

    # Calculate statistics
    total_queries = 26490  # Total Metisa plana proteins
    hits_count = len(df_hits)
    no_hits_count = total_queries - hits_count

    print("\n" + "=" * 65)
    print("      STEP 4: CONTAMINATION & TAXONOMY SCREENING SUMMARY      ")
    print("=" * 65)
    
    counts = df_hits["tax_group"].value_counts()
    for grp, cnt in counts.items():
        pct = (cnt / total_queries) * 100
        print(f"  - {grp:<30}: {cnt:>6,} genes ({pct:>5.2f}%)")
    
    print(f"  - No Match / Unannotated        : {no_hits_count:>6,} genes ({(no_hits_count/total_queries)*100:>5.2f}%)")
    print("-" * 65)

    contam_df = df_hits[df_hits["is_contaminant"]]
    total_contam = len(contam_df)
    print(f"Total Non-Arthropod Contaminants Flagged: {total_contam:,} ({(total_contam/total_queries)*100:.2f}%)")
    print("=" * 65)

    # Save summary table
    df_hits.to_csv(summary_csv, index=False)
    print(f"\nDetailed taxonomy table saved to: {summary_csv}")

    # Generate set of valid sequence IDs (Keep Arthropoda, Non-Arthropod Metazoa, Other Eukaryote, and No Hits)
    # DISQUALIFY confirmed Bacteria, Fungi, Viruses, Plants
    disqualified_ids = set(contam_df["qseqid"])
    
    # Read full clean fasta header list
    all_ids = set()
    with open(clean_fasta, "r") as f:
        for line in f:
            if line.startswith(">"):
                all_ids.add(line.split()[0][1:])

    allowed_ids = all_ids - disqualified_ids
    filter_fasta(clean_fasta, filtered_fasta, allowed_ids)


if __name__ == "__main__":
    main()