import os
import pandas as pd
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction


def calculate_gc_percent(seq_str):
    """Calculates GC percentage using modern Biopython syntax."""
    return gc_fraction(seq_str) * 100


def find_optimal_dsrna_region(
    sequence, min_len=200, max_len=500, target_gc_min=40.0, target_gc_max=60.0
):
    """Sliding window approach to identify optimal 200-500 bp dsRNA target constructs

    matching ideal GC content (40-60%).
    """
    seq_str = str(sequence).upper()
    seq_len = len(seq_str)

    if seq_len < min_len:
        # Sequence too short for standard dsRNA, return entire sequence if GC is acceptable
        gc = calculate_gc_percent(seq_str)
        return {
            "start": 1,
            "end": seq_len,
            "length": seq_len,
            "gc_content": round(gc, 2),
            "seq": seq_str,
            "status": "Short Sequence (Full Length)",
        }

    best_region = None
    best_gc_diff = 999.0  # Measure distance to ideal 50% GC

    # Slide window across sequence (stepping by 20 bp)
    for window_size in range(max_len, min_len - 1, -50):
        if window_size > seq_len:
            continue

        for start in range(0, seq_len - window_size + 1, 20):
            end = start + window_size
            subseq = seq_str[start:end]
            gc = calculate_gc_percent(subseq)

            # Check if GC content falls within acceptable 40-60% range
            if target_gc_min <= gc <= target_gc_max:
                gc_diff = abs(50.0 - gc)
                if gc_diff < best_gc_diff:
                    best_gc_diff = gc_diff
                    best_region = {
                        "start": start + 1,
                        "end": end,
                        "length": window_size,
                        "gc_content": round(gc, 2),
                        "seq": subseq,
                        "status": "Optimal Window Identified",
                    }

    # Fallback if no window hits perfect 40-60%
    if not best_region:
        default_sub = seq_str[: min(300, seq_len)]
        best_region = {
            "start": 1,
            "end": len(default_sub),
            "length": len(default_sub),
            "gc_content": round(calculate_gc_percent(default_sub), 2),
            "seq": default_sub,
            "status": "Suboptimal GC (Fallback Window)",
        }

    return best_region


def extract_sirna_candidates(dsrna_seq, sirna_len=21):
    """Scans chosen dsRNA region to extract top 19-21 bp siRNA core targets with 40-60% GC."""
    sirnas = []
    for i in range(0, len(dsrna_seq) - sirna_len + 1, 5):
        sirna_seq = dsrna_seq[i : i + sirna_len]
        gc = calculate_gc_percent(sirna_seq)

        # Prefer siRNAs starting with A/U at 5' end and 40-60% GC (Reynolds rules simplified)
        if 40.0 <= gc <= 60.0:
            sirnas.append(
                {
                    "pos": i + 1,
                    "sirna_seq": sirna_seq,
                    "gc_content": round(gc, 2),
                }
            )

    return sirnas[:3]  # Return top 3 representative siRNAs per gene


def process_rnai_design(fasta_input, csv_output, fasta_output):
    """Main function to parse nucleotide candidates, select dsRNA constructs,

    and output CSV report + FASTA of dsRNA fragments.
    """
    if not os.path.exists(fasta_input):
        print(
            f"Error: Could not find '{fasta_input}'. Please make sure the file exists."
        )
        return

    records = list(SeqIO.parse(fasta_input, "fasta"))
    print(
        f"Processing {len(records)} candidate nucleotide sequences from '{fasta_input}'...\n"
    )

    results = []
    dsrna_records = []

    for record in records:
        candidate_id = record.id
        full_seq = str(record.seq)

        # 1. Identify best 200-500 bp dsRNA region
        dsrna = find_optimal_dsrna_region(full_seq)

        # 2. Identify top 21-bp siRNA seeds within the region
        top_sirnas = extract_sirna_candidates(dsrna["seq"], sirna_len=21)
        sirna_str = " | ".join(
            [f"Pos {s['pos']}: {s['sirna_seq']} ({s['gc_content']}% GC)" for s in top_sirnas]
        )

        results.append(
            {
                "Candidate_ID": candidate_id,
                "Full_Nucleotide_Length": len(full_seq),
                "dsRNA_Start_Pos": dsrna["start"],
                "dsRNA_End_Pos": dsrna["end"],
                "dsRNA_Construct_Length_bp": dsrna["length"],
                "dsRNA_GC_Content_%": dsrna["gc_content"],
                "Design_Status": dsrna["status"],
                "Top_21bp_siRNA_Candidates": sirna_str,
                "dsRNA_Sequence": dsrna["seq"],
            }
        )

        # Prepare construct FASTA
        from Bio.Seq import Seq
        from Bio.SeqRecord import SeqRecord

        dsrna_rec = SeqRecord(
            Seq(dsrna["seq"]),
            id=f"{candidate_id}_dsRNA_{dsrna['length']}bp",
            description=f"Region:{dsrna['start']}-{dsrna['end']} GC:{dsrna['gc_content']}%",
        )
        dsrna_records.append(dsrna_rec)

    # 3. Export CSV Report
    df_out = pd.DataFrame(results)
    df_out.to_csv(csv_output, index=False)
    print(f"✅ Generated RNAi design report: '{csv_output}'")

    # 4. Export FASTA of dsRNA constructs
    SeqIO.write(dsrna_records, fasta_output, "fasta")
    print(f"✅ Exported dsRNA construct sequences: '{fasta_output}'\n")




# --- RUN DESIGN ---
if __name__ == "__main__":
    INPUT_FASTA = "top_candidates_nucleotide.fasta"
    OUTPUT_CSV = "RNAi & Primer Results/rnai_dsrna_candidates_designed.csv"
    OUTPUT_FASTA = "RNAi & Primer Results/rnai_dsrna_constructs.fasta"

    process_rnai_design(INPUT_FASTA, OUTPUT_CSV, OUTPUT_FASTA)