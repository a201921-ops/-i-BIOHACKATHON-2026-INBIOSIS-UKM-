import csv
import os

def refine_subfamilies(input_csv, output_csv):
    if not os.path.exists(input_csv):
        print(f"[❌ ERROR] Input file '{input_csv}' does not exist!")
        return

    refined_rows = []

    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))

    for row in reader:
        # Safely look for 'gene_family' or 'target_family' without raising KeyError
        fam = row.get("gene_family") or row.get("target_family") or "Other"
        stitle = row.get("stitle", "").lower()
        acc = row.get("best_hit_accession", "").lower()

        subfamily = "Unclassified"

        # Refine specific subfamilies/clades based on accession/stitle keywords
        if fam == "nAChR":
            if "alpha" in stitle or "ach1" in acc or "ach2" in acc:
                subfamily = "nAChR Alpha Subunit"
            elif "beta" in stitle or "ach3" in acc:
                subfamily = "nAChR Beta Subunit"
            else:
                subfamily = "nAChR (Unclassified)"
        elif fam == "VGSC":
            subfamily = "Voltage-Gated Sodium Channel"
        elif fam == "Chitin_Synthase":
            if "chs1" in acc or "chs-a" in stitle:
                subfamily = "Chs-A (Epidermal/Gut)"
            elif "chs2" in acc or "chs-b" in stitle:
                subfamily = "Chs-B (Peritrophic Membrane)"
            else:
                subfamily = "Chitin Synthase (Unclassified)"
        elif fam == "COE_AChE":
            if "ace1" in acc or "aces" in acc:
                subfamily = "AChE (Acetylcholinesterase)"
            else:
                subfamily = "Carboxylesterase / Esterase"
        elif fam == "P450":
            if "cp6" in acc or "cyp6" in stitle:
                subfamily = "CYP6 Clade (Metabolic Resistance)"
            elif "cp4" in acc or "cyp4" in stitle:
                subfamily = "CYP4 Clade"
            else:
                subfamily = "P450 (Unclassified)"
        elif fam == "GABA":
            subfamily = "GABA (RDL/Chloride Channel)"
        else:
            subfamily = f"{fam} Family"

        # Standardize keys in row
        row["gene_family"] = fam
        row["subfamily_or_clade"] = subfamily
        refined_rows.append(row)

    if refined_rows:
        fieldnames = list(refined_rows[0].keys())
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(refined_rows)
        print(f"[✔ SUCCESS] Refined subfamilies for {len(refined_rows)} candidates into '{output_csv}'")

if __name__ == "__main__":
    refine_subfamilies("results/phase3_mined_targets.csv", "results/phase3_refined_candidates.csv")