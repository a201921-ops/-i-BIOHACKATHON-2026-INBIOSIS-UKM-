import os
import subprocess
import sys

# Steps located strictly inside the pipelineB directory
PIPELINE_STEPS = [
    "download_oil_palm_db.py",  # Step 0: Ensure host database exists
    "extract_candidate_nucleotides.py",  # Step 1: Extract candidate sequences
    "design_rnai_constructs.py",  # Step 2: Slice dsRNA windows
    "run_offtarget_check.py",  # Step 3: BLASTn against Oil Palm
    "design_qpcr_primers.py",  # Step 4: Pick qPCR primers
    "build_final_master_table.py",  # Step 5: Generate output CSV
]


def run_pipelineB():
    print("🚀 Running Standalone Pipeline B Test...\n")

    # Ensure required output directories exist
    os.makedirs("RNAi & Primer Results", exist_ok=True)
    os.makedirs("oil_palm_db", exist_ok=True)

    for step in PIPELINE_STEPS:
        print(f"▶️ RUNNING: {step}")
        result = subprocess.run([sys.executable, step])
        if result.returncode != 0:
            print(f"❌ Standalone test stopped: '{step}' failed.")
            sys.exit(1)
        print(f"✅ COMPLETED: {step}\n")

    print(
        "🎉 PIPELINE B TEST PASSED! All standalone steps executed successfully."
    )


if __name__ == "__main__":
    run_pipelineB()