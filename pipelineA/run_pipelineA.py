import os
import subprocess
import sys


def run_command(command, description):
    print(f"\n==================================================")
    print(f"[+] Step: {description}")
    print(f"[>] Command: {command}")
    print(f"==================================================")

    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"\n[❌ ERROR] Command failed at step: {description}")
        sys.exit(1)
    else:
        print(f"[✔ SUCCESS] {description} completed successfully.\n")


def main():
    print("🚀 STARTING PIPELINE A: TARGET DISCOVERY & MINING 🚀\n")

    os.makedirs("results", exist_ok=True)
    diamond_exe = (
        ".\\diamond.exe" if os.path.exists("diamond.exe") else ".\\diamond"
    )

    # Step 0: Ensure databases exist (downloads & formats if missing)
    if os.path.exists("download_databases.py"):
        run_command(
            "python download_databases.py",
            "0/6 - Pre-flight Check: Auto-Downloading Reference Databases",
        )

    # Step 1: QC Phase 2 (Generates proteins_clean.fasta)
    run_command("python qc_phase2.py", "1/6 - Running QC Phase 2")

    # AUTO-FIX FOR NEW DATASETS:
    # If proteins_arthropod_only.fasta doesn't exist yet, generate it automatically!
    if not os.path.exists("proteins_arthropod_only.fasta"):
        print(
            "\n[!] 'proteins_arthropod_only.fasta' not found. Bootstrapping screening data..."
        )

        # Step A: Run DIAMOND on raw cleaned proteome to create initial hits
        cmd_init_diamond = (
            f"{diamond_exe} blastp "
            "--query proteins_clean.fasta "
            "--db db/uniprot_sprot "
            "--out results/diamond_sprot_hits.tsv "
            "--outfmt 6 qseqid sseqid pident length evalue bitscore stitle "
            "--evalue 1e-5 "
            "--threads 4"
        )
        run_command(
            cmd_init_diamond,
            "Bootstrap A: Running initial DIAMOND for screening",
        )

        # Step B: Generate proteins_arthropod_only.fasta
        run_command(
            "python screen_contaminants.py",
            "Bootstrap B: Generating proteins_arthropod_only.fasta",
        )

    # Step 2: Main DIAMOND run on proteins_arthropod_only.fasta (Refined Data 2 hits)
    cmd_diamond = (
        f"{diamond_exe} blastp "
        "--query proteins_arthropod_only.fasta "
        "--db db/uniprot_sprot "
        "--out results/diamond_sprot_hits.tsv "
        "--outfmt 6 qseqid sseqid pident length evalue bitscore stitle "
        "--evalue 1e-5 "
        "--max-target-seqs 5 "
        "--threads 4"
    )
    run_command(cmd_diamond, "2/6 - Running DIAMOND BLASTp (Arthropod Only)")

    # Step 3: Screen Contaminants
    run_command("python screen_contaminants.py", "3/6 - Screening Contaminants")

    # Step 4: Mine Targets
    run_command("python phase3_mine_targets.py", "4/6 - Mining Targets")

    # Step 5: Refine Subfamilies
    run_command(
        "python phase3_refine_subfamilies.py", "5/6 - Refining Subfamilies"
    )

    # Step 6: Build Official Top Table directly from unique mined targets
    run_command(
        "python build_official_top10_table.py",
        "6/6 - Building Official Target Table",
    )

    print("\n🎉 ==================================================")
    print("🎉 PIPELINE A COMPLETE! All target discovery steps finished.")
    print("==================================================\n")


if __name__ == "__main__":
    main()