import gzip
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request


def download_file(url, destination):
    print(f"[⬇] Downloading {url} -> {destination}...")
    urllib.request.urlretrieve(url, destination)
    print(f"[✔] Downloaded: {destination}")


def setup_uniprot_sprot():
    """Downloads UniProt Swiss-Prot FASTA into uniprot_sprot.fasta/ folder and builds DIAMOND db."""
    target_dir = "uniprot_sprot.fasta"
    os.makedirs(target_dir, exist_ok=True)

    fasta_path = os.path.join(target_dir, "uniprot_sprot.fasta")
    gz_path = os.path.join(target_dir, "uniprot_sprot.fasta.gz")
    dmnd_path = os.path.join("db", "uniprot_sprot.dmnd")
    os.makedirs("db", exist_ok=True)

    # Step 1: Download & Extract FASTA if missing
    if not os.path.exists(fasta_path):
        if not os.path.exists(gz_path):
            url = "https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz"
            download_file(url, gz_path)

        print("[📦] Decompressing uniprot_sprot.fasta.gz...")
        with gzip.open(gz_path, "rb") as f_in:
            with open(fasta_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"[✔] FASTA extracted to '{fasta_path}'!")

        if os.path.exists(gz_path):
            os.remove(gz_path)
    else:
        print(f"[✔] '{fasta_path}' already exists.")

    # Step 2: Build DIAMOND database (.dmnd) if missing
    if not os.path.exists(dmnd_path):
        diamond_exe = (
            ".\\diamond.exe" if os.path.exists("diamond.exe") else "diamond"
        )
        print(f"[⚙] Building DIAMOND database at '{dmnd_path}'...")
        cmd = f"{diamond_exe} makedb --in {fasta_path} -d {dmnd_path[:-5]}"
        subprocess.run(cmd, shell=True, check=True)
        print("[✔] DIAMOND database indexed successfully!")
    else:
        print(f"[✔] '{dmnd_path}' database already exists.")


def setup_ncbi_taxdump():
    """Downloads NCBI Taxonomy dump and extracts to taxdump/"""
    os.makedirs("taxdump", exist_ok=True)
    tar_path = os.path.join("taxdump", "taxdump.tar.gz")
    names_dmp = os.path.join("taxdump", "names.dmp")

    if not os.path.exists(names_dmp):
        if not os.path.exists(tar_path):
            url = "https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz"
            download_file(url, tar_path)

        print("[📦] Extracting taxdump.tar.gz...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path="taxdump")
        print("[✔] NCBI Taxdump files extracted to 'taxdump/'!")

        if os.path.exists(tar_path):
            os.remove(tar_path)
    else:
        print("[✔] 'taxdump/' directory already contains taxonomy files.")


if __name__ == "__main__":
    print("🚀 Auto-Checking / Downloading Databases for Pipeline A...\n")
    setup_uniprot_sprot()
    print("-" * 50)
    setup_ncbi_taxdump()
    print("\n🎉 ALL DATABASES READY FOR PIPELINE A!")