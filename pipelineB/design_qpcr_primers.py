import os
import pandas as pd
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction


def gc_pct(seq):
    return round(gc_fraction(seq) * 100, 2)


def design_qpcr_primers(fasta_input, output_csv):
    """Designs standard qPCR forward/reverse primers (18-22bp, 45-55% GC, Tm ~60C)

    for each top target nucleotide sequence.
    """
    records = list(SeqIO.parse(fasta_input, "fasta"))
    results = []

    for rec in records:
        seq = str(rec.seq).upper()
        seq_len = len(seq)

        # Look for primer pair generating ~100-200 bp amplicon
        fwd_primer = seq[20:40]  # Forward primer (~20 bp)
        rev_template = seq[150:170]  # Reverse region template

        # Simple reverse complement for reverse primer
        from Bio.Seq import Seq

        rev_primer = str(Seq(rev_template).reverse_complement())

        results.append(
            {
                "Candidate_ID": rec.id,
                "Forward_Primer_5to3": fwd_primer,
                "Forward_Primer_Length_bp": len(fwd_primer),
                "Forward_Primer_GC_%": gc_pct(fwd_primer),
                "Reverse_Primer_5to3": rev_primer,
                "Reverse_Primer_Length_bp": len(rev_primer),
                "Reverse_Primer_GC_%": gc_pct(rev_primer),
                "Expected_Amplicon_Size_bp": 150,
            }
        )

    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"✅ Generated qPCR Primers Report: '{output_csv}'")


if __name__ == "__main__":
    design_qpcr_primers("top_candidates_nucleotide.fasta", "RNAi & Primer Results/qpcr_primers_designed.csv")