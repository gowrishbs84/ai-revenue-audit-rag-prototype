import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="eCash Audit Reconciliation", layout="wide")

st.title("AI Revenue Audit RAG Prototype")
st.subheader("SDS vs CMP eCash Reconciliation with Human-in-the-Loop Validation")

st.write(
    "This prototype compares SDS and CMP eCash data by slot location and gaming date, "
    "detects variances, allows human validation, captures adjustment reasons, "
    "validates CMP adjustments against SDS values, and simulates committing adjustments."
)

sds_file = st.file_uploader("Upload SDS eCash CSV", type=["csv"])
cmp_file = st.file_uploader("Upload CMP eCash CSV", type=["csv"])

required_columns = ["slot_location", "gamingdt", "ecash_in", "ecash_out"]

if sds_file and cmp_file:
    sds_df = pd.read_csv(sds_file)
    cmp_df = pd.read_csv(cmp_file)

    sds_missing = [col for col in required_columns if col not in sds_df.columns]
    cmp_missing = [col for col in required_columns if col not in cmp_df.columns]

    if sds_missing:
        st.error(f"SDS file missing columns: {sds_missing}")
    elif cmp_missing:
        st.error(f"CMP file missing columns: {cmp_missing}")
    else:
        st.subheader("Source Data")

        col_a, col_b = st.columns(2)

        with col_a:
            st.write("SDS eCash Data")
            st.dataframe(sds_df)

        with col_b:
            st.write("CMP eCash Data")
            st.dataframe(cmp_df)

        merged_df = pd.merge(
            sds_df,
            cmp_df,
            on=["slot_location", "gamingdt"],
            how="outer",
            suffixes=("_sds", "_cmp")
        )

        value_columns = [
            "ecash_in_sds",
            "ecash_out_sds",
            "ecash_in_cmp",
            "ecash_out_cmp"
        ]

        merged_df[value_columns] = merged_df[value_columns].fillna(0)

        merged_df["ecash_in_variance"] = (
            merged_df["ecash_in_sds"] - merged_df["ecash_in_cmp"]
        )

        merged_df["ecash_out_variance"] = (
            merged_df["ecash_out_sds"] - merged_df["ecash_out_cmp"]
        )

        merged_df["variance_status"] = merged_df.apply(
            lambda row: "Variance Found"
            if row["ecash_in_variance"] != 0 or row["ecash_out_variance"] != 0
            else "Matched",
            axis=1
        )

        variance_df = merged_df[merged_df["variance_status"] == "Variance Found"]

        st.subheader("Reconciliation Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total eCash In Variance",
            f"${merged_df['ecash_in_variance'].sum():,.2f}"
        )

        col2.metric(
            "Total eCash Out Variance",
            f"${merged_df['ecash_out_variance'].sum():,.2f}"
        )

        col3.metric("Variance Records", len(variance_df))

        st.subheader("Reconciliation Report")
        st.dataframe(merged_df)

        csv_report = merged_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Reconciliation Report",
            data=csv_report,
            file_name="ecash_reconciliation_report.csv",
            mime="text/csv"
        )

        if variance_df.empty:
            st.success("Reconciliation successful. No variance found between SDS and CMP.")

        else:
            st.error("Variance detected. Human validation is required before adjustment.")

            st.subheader("Variance Details")
            st.dataframe(variance_df)

            st.subheader("Human-in-the-Loop Adjustment Review")

            adjusted_df = merged_df.copy()
            adjustment_log = []

            for index, row in variance_df.iterrows():
                st.markdown("---")
                st.markdown(
                    f"### Slot Location: {row['slot_location']} | Gaming Date: {row['gamingdt']}"
                )

                st.write(f"SDS eCash In: ${row['ecash_in_sds']:,.2f}")
                st.write(f"CMP eCash In: ${row['ecash_in_cmp']:,.2f}")
                st.write(f"eCash In Variance: ${row['ecash_in_variance']:,.2f}")

                st.write(f"SDS eCash Out: ${row['ecash_out_sds']:,.2f}")
                st.write(f"CMP eCash Out: ${row['ecash_out_cmp']:,.2f}")
                st.write(f"eCash Out Variance: ${row['ecash_out_variance']:,.2f}")

                validation_status = st.selectbox(
                    f"Human Validation Status for Slot {row['slot_location']}",
                    [
                        "Pending Review",
                        "Approved for CMP Adjustment",
                        "Rejected - Requires Further Investigation"
                    ],
                    key=f"validation_{index}"
                )

                adjustment_reason = st.text_area(
                    f"Adjustment Reason for Slot {row['slot_location']}",
                    placeholder="Example: CMP posting delay identified. SDS value verified as source of truth.",
                    key=f"reason_{index}"
                )

                adjusted_ecash_in_cmp = st.number_input(
                    f"Adjusted CMP eCash In for Slot {row['slot_location']}",
                    value=float(row["ecash_in_cmp"]),
                    key=f"in_{index}"
                )

                adjusted_ecash_out_cmp = st.number_input(
                    f"Adjusted CMP eCash Out for Slot {row['slot_location']}",
                    value=float(row["ecash_out_cmp"]),
                    key=f"out_{index}"
                )

                if validation_status == "Approved for CMP Adjustment":
                    adjusted_df.loc[index, "ecash_in_cmp"] = adjusted_ecash_in_cmp
                    adjusted_df.loc[index, "ecash_out_cmp"] = adjusted_ecash_out_cmp

                    adjustment_log.append({
                        "slot_location": row["slot_location"],
                        "gamingdt": row["gamingdt"],
                        "original_ecash_in_cmp": row["ecash_in_cmp"],
                        "adjusted_ecash_in_cmp": adjusted_ecash_in_cmp,
                        "original_ecash_out_cmp": row["ecash_out_cmp"],
                        "adjusted_ecash_out_cmp": adjusted_ecash_out_cmp,
                        "validation_status": validation_status,
                        "adjustment_reason": adjustment_reason,
                        "committed_by": "Revenue Audit User",
                        "committed_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

            if st.button("Commit Approved Adjustments and Rerun Reconciliation"):

                if not adjustment_log:
                    st.warning(
                        "No approved adjustments found. Please approve at least one variance before committing."
                    )

                else:
                    validation_failed = False

                    for index, row in adjusted_df.iterrows():
                        in_match = row["ecash_in_sds"] == row["ecash_in_cmp"]
                        out_match = row["ecash_out_sds"] == row["ecash_out_cmp"]

                        if not in_match or not out_match:
                            validation_failed = True

                    if validation_failed:
                        st.error(
                            "Adjustment validation failed. Adjusted CMP values must match SDS values before commit."
                        )

                        validation_variance_df = adjusted_df[
                            (adjusted_df["ecash_in_sds"] != adjusted_df["ecash_in_cmp"]) |
                            (adjusted_df["ecash_out_sds"] != adjusted_df["ecash_out_cmp"])
                        ]

                        st.subheader("Remaining Variance Records")
                        st.dataframe(validation_variance_df)

                    else:
                        adjusted_df["ecash_in_variance"] = (
                            adjusted_df["ecash_in_sds"] - adjusted_df["ecash_in_cmp"]
                        )

                        adjusted_df["ecash_out_variance"] = (
                            adjusted_df["ecash_out_sds"] - adjusted_df["ecash_out_cmp"]
                        )

                        adjusted_df["variance_status"] = adjusted_df.apply(
                            lambda row: "Variance Found"
                            if row["ecash_in_variance"] != 0 or row["ecash_out_variance"] != 0
                            else "Matched",
                            axis=1
                        )

                        rerun_variance_df = adjusted_df[
                            adjusted_df["variance_status"] == "Variance Found"
                        ]

                        adjustment_log_df = pd.DataFrame(adjustment_log)

                        st.success("Approved adjustments committed successfully.")

                        st.subheader("Adjustment Audit Log")
                        st.dataframe(adjustment_log_df)

                        log_csv = adjustment_log_df.to_csv(index=False).encode("utf-8")

                        st.download_button(
                            label="Download Adjustment Audit Log",
                            data=log_csv,
                            file_name="cmp_adjustment_audit_log.csv",
                            mime="text/csv"
                        )

                        st.subheader("Reconciliation Result After Committed Adjustments")
                        st.dataframe(adjusted_df)

                        adjusted_csv = adjusted_df.to_csv(index=False).encode("utf-8")

                        st.download_button(
                            label="Download Final Reconciliation Report",
                            data=adjusted_csv,
                            file_name="final_ecash_reconciliation_report.csv",
                            mime="text/csv"
                        )

                        if rerun_variance_df.empty:
                            st.success(
                                "Reconciliation successful after committed CMP adjustments."
                            )
                        else:
                            st.warning(
                                "Variance still exists after adjustment. Further review required."
                            )
                            st.dataframe(rerun_variance_df)

            st.subheader("AI-Style Audit Summary")

            st.write(f"""
            Variance was detected between SDS and CMP eCash values.

            Total eCash In Variance: ${merged_df['ecash_in_variance'].sum():,.2f}  
            Total eCash Out Variance: ${merged_df['ecash_out_variance'].sum():,.2f}  
            Impacted Records: {len(variance_df)}

            Human-in-the-loop validation is required before CMP adjustments are committed.
            The audit user must download the reconciliation report, validate the variance,
            provide an adjustment reason, approve the adjustment, and rerun reconciliation.
            """)

else:
    st.info("Please upload both SDS and CMP eCash CSV files.")