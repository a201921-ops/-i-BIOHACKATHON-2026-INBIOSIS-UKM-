import os
import pandas as pd


def load_and_prep(csv_path):
    """Utility function to safely load CSV and strip string whitespace."""
    if not os.path.exists(csv_path):
        print(f"Error: File '{csv_path}' not found.")
        return None
    df = pd.read_csv(csv_path)
    # Convert all object columns to clean strings (strip trailing spaces)
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()
    return df


def build_master_publication_table():
    # 1. File Paths
    target_csv = (
        "results/official_top10_table_PUBLICATION_READY.csv"
        if os.path.exists("results/official_top10_table_PUBLICATION_READY.csv")
        else "official_top10_table_PUBLICATION_READY.csv"
    )
    primers_csv = "RNAi & Primer Results/qpcr_primers_designed.csv"
    offtarget_csv = "results/offtarget_check_results.csv"

    if not os.path.exists(offtarget_csv):
        offtarget_csv = "offtarget_check_results.csv"

    # 2. Load Datasets
    df_targets = load_and_prep(target_csv)
    df_primers = load_and_prep(primers_csv)
    df_offtarget = load_and_prep(offtarget_csv)

    if df_targets is None or df_primers is None:
        print("Stopping: Missing target or primer input CSV files.")
        return

    # 3. Find the primary Gene ID column in the target table
    gene_col_targets = df_targets.columns[0]
    for col in df_targets.columns:
        if any(
            k in col.lower()
            for k in ["gene", "id", "qseqid", "transcript", "candidate"]
        ):
            gene_col_targets = col
            break

    df_targets[gene_col_targets] = df_targets[gene_col_targets].astype(str)
    df_primers["Candidate_ID"] = df_primers["Candidate_ID"].astype(str)

    # 4. Merge Target Data with qPCR Primers
    print(f"Merging target data with qPCR primers on: '{gene_col_targets}'...")
    df_master = pd.merge(
        df_targets,
        df_primers[
            [
                "Candidate_ID",
                "Forward_Primer_5to3",
                "Reverse_Primer_5to3",
            ]
        ],
        left_on=gene_col_targets,
        right_on="Candidate_ID",
        how="left",
    )

    if "Candidate_ID" in df_master.columns and gene_col_targets != "Candidate_ID":
        df_master.drop(columns=["Candidate_ID"], inplace=True)

    # 5. Merge Off-Target Screening Results
    if df_offtarget is not None:
        print("Merging host off-target screening status...")
        offtarget_id_col = "Candidate_ID" if "Candidate_ID" in df_offtarget.columns else df_offtarget.columns[0]
        df_offtarget[offtarget_id_col] = df_offtarget[offtarget_id_col].astype(str)
        
        # Identify incoming status column
        status_col = (
            "offtarget_check" 
            if "offtarget_check" in df_offtarget.columns 
            else ("offtarget_status" if "offtarget_status" in df_offtarget.columns else df_offtarget.columns[-1])
        )

        df_master = pd.merge(
            df_master,
            df_offtarget[[offtarget_id_col, status_col]],
            left_on=gene_col_targets,
            right_on=offtarget_id_col,
            how="left",
        )
        if offtarget_id_col in df_master.columns and gene_col_targets != offtarget_id_col:
            df_master.drop(columns=[offtarget_id_col], inplace=True)

    # 6. Explicitly Rename Columns to 'offtarget_check'
    rename_dict = {
        "Forward_Primer_5to3": "Forward_Primer",
        "Reverse_Primer_5to3": "Reverse_Primer",
        "offtarget_status": "offtarget_check",
    }
    df_master.rename(columns=rename_dict, inplace=True)

    # 7. Drop ONLY unhelpful/clutter columns (keeping 'offtarget_check')
    unwanted_columns = [
        "dsRNA_Construct_Length_bp",
        "dsRNA_Construct_Length",
        "dsRNA_GC_Content_%",
        "dsRNA_GC_Content",
        "Top_21bp_siRNA_Candidates",
        "Top_21bp_siRNA",
        "Expected_Amplicon_Size_bp",
        "Expected_Amplicon_Size",
        "expression_evidence_comment",
        "expression_support",
        "offtarget_check_details",
    ]
    df_master.drop(
        columns=[col for col in unwanted_columns if col in df_master.columns],
        inplace=True,
    )

    # 8. Save Final Master CSV Output
    output_csv = "FINAL_MASTER_PUBLICATION_TABLE.csv"
    df_master.to_csv(output_csv, index=False)

    print("\n" + "=" * 60)
    print(f"🎉 SUCCESS! Table created with 'offtarget_check' column: '{output_csv}'")
    print(
        f"Total target candidates compiled: {len(df_master)} rows x {len(df_master.columns)} columns."
    )
    print("=" * 60)


if __name__ == "__main__":
    build_master_publication_table()