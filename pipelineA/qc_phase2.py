#!/usr/bin/env python3
"""
Phase 2 QC Script: Metisa plana Proteome Sanitization & Contamination Screening
i-Biohackathon 2026 - Track 2
"""

import sys
import re
from pathlib import Path
import pandas as pd
import numpy as np


def parse_fasta(fasta_path: Path):
    """
    Fast, memory-efficient FASTA generator.
    Yields tuple of (header_id, full_header, sequence).
    """
    header_id, full_header, seq_chunks = None, None, []
    with open(fasta_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header_id:
                    yield header_id, full_header, "".join(seq_chunks)
                full_header = line[1:]
                header_id = full_header.split()[0]
                seq_chunks = []
            else:
                seq_chunks.append(line)
        if header_id:
            yield header_id, full_header, "".join(seq_chunks)


def clean_and_profile_proteome(
    input_fasta: Path, output_clean_fasta: Path
) -> pd.DataFrame:
    """
    Cleans proteome FASTA by removing trailing stop characters (*),
    and collects per-protein QC metrics.
    """
    print(f"[1/3] Sanitizing and profiling sequence data from: {input_fasta}")

    qc_records = []

    with open(output_clean_fasta, "w") as out_f:
        for seq_id, header, raw_seq in parse_fasta(input_fasta):
            # Track raw traits before modification
            has_terminal_stop = raw_seq.endswith("*")
            internal_stops = raw_seq[:-1].count("*") if has_terminal_stop else raw_seq.count("*")
            x_count = raw_seq.upper().count("X")

            # Clean sequence: strip trailing stop codon for downstream tool compatibility
            clean_seq = raw_seq.rstrip("*")
            seq_len = len(clean_seq)

            # Write cleaned FASTA
            out_f.write(f">{header}\n{clean_seq}\n")

            # Collect record stats
            qc_records.append(
                {
                    "protein_id": seq_id,
                    "gene_id": seq_id.split(".")[0],  # e.g., g25394.t1 -> g25394
                    "length_aa": seq_len,
                    "has_terminal_stop": has_terminal_stop,
                    "is_short_lt_50aa": seq_len < 50,
                    "count_X": x_count,
                    "has_ambiguous_X": x_count > 0,
                    "internal_stops": internal_stops,
                }
            )

    df_qc = pd.DataFrame(qc_records)
    print(f"      Cleaned FASTA written to: {output_clean_fasta}")
    return df_qc


def parse_diamond_tax_results(
    diamond_tsv: Path, df_qc: pd.DataFrame, non_target_taxa=None
) -> pd.DataFrame:
    """
    Parses DIAMOND BLASTp tabular output with taxonomy information to identify
    non-arthropod contaminant candidate models.
    
    Expected DIAMOND outfmt:
    qseqid sseqid pident length evalue stitle staxids sscinames
    """
    if non_target_taxa is None:
        # Default non-arthropod organism groups to flag
        non_target_taxa = ["Bacteria", "Fungi", "Viruses", "Streptophyta", "Microsporidia"]

    if not diamond_tsv.exists():
        print(f"\n[Warning] DIAMOND result file '{diamond_tsv}' not found.")
        print("          Skipping contamination filtering step. Marking contamination_status as 'Unscreened'.")
        df_qc["best_hit_tax"] = "Not Evaluated"
        df_qc["is_contaminant"] = False
        return df_qc

    print(f"\n[2/3] Parsing DIAMOND taxonomy output from: {diamond_tsv}")

    colnames = ["qseqid", "sseqid", "pident", "length", "evalue", "stitle", "staxids", "sscinames"]
    df_hits = pd.read_csv(diamond_tsv, sep="\t", names=colnames, comment="#")

    # Keep top hit per query protein
    df_top = df_hits.drop_duplicates(subset=["qseqid"], keep="first").copy()

    # Determine contamination flag
    pattern = "|".join(non_target_taxa)
    df_top["is_contaminant"] = df_top["sscinames"].str.contains(
        pattern, case=False, na=False
    ) | df_top["stitle"].str.contains(pattern, case=False, na=False)

    # Merge taxonomy stats back to QC DataFrame
    df_merged = df_qc.merge(
        df_top[["qseqid", "sseqid", "pident", "evalue", "sscinames", "is_contaminant"]],
        left_on="protein_id",
        right_on="qseqid",
        how="left",
    )
    df_merged["is_contaminant"] = df_merged["is_contaminant"].fillna(False)
    df_merged.rename(columns={"sscinames": "best_hit_tax"}, inplace=True)

    return df_merged


def generate_qc_summary_report(df_qc: pd.DataFrame, report_csv: Path):
    """
    Prints summary metrics matching the brief expectations and exports the final table.
    """
    print("\n" + "=" * 60)
    print("           METISA PLANA PROTEOME PHASE 2 QC SUMMARY           ")
    print("=" * 60)

    total_genes = len(df_qc)
    mean_len = df_qc["length_aa"].mean()
    median_len = df_qc["length_aa"].median()
    min_len = df_qc["length_aa"].min()
    max_len = df_qc["length_aa"].max()

    no_stop_count = (~df_qc["has_terminal_stop"]).sum()
    short_count = df_qc["is_short_lt_50aa"].sum()
    x_count = df_qc["has_ambiguous_X"].sum()
    contam_count = df_qc["is_contaminant"].sum() if "is_contaminant" in df_qc.columns else 0

    print(f"Total Predicted Proteins/Genes : {total_genes:,}")
    print(f"Sequence Lengths (aa)          : Min={min_len}, Max={max_len:,}, Mean={mean_len:.1f}, Median={median_len:.1f}")
    print(f"Missing Terminal Stop (*)      : {no_stop_count:,} ({no_stop_count/total_genes*100:.2f}%)")
    print(f"Short Sequences (< 50 aa)      : {short_count:,} ({short_count/total_genes*100:.2f}%)")
    print(f"Contains Ambiguous 'X'         : {x_count:,} ({x_count/total_genes*100:.2f}%)")
    print(f"Flagged Non-Arthropod Models   : {contam_count:,} ({contam_count/total_genes*100:.2f}%)")
    print("=" * 60)

    df_qc.to_csv(report_csv, index=False)
    print(f"[3/3] Detailed per-protein QC metrics saved to: {report_csv}\n")


def main():
    # File Paths
    raw_fasta = Path("proteins_longest_isoform.fasta")
    clean_fasta = Path("proteins_clean.fasta")
    diamond_tsv = Path("results/diamond_tax_hits.tsv")
    qc_csv = Path("results/proteome_qc_summary.csv")

    Path("results").mkdir(exist_ok=True)

    if not raw_fasta.exists():
        print(f"[Error] Primary FASTA file '{raw_fasta}' not found in current directory.")
        sys.exit(1)

    # Run Pipeline
    df_qc = clean_and_profile_proteome(raw_fasta, clean_fasta)
    df_qc = parse_diamond_tax_results(diamond_tsv, df_qc)
    generate_qc_summary_report(df_qc, qc_csv)


if __name__ == "__main__":
    main()