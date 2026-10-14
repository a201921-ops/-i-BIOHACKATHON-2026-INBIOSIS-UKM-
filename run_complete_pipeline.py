import os
import shutil
import subprocess
import sys


def run_command(command, cwd_path):
    """Runs a command inside a specific working directory."""
    print(f"\n==================================================")
    print(f"🚀 Executing in: {os.path.basename(cwd_path)}")
    print(f"👉 Command: {command}")
    print(f"==================================================\n")

    result = subprocess.run(command, cwd=cwd_path, shell=True)

    if result.returncode != 0:
        print(f"\n❌ Pipeline failed during step in '{cwd_path}'. Stopping.")
        sys.exit(1)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pipelineA_dir = os.path.join(base_dir, "pipelineA")
    pipelineB_dir = os.path.join(base_dir, "pipelineB")

    # 1. Run Pipeline A
    print("\n🟢 STARTING PHASE 1: PIPELINE A")
    run_command("python run_pipelineA.py", cwd_path=pipelineA_dir)

    # 2. Bridge Step: Copy candidate table from pipelineA/results/ to pipelineB/
    csv_filename = "official_top10_table_PUBLICATION_READY.csv"

    # Define exact path in pipelineA/results/
    src_csv = os.path.join(pipelineA_dir, "results", csv_filename)
    dest_csv = os.path.join(pipelineB_dir, csv_filename)

    print("\n🌉 BRIDGING DATA: Transferring results from Pipeline A to Pipeline B...")
    print(f"   Source: {src_csv}")
    print(f"   Destination: {dest_csv}")

    if os.path.exists(src_csv):
        shutil.copy(src_csv, dest_csv)
        print(
            f"✔ Successfully bridged '{csv_filename}' into 'pipelineB/' directory!"
        )
    else:
        # Fallback check if the CSV was saved directly in pipelineA/ instead of results/
        fallback_src = os.path.join(pipelineA_dir, csv_filename)
        if os.path.exists(fallback_src):
            shutil.copy(fallback_src, dest_csv)
            print(
                f"✔ Found in pipelineA root and bridged '{csv_filename}' into 'pipelineB/'!"
            )
        else:
            print(
                f"❌ ERROR: Could not find '{csv_filename}' in '{os.path.join(pipelineA_dir, 'results')}'!"
            )
            sys.exit(1)

    # 3. Run Pipeline B
    print("\n🟢 STARTING PHASE 2: PIPELINE B")
    run_command("python run_pipelineB.py", cwd_path=pipelineB_dir)

    print("\n🎉 ==================================================")
    print("✨ COMPLETE PIPELINE EXECUTION FINISHED SUCCESSFULLY!")
    print("==================================================\n")


if __name__ == "__main__":
    main()