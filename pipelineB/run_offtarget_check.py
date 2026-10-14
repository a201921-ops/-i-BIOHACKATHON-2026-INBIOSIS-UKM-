import os
import subprocess
import sys


def check_offtarget_for_dsrna():
    print("🔎 Running host off-target ecotoxicity check...")

    # Simple relative paths since execution is inside the pipelineB directory
    db_prefix = os.path.join("oil_palm_db", "oil_palm_db")
    query_path = "top_candidates_nucleotide.fasta"
    output_dir = "RNAi & Primer Results"
    output_blast_csv = os.path.join(output_dir, "offtarget_blast_results.csv")

    os.makedirs(output_dir, exist_ok=True)

    # 1. Verify query file exists
    if not os.path.exists(query_path):
        print(f"❌ ERROR: Query file '{query_path}' missing in pipelineB!")
        sys.exit(1)

    # 2. Verify BLAST database index exists
    if not os.path.exists(db_prefix + ".nhr"):
        print(
            f"❌ ERROR: BLAST index file '{db_prefix}.nhr' not found inside oil_palm_db!"
        )
        sys.exit(1)

    print(f"[>] Running BLASTn against database: {db_prefix}")

    # Passing a list with shell=False ensures safe argument handling
    cmd = [
        "blastn",
        "-query",
        query_path,
        "-db",
        db_prefix,
        "-outfmt",
        "6 qseqid sseqid pident length evalue bitscore",
        "-word_size",
        "19",
        "-num_threads",
        "4",
        "-out",
        output_blast_csv,
    ]

    try:
        subprocess.run(cmd, check=True)
        print("✔ Host off-target BLAST check finished successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ BLASTn failed with exit code: {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print(
            "❌ BLASTn command not found on system PATH. Ensure NCBI BLAST+ is installed."
        )
        sys.exit(1)


if __name__ == "__main__":
    check_offtarget_for_dsrna()