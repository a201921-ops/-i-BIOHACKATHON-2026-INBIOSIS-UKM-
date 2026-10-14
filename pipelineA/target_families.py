import re
import csv
from Bio import SeqIO

# Define target family domain signatures
TARGET_FAMILIES = {
    "P450": {
        "pfam": "PF00067",
        "interpro": "IPR001128",
        "keywords": [r"\bp450\b", r"cytochrome p450", r"\bcyp\d+"],
        "category": "Detoxification - Phase I"
    },
    "GST": {
        "pfam": "PF02798;PF00043",
        "interpro": "IPR004045;IPR004046",
        "keywords": [r"glutathione s-transferase", r"\bgst\b", r"glutathione transferase"],
        "category": "Detoxification - Phase II"
    },
    "COE_AChE": {
        "pfam": "PF00135",
        "interpro": "IPR002018",
        "keywords": [r"carboxylesterase", r"acetylcholinesterase", r"esterase fe-1", r"cholinesterase"],
        "category": "Detoxification / Neuro-target"
    },
    "Chitin_Synthase": {
        "pfam": "PF01644;PF03142",
        "interpro": "IPR002638",
        "keywords": [r"chitin synthase", r"chitin UDP-N-acetylglucosaminyltransferase"],
        "category": "Growth & Physiology"
    },
    "nAChR": {
        "pfam": "PF02931;PF00029",
        "interpro": "IPR002394",
        "keywords": [r"nicotinic acetylcholine receptor", r"achr", r"ligand-gated ion-channel subunit"],
        "category": "Neuro-target"
    },
    "VGSC": {
        "pfam": "PF00520",
        "interpro": "IPR005821",
        "keywords": [r"sodium channel", r"voltage-gated sodium channel", r"para-like sodium channel"],
        "category": "Neuro-target"
    },
    "GABA": {
        "pfam": "PF02931",
        "interpro": "IPR006029",
        "keywords": [r"gaba", r"gamma-aminobutyric acid receptor", r"rdl"],
        "category": "Neuro-target"
    }
}

print("Target family dictionary loaded successfully!")