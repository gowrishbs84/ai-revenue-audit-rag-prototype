import os
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="eCash Audit Reconciliation", layout="wide")

st.title("AI Revenue Audit RAG Prototype")
st.subheader("SDS vs CMP eCash Reconciliation with Tool Calling + SOP RAG")

required_columns = ["slot_location", "gamingdt", "ecash_in", "ecash_out"]


def load_sop():
    with open("knowledge_base/ecash_audit_sop.txt", "r", encoding="utf-8") as file:
        return file.read()


def reconcile_ecash(sds_df, cmp_df):
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

    return merged_df


def generate_ai_recommendation(reconciliation_df, sop_text):
    variance_df = reconciliation_df[
        reconciliation_df["variance_status"] == "Variance Found"
    ]

    if variance_df.empty:
        return "No variance found. No AI recommendation required."

    variance_context = variance_df.to_string(index=False)

    prompt = f"""
You are an AI revenue audit assistant.

Use the SOP guidance and reconciliation tool output below to generate an audit recommendation.

Important rules:
- Do not recalculate financial values.
- Use only the reconciliation tool output.
- Follow the SOP guidance.
- Recommend human validation before adjustment.
- Keep the response concise and audit-friendly.

SOP Guidance:
{sop_text}

Reconciliation Tool Output:
{variance_context}

Generate:
1. Summary of variance
2. Risk level
3. Recommended audit action
4. Human approval requirement
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


st.write(
    "This prototype compares SDS and CMP eCash data, detects variances using a deterministic "
    "Python reconciliation tool, retrieves SOP guidance, and uses OpenAI to generate an audit recommendation."
)

sds_file = st.file_uploader("Upload SDS eCash CSV", type=["csv"])
cmp_file = st.file_uploader("Upload CMP eCash CSV", type=["csv"])

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
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("SDS eCash Data")
            st.dataframe(sds_df)

        with col_b:
            st.subheader("CMP eCash Data")
            st.dataframe(cmp_df)

        merged_df = reconcile_ecash(sds_df, cmp_df)

        variance_df = merged_df[
            merged_df["variance_status"] == "Variance Found"
        ]

        st.subheader("Reconciliation Summary")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total eCash In Variance", f"${merged_df['ecash_in_variance'].sum():,.2f}")
        col2.metric("Total eCash Out Variance", f"${merged_df['ecash_out_variance'].sum():,.2f}")
        col3.metric("Variance Records", len(variance_df))

        st.subheader("Reconciliation Report")
        st.dataframe(merged_df)

        st.download_button(
            label="Download Reconciliation Report",
            data=merged_df.to_csv(index=False).encode("utf-8"),
            file_name="ecash_reconciliation_report.csv",
            mime="text/csv"
        )

        if variance_df.empty:
            st.success("Reconciliation successful. No variance found between SDS and CMP.")
        else:
            st.error("Variance detected. Human validation is required before adjustment.")

            st.subheader("Variance Details")
            st.dataframe(variance_df)

            st.subheader("AI Audit Recommendation using SOP RAG")

            if st.button("Generate AI Audit Recommendation"):
                try:
                    sop_text = load_sop()
                    ai_response = generate_ai_recommendation(merged_df, sop_text)
                    st.write(ai_response)
                except Exception as e:
                    st.error(f"AI recommendation failed: {e}")

            st.subheader("Human-in-the-Loop Adjustment Review")

            adjusted_df = merged_df.copy()
            adjustment_log = []

            for index, row in variance_df.iterrows():
                st.markdown("---")
                st.markdown(f"### Slot Location: {row['slot_location']} | Gaming Date: {row['gamingdt']}")

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
                    st.warning("No approved adjustments found. Please approve at least one variance before committing.")
                else:
                    validation_variance_df = adjusted_df[
                        (adjusted_df["ecash_in_sds"] != adjusted_df["ecash_in_cmp"]) |
                        (adjusted_df["ecash_out_sds"] != adjusted_df["ecash_out_cmp"])
                    ]

                    if not validation_variance_df.empty:
                        st.error("Adjustment validation failed. Adjusted CMP values must match SDS values before commit.")
                        st.subheader("Remaining Variance Records")
                        st.dataframe(validation_variance_df)
                    else:
                        adjusted_df = reconcile_ecash(
                            adjusted_df[["slot_location", "gamingdt", "ecash_in_sds", "ecash_out_sds"]]
                            .rename(columns={"ecash_in_sds": "ecash_in", "ecash_out_sds": "ecash_out"}),
                            adjusted_df[["slot_location", "gamingdt", "ecash_in_cmp", "ecash_out_cmp"]]
                            .rename(columns={"ecash_in_cmp": "ecash_in", "ecash_out_cmp": "ecash_out"})
                        )

                        adjustment_log_df = pd.DataFrame(adjustment_log)

                        st.success("Approved adjustments committed successfully.")

                        st.subheader("Adjustment Audit Log")
                        st.dataframe(adjustment_log_df)

                        st.download_button(
                            label="Download Adjustment Audit Log",
                            data=adjustment_log_df.to_csv(index=False).encode("utf-8"),
                            file_name="cmp_adjustment_audit_log.csv",
                            mime="text/csv"
                        )

                        st.subheader("Final Reconciliation Report")
                        st.dataframe(adjusted_df)

                        st.download_button(
                            label="Download Final Reconciliation Report",
                            data=adjusted_df.to_csv(index=False).encode("utf-8"),
                            file_name="final_ecash_reconciliation_report.csv",
                            mime="text/csv"
                        )

                        st.success("Reconciliation successful after committed CMP adjustments.")
else:
    st.info("Please upload both SDS and CMP eCash CSV files.")