import gzip
import os
import shutil
import subprocess
import sys
import urllib.request


def setup_oil_palm_db():
    db_dir = "oil_palm_db"
    os.makedirs(db_dir, exist_ok=True)

    fasta_path = os.path.abspath(os.path.join(db_dir, "oil_palm_transcripts.fasta"))
    gz_path = os.path.abspath(os.path.join(db_dir, "oil_palm_transcripts.fasta.gz"))
    db_prefix = os.path.abspath(os.path.join(db_dir, "oil_palm_db"))

    ncbi_url = "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/442/705/GCF_000442705.2_EG11/GCF_000442705.2_EG11_rna.fna.gz"

    # 1. Download FASTA if missing
    if not os.path.exists(fasta_path):
        print("[⬇] Downloading NCBI RefSeq Oil Palm transcriptome...")
        try:
            req = urllib.request.Request(
                ncbi_url,
                headers={"User-Agent": "Mozilla/5.0 (Bioinformatics-Pipeline)"},
            )

            with urllib.request.urlopen(req) as response, open(gz_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)

            print("[⚙] Extracting FASTA file...")
            with gzip.open(gz_path, "rb") as f_in, open(fasta_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

            if os.path.exists(gz_path):
                os.remove(gz_path)

            print(f"[✔] FASTA ready: '{fasta_path}'")
        except Exception as e:
            print(f"[❌ ERROR] Download failed: {e}")
            sys.exit(1)

    # 2. Build BLAST Index using list-format subprocess.run (safely handles spaces in paths)
    nhr_file = db_prefix + ".nhr"
    if not os.path.exists(nhr_file):
        print(f"[⚙] Indexing BLAST database at '{db_prefix}'...")
        cmd = [
            "makeblastdb",
            "-in", fasta_path,
            "-dbtype", "nucl",
            "-out", db_prefix
        ]
        result = subprocess.run(cmd)
        if result.returncode == 0:
            print("[✔] BLAST database built successfully!")
        else:
            print("[❌ ERROR] makeblastdb failed.")
            sys.exit(1)
    else:
        print("[✔] BLAST database index is ready.")


if __name__ == "__main__":
    setup_oil_palm_db()