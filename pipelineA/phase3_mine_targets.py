import csv
import os
import re

# Strict functional keyword definitions
KEYWORDS = {
    # Neuroreceptors
    'COE_AChE': [r'\bacetylcholinesterase\b', r'\bache\b', r'\baces\b', r'\bcarboxylesterase\b', r'\best6\b'],
    'nAChR': [r'\bnicotinic acetylcholine\b', r'\bnachr\b', r'acetylcholine receptor subunit'],
    'GABA': [r'\bgaba receptor\b', r'\brdl\b', r'gamma-aminobutyric acid receptor', r'gaba-gated'],
    'VGSC': [r'\bvoltage-gated sodium channel\b', r'\bsodium channel protein\b', r'\bpara-like\b', r'\bscna\b', r'\bnach\b'],
    'RyR': [r'\bryanodine receptor\b', r'\bryr\b'],
    'GluCl': [r'\bglutamate-gated chloride\b', r'\bglucl\b'],
    'Octopamine': [r'\boctopamine receptor\b', r'\boctor\b', r'\boct-alpha\b', r'\boct-beta\b'],
    
    # Metabolic & Detoxification
    'P450': [r'\bcytochrome p450\b', r'\bcyp6\b', r'\bcyp4\b', r'\bcyp9\b', r'\bcp6b\b'],
    'GST': [r'\bglutathione s-transferase\b', r'\bgstd\b', r'\bgste\b', r'\bgstt\b', r'\bgst1\b', r'\bgst2\b'],
    'ABC_Transporter': [r'\babc transporter\b', r'\batp-binding cassette\b', r'\babcc\b', r'\babcg\b'],
    
    # Growth, Cuticle & Energy
    'Chitin_Synthase': [r'\bchitin synthase\b', r'\bchs1\b', r'\bchs2\b', r'\bchs-a\b', r'\bchs-b\b'],
    'V_ATPase': [r'\bv-type proton atpase\b', r'\bv-atpase\b', r'vacuolar atpase'],
    'Trehalase': [r'\btrehalase\b', r'\btreh\b'],
    'Ecdysone': [r'\becdysone receptor\b', r'\becr\b']
}

# Non-arthropod models to exclude strictly
EXCLUDE_SPECIES = [
    '_HUMAN', '_MOUSE', '_RAT', '_RABIT', '_BOVIN', '_MACMU', '_PIG',
    '_BACSU', '_ECOLI', '_YEAST', '_ARATH', '_PONAB', '_XENLA', '_BUNFA', 
    '_BUNMU', '_NAJNA', '_DANRE', '_CHICK'
]

EXCLUDE_TERMS = ['dehydratase', 'dehydration', 'ribosomal', 'synthetase', 'sulfotransferase']

def classify_target(stitle, accession):
    acc_upper = accession.upper()
    text_lower = f"{stitle} {accession}".lower()

    # Discard non-arthropods
    if any(sp in acc_upper for sp in EXCLUDE_SPECIES):
        return "Other"

    # Discard false-positive terms
    if any(term in text_lower for term in EXCLUDE_TERMS):
        return "Other"

    for family, patterns in KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return family

    return "Other"

def mine_targets(tsv_file="results/diamond_sprot_hits.tsv", output_csv="results/phase3_mined_targets.csv"):
    if not os.path.exists(tsv_file):
        print(f"[❌ ERROR] '{tsv_file}' missing!")
        return

    mined_rows = []
    seen_genes = set()

    with open(tsv_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 7:
                continue

            qseqid = parts[0]
            sseqid = parts[1]
            pident = parts[2]
            length = parts[3]
            evalue = parts[4]
            bitscore = parts[5]
            stitle = parts[6]

            gene_id = qseqid.split('.')[0] if '.' in qseqid else qseqid
            family = classify_target(stitle, sseqid)

            if family != "Other" and gene_id not in seen_genes:
                mined_rows.append({
                    'gene_id': gene_id,
                    'protein_id': qseqid,
                    'gene_family': family,
                    'best_hit_accession': sseqid,
                    'evalue': evalue,
                    'identity_pct': pident,
                    'stitle': stitle
                })
                seen_genes.add(gene_id)

    if mined_rows:
        fieldnames = list(mined_rows[0].keys())
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(mined_rows)
        print(f"[✔ SUCCESS] Mined {len(mined_rows)} clean target candidates into '{output_csv}'")

if __name__ == "__main__":
    mine_targets()